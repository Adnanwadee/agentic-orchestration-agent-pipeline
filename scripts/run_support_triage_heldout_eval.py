from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.support_triage_classifier import (
    CLASSIFIER_REPAIR_INSTRUCTION_SHA256,
    CLASSIFIER_REPAIR_INSTRUCTION_VERSION,
    CLASSIFIER_PROMPT_SHA256,
    CLASSIFIER_PROMPT_VERSION,
    CONFIDENCE_THRESHOLD,
    MODEL_ID,
    ClassifierExecutionResult,
    ModelCallResult,
    TicketIntake,
    classify_with_bounded_attempts,
    local_env_classifier,
)
from tools.support_triage_drafter import (
    DRAFT_PROMPT_SHA256,
    DRAFT_PROMPT_VERSION,
    DraftModelCallResult,
    DraftRequest,
    draft_auto_route_response,
    local_env_drafter,
)


SEED_PATH = ROOT / "data" / "support_tickets_seed.json"
GROUND_TRUTH_PATH = ROOT / "data" / "support_tickets_ground_truth.json"
SPLIT_PATH = ROOT / "data" / "support_tickets_split.json"
FREEZE_MANIFEST_PATH = ROOT / "data" / "support_tickets_freeze_manifest.json"
DEFAULT_OUTPUT_ROOT = ROOT / "artifacts" / "evaluations" / "support_triage" / "held_out_final"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_frozen_hashes(include_ground_truth: bool = True) -> dict[str, str]:
    manifest = load_json(FREEZE_MANIFEST_PATH)
    expected = manifest["sha256"]
    actual = {
        "support_tickets_seed": sha256_file(SEED_PATH),
        "support_tickets_split": sha256_file(SPLIT_PATH),
    }
    if include_ground_truth:
        actual["support_tickets_ground_truth"] = sha256_file(GROUND_TRUTH_PATH)
    expected_subset = {key: expected[key] for key in actual}
    if actual != expected_subset:
        raise SystemExit(
            "HELD_OUT_FREEZE_HASH_MISMATCH "
            + json.dumps({"expected": expected_subset, "actual": actual}, sort_keys=True)
        )
    return actual


def load_held_out_inference_records() -> tuple[list[dict[str, str]], dict[str, Any], dict[str, str]]:
    hashes = verify_frozen_hashes(include_ground_truth=False)
    seed = {ticket["id"]: ticket for ticket in load_json(SEED_PATH)}
    split = load_json(SPLIT_PATH)
    manifest = load_json(FREEZE_MANIFEST_PATH)
    held_out_ids = split["held_out_ids"]
    if held_out_ids != manifest["held_out_ids"]:
        raise SystemExit("HELD_OUT_SPLIT_MANIFEST_MISMATCH")
    if set(held_out_ids).intersection(split["development_ids"]):
        raise SystemExit("DEV_HELD_OUT_OVERLAP_DETECTED")
    records = [
        {"ticket_id": ticket_id, "ticket_text": seed[ticket_id]["text"]}
        for ticket_id in held_out_ids
    ]
    return records, manifest, hashes


def load_ground_truth_records() -> dict[str, dict[str, Any]]:
    verify_frozen_hashes(include_ground_truth=True)
    return {record["ticket_id"]: record for record in load_json(GROUND_TRUTH_PATH)}


def run_inference_phase(
    *,
    classifier_call: Callable[[TicketIntake, int], ModelCallResult],
    drafter_call: Callable[[DraftRequest, int], DraftModelCallResult],
) -> dict[str, Any]:
    records, manifest, inference_hashes = load_held_out_inference_records()
    outputs = []
    for record in records:
        ticket = TicketIntake(
            ticket_id=record["ticket_id"],
            ticket_text=record["ticket_text"],
        )
        classifier_execution = classify_with_bounded_attempts(ticket, classifier_call)
        output = _finalize_ticket(ticket, classifier_execution, drafter_call)
        outputs.append(output.model_dump())
        if classifier_execution.validation_status == "execution_error":
            return _incomplete_output(
                manifest=manifest,
                inference_hashes=inference_hashes,
                outputs=outputs,
                error_code="HELD_OUT_CLASSIFIER_EXECUTION_ERROR",
                failed_ticket_id=ticket.ticket_id,
            )

    return {
        "run_started_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "model_id": MODEL_ID,
        "classifier_prompt_version": CLASSIFIER_PROMPT_VERSION,
        "classifier_prompt_sha256": CLASSIFIER_PROMPT_SHA256,
        "classifier_repair_instruction_version": CLASSIFIER_REPAIR_INSTRUCTION_VERSION,
        "classifier_repair_instruction_sha256": CLASSIFIER_REPAIR_INSTRUCTION_SHA256,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "drafter_prompt_version": DRAFT_PROMPT_VERSION,
        "drafter_prompt_sha256": DRAFT_PROMPT_SHA256,
        "freeze_version": manifest["freeze_version"],
        "frozen_inference_hashes": inference_hashes,
        "held_out_ids": [record["ticket_id"] for record in records],
        "results": outputs,
        "executed_ticket_count": len(outputs),
        "scored": False,
        "final_status": "HELD_OUT_INFERENCE_COMPLETE",
    }


def _finalize_ticket(ticket: TicketIntake, classifier_execution: ClassifierExecutionResult, drafter_call):
    from tools.support_triage_classifier import build_structured_output

    output = build_structured_output(ticket, classifier_execution)
    final_output, _ = draft_auto_route_response(output, drafter_call)
    return final_output


def _incomplete_output(
    *,
    manifest: dict[str, Any],
    inference_hashes: dict[str, str],
    outputs: list[dict[str, Any]],
    error_code: str,
    failed_ticket_id: str,
) -> dict[str, Any]:
    return {
        "run_started_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "model_id": MODEL_ID,
        "classifier_prompt_version": CLASSIFIER_PROMPT_VERSION,
        "classifier_prompt_sha256": CLASSIFIER_PROMPT_SHA256,
        "drafter_prompt_version": DRAFT_PROMPT_VERSION,
        "drafter_prompt_sha256": DRAFT_PROMPT_SHA256,
        "freeze_version": manifest["freeze_version"],
        "frozen_inference_hashes": inference_hashes,
        "results": outputs,
        "executed_ticket_count": len(outputs),
        "scored": False,
        "error_code": error_code,
        "failed_ticket_id": failed_ticket_id,
        "final_status": "HELD_OUT_EVALUATION_INCOMPLETE",
    }


def score_outputs(inference_output: dict[str, Any]) -> dict[str, Any]:
    ground_truth = load_ground_truth_records()
    results = inference_output["results"]
    category_correct = 0
    urgency_correct = 0
    urgency_denominator = 0
    for result in results:
        expected = ground_truth[result["ticket_id"]]
        classification = result.get("classification") or {}
        if classification.get("category") == expected["expected_category"]:
            category_correct += 1
        if expected["expected_urgency"] is not None:
            urgency_denominator += 1
            if classification.get("urgency") == expected["expected_urgency"]:
                urgency_correct += 1
    return {
        "category_correct": category_correct,
        "category_denominator": len(results),
        "urgency_correct": urgency_correct,
        "urgency_denominator": urgency_denominator,
        "structured_output_count": len(results),
        "human_review_count": sum(1 for result in results if result["review_required"]),
        "auto_routed_count": sum(1 for result in results if result["status"] == "auto_routed"),
        "draft_failed_count": sum(1 for result in results if result["status"] == "draft_failed"),
    }


def execute_real_held_out_evaluation(output_root: Path = DEFAULT_OUTPUT_ROOT) -> Path:
    try:
        classifier_call = local_env_classifier()
        drafter_call = local_env_drafter()
    except Exception as exc:
        raise SystemExit(
            "HELD_OUT_INITIALIZATION_ERROR "
            + json.dumps(
                {
                    "scored": False,
                    "executed_ticket_count": 0,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                },
                sort_keys=True,
            )
        ) from exc

    inference_output = run_inference_phase(
        classifier_call=classifier_call,
        drafter_call=drafter_call,
    )
    if inference_output["final_status"] != "HELD_OUT_INFERENCE_COMPLETE":
        raise SystemExit(
            "HELD_OUT_EVALUATION_INCOMPLETE " + json.dumps(inference_output, sort_keys=True)
        )
    inference_output["frozen_hashes"] = verify_frozen_hashes(include_ground_truth=True)
    inference_output["metrics"] = score_outputs(inference_output)
    inference_output["scored"] = True
    run_dir = output_root / inference_output["run_started_utc"].replace(":", "").replace("-", "")
    run_dir.mkdir(parents=True, exist_ok=False)
    output_path = run_dir / "heldout_results.json"
    output_path.write_text(json.dumps(inference_output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def run_mocked_heldout_preflight() -> dict[str, Any]:
    calls = {"classifier": [], "drafter": []}

    def classifier_call(ticket: TicketIntake, attempt: int) -> ModelCallResult:
        calls["classifier"].append(ticket.ticket_id)
        return ModelCallResult(
            raw_text=json.dumps(
                {
                    "category": "general",
                    "secondary_category": None,
                    "urgency": "low",
                    "confidence": 0.90,
                    "reasoning": "mocked held-out preflight classification",
                }
            ),
            latency_seconds=0.01,
            token_usage={"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        )

    def drafter_call(request: DraftRequest, attempt: int) -> DraftModelCallResult:
        calls["drafter"].append(request.ticket_id)
        return DraftModelCallResult(
            raw_text=json.dumps({"problem_summary": "the reported support request"}),
            latency_seconds=0.01,
            token_usage={"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        )

    inference_output = run_inference_phase(classifier_call=classifier_call, drafter_call=drafter_call)
    held_out_ids = inference_output["held_out_ids"]
    produced_ids = [result["ticket_id"] for result in inference_output["results"]]
    unique_ids = sorted(set(produced_ids))
    metrics = score_outputs(inference_output)
    return {
        "mode": "mocked_heldout_preflight",
        "MOCKED_HELDOUT_PREFLIGHT": "PASS",
        "HELD_OUT_ID_COUNT": len(held_out_ids),
        "EXECUTED_RECORD_COUNT": len(produced_ids),
        "UNIQUE_RECORD_COUNT": len(unique_ids),
        "DROPPED_RECORDS": len(set(held_out_ids) - set(produced_ids)),
        "DUPLICATE_RECORDS": len(produced_ids) - len(set(produced_ids)),
        "held_out_ids": held_out_ids,
        "produced_ids": produced_ids,
        "classifier_calls": calls["classifier"],
        "drafter_calls": calls["drafter"],
        "scorer_plumbing": {
            "ground_truth_loaded_after_inference": True,
            "mocked_metrics_not_model_evidence": True,
            "metrics": metrics,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the frozen support-triage HELD-OUT evaluation.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--mocked-preflight", action="store_true", help="Run zero-network held-out runner preflight.")
    mode.add_argument(
        "--execute-real-heldout",
        action="store_true",
        help="Run the one-time real HELD-OUT evaluation. Requires explicit supervisor authorization.",
    )
    args = parser.parse_args()
    if args.mocked_preflight:
        print(json.dumps(run_mocked_heldout_preflight(), indent=2, sort_keys=True))
        return 0
    output_path = execute_real_held_out_evaluation()
    print(f"HELD_OUT_EVALUATION_WRITTEN={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
