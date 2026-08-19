from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.support_triage_classifier import (
    CLASSIFIER_REPAIR_INSTRUCTION_SHA256,
    CLASSIFIER_REPAIR_INSTRUCTION_VERSION,
    CLASSIFIER_PROMPT_SHA256,
    CLASSIFIER_PROMPT_VERSION,
    MODEL_ID,
    ModelCallResult,
    TicketIntake,
    classify_with_bounded_attempts,
    local_env_classifier,
)


SEED_PATH = ROOT / "data" / "support_tickets_seed.json"
GROUND_TRUTH_PATH = ROOT / "data" / "support_tickets_ground_truth.json"
SPLIT_PATH = ROOT / "data" / "support_tickets_split.json"
FREEZE_MANIFEST_PATH = ROOT / "data" / "support_tickets_freeze_manifest.json"
DEFAULT_OUTPUT_ROOT = ROOT / "artifacts" / "evaluations" / "support_triage" / "dev_initial"
SMOKE_TICKET_ID = "SMOKE-INFRA-001"
SMOKE_TICKET_TEXT = "The demo settings page shows an error when I click Save."


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_frozen_hashes() -> dict[str, str]:
    manifest = load_json(FREEZE_MANIFEST_PATH)
    expected = manifest["sha256"]
    actual = {
        "support_tickets_seed": sha256_file(SEED_PATH),
        "support_tickets_ground_truth": sha256_file(GROUND_TRUTH_PATH),
        "support_tickets_split": sha256_file(SPLIT_PATH),
    }
    if actual != expected:
        raise SystemExit(
            "DATASET_FREEZE_HASH_MISMATCH "
            + json.dumps({"expected": expected, "actual": actual}, sort_keys=True)
        )
    return actual


def load_development_records() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]]:
    seed = {ticket["id"]: ticket for ticket in load_json(SEED_PATH)}
    ground_truth = {record["ticket_id"]: record for record in load_json(GROUND_TRUTH_PATH)}
    split = load_json(SPLIT_PATH)
    manifest = load_json(FREEZE_MANIFEST_PATH)
    development_ids = split["development_ids"]
    held_out_ids = set(split["held_out_ids"])

    if development_ids != manifest["development_ids"]:
        raise SystemExit("DEV_SPLIT_MANIFEST_MISMATCH")
    if held_out_ids.intersection(development_ids):
        raise SystemExit("HELD_OUT_LEAKAGE_DETECTED")

    records = []
    for ticket_id in development_ids:
        if ticket_id in held_out_ids:
            raise SystemExit(f"HELD_OUT_ID_IN_DEV_RUN: {ticket_id}")
        ticket = seed[ticket_id]
        records.append(
            {
                "ticket_id": ticket_id,
                "ticket_text": ticket["text"],
                "ground_truth": ground_truth[ticket_id],
            }
        )
    return records, ground_truth, manifest


def compute_metrics(results: list[dict[str, Any]], ground_truth: dict[str, dict[str, Any]]) -> dict[str, Any]:
    category_correct = 0
    urgency_correct = 0
    urgency_denominator = 0
    null_urgency_handling = []

    for result in results:
        ticket_id = result["ticket_id"]
        expected = ground_truth[ticket_id]
        predicted = result.get("classification")
        predicted_dict = predicted if isinstance(predicted, dict) else {}
        if predicted_dict.get("category") == expected["expected_category"]:
            category_correct += 1
        expected_urgency = expected["expected_urgency"]
        if expected_urgency is None:
            validation_status = result.get("validation_status")
            classification_present = isinstance(predicted, dict)
            predicted_urgency = predicted_dict.get("urgency") if classification_present else None
            null_urgency_handling.append(
                {
                    "ticket_id": ticket_id,
                    "validation_status": validation_status,
                    "classification_present": classification_present,
                    "predicted_urgency": predicted_urgency,
                    "expected_urgency": None,
                    "null_urgency_match": (
                        validation_status == "valid"
                        and classification_present
                        and predicted_urgency is None
                    ),
                }
            )
        else:
            urgency_denominator += 1
            if predicted_dict.get("urgency") == expected_urgency:
                urgency_correct += 1

    return {
        "category_accuracy": category_correct / len(results) if results else 0.0,
        "category_correct": category_correct,
        "category_denominator": len(results),
        "urgency_accuracy": urgency_correct / urgency_denominator if urgency_denominator else None,
        "urgency_correct": urgency_correct,
        "urgency_denominator": urgency_denominator,
        "null_urgency_handling": null_urgency_handling,
        "explicit_ticket_reports": {
            ticket_id: next((item for item in results if item["ticket_id"] == ticket_id), None)
            for ticket_id in ("T09", "T10", "T21")
        },
    }


def dry_run() -> dict[str, Any]:
    hashes = verify_frozen_hashes()
    records, _, manifest = load_development_records()
    dev_ids = [record["ticket_id"] for record in records]
    held_out_ids = manifest["held_out_ids"]
    return {
        "mode": "dry_run",
        "real_classifier_calls": 0,
        "model_id": MODEL_ID,
        "prompt_version": CLASSIFIER_PROMPT_VERSION,
        "prompt_sha256": CLASSIFIER_PROMPT_SHA256,
        "freeze_version": manifest["freeze_version"],
        "frozen_hashes": hashes,
        "development_ids": dev_ids,
        "development_count": len(dev_ids),
        "held_out_ids_excluded": not bool(set(dev_ids).intersection(held_out_ids)),
        "output_root": str(DEFAULT_OUTPUT_ROOT),
    }


def safe_error_metadata(exc: Exception) -> dict[str, str]:
    return {
        "error_type": type(exc).__name__,
        "error_message": str(exc),
    }


def execute_development_evaluation(output_root: Path = DEFAULT_OUTPUT_ROOT) -> Path:
    hashes = verify_frozen_hashes()
    records, ground_truth, manifest = load_development_records()
    try:
        classifier = local_env_classifier()
    except Exception as exc:
        error = safe_error_metadata(exc)
        raise SystemExit(
            "DEV_EVALUATION_INVALID_INITIALIZATION_ERROR "
            + json.dumps(
                {
                    "scored": False,
                    "dev_tickets_executed": 0,
                    "error_code": "CLASSIFIER_INITIALIZATION_ERROR",
                    "error_type": error["error_type"],
                    "error_message": error["error_message"],
                },
                sort_keys=True,
            )
        ) from exc
    run_started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    outputs = []

    for record in records:
        ticket = TicketIntake(
            ticket_id=record["ticket_id"],
            ticket_text=record["ticket_text"],
        )
        execution = classify_with_bounded_attempts(ticket, classifier)
        payload = execution.model_dump()
        payload["ticket_text"] = ticket.ticket_text
        if execution.validation_status == "execution_error":
            raise SystemExit(
                "DEV_EVALUATION_INVALID_EXECUTION_ERROR "
                + json.dumps(
                    {
                        "scored": False,
                        "failed_ticket_id": ticket.ticket_id,
                        "validation_status": execution.validation_status,
                        "attempt_count": execution.attempt_count,
                        "error_code": execution.error_code,
                        "error_message": execution.error_message,
                    },
                    sort_keys=True,
                )
            )
        outputs.append(payload)

    metrics = compute_metrics(outputs, ground_truth)
    run_dir = output_root / run_started.replace(":", "").replace("-", "")
    run_dir.mkdir(parents=True, exist_ok=False)
    output_path = run_dir / "development_results.json"
    output_path.write_text(
        json.dumps(
            {
                "run_started_utc": run_started,
                "model_id": MODEL_ID,
                "prompt_version": CLASSIFIER_PROMPT_VERSION,
                "prompt_sha256": CLASSIFIER_PROMPT_SHA256,
                "freeze_version": manifest["freeze_version"],
                "frozen_hashes": hashes,
                "development_ids": [record["ticket_id"] for record in records],
                "results": outputs,
                "metrics": metrics,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return output_path


def run_smoke(call_model=None) -> dict[str, Any]:
    ticket = TicketIntake(ticket_id=SMOKE_TICKET_ID, ticket_text=SMOKE_TICKET_TEXT)
    if call_model is None:
        started = time.perf_counter()
        try:
            call_model = local_env_classifier()
        except Exception as exc:
            error = safe_error_metadata(exc)
            return {
                "smoke_ticket_id": SMOKE_TICKET_ID,
                "smoke_ticket_text": SMOKE_TICKET_TEXT,
                "model_id": MODEL_ID,
                "base_prompt_version": CLASSIFIER_PROMPT_VERSION,
                "base_prompt_sha256": CLASSIFIER_PROMPT_SHA256,
                "repair_instruction_version": CLASSIFIER_REPAIR_INSTRUCTION_VERSION,
                "repair_instruction_sha256": CLASSIFIER_REPAIR_INSTRUCTION_SHA256,
                "validation_status": "execution_error",
                "attempt_count": 0,
                "classification": None,
                "latency_seconds": time.perf_counter() - started,
                "token_usage": None,
                "error_code": "CLASSIFIER_INITIALIZATION_ERROR",
                "error_type": error["error_type"],
                "error_message": error["error_message"],
                "final_status": "SMOKE_CLASSIFIER_INTEGRATION=EXECUTION_ERROR",
            }
    execution = classify_with_bounded_attempts(ticket, call_model)
    output = {
        "smoke_ticket_id": SMOKE_TICKET_ID,
        "smoke_ticket_text": SMOKE_TICKET_TEXT,
        "model_id": MODEL_ID,
        "base_prompt_version": CLASSIFIER_PROMPT_VERSION,
        "base_prompt_sha256": CLASSIFIER_PROMPT_SHA256,
        "repair_instruction_version": CLASSIFIER_REPAIR_INSTRUCTION_VERSION,
        "repair_instruction_sha256": CLASSIFIER_REPAIR_INSTRUCTION_SHA256,
        "validation_status": execution.validation_status,
        "attempt_count": execution.attempt_count,
        "classification": execution.classification.model_dump() if execution.classification else None,
        "latency_seconds": execution.latency_seconds,
        "token_usage": execution.token_usage,
        "error_code": execution.error_code,
        "error_message": execution.error_message,
    }
    if execution.validation_status == "valid":
        output["final_status"] = "SMOKE_CLASSIFIER_INTEGRATION=PASS"
    elif execution.validation_status == "invalid_exhausted":
        output["final_status"] = "SMOKE_CLASSIFIER_INTEGRATION=MODEL_OUTPUT_INVALID"
    else:
        output["final_status"] = "SMOKE_CLASSIFIER_INTEGRATION=EXECUTION_ERROR"
    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the frozen support-triage DEVELOPMENT evaluation or safe preflight."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Verify freeze and DEV IDs without model calls.")
    mode.add_argument(
        "--execute-real-classifier",
        action="store_true",
        help="Run the initial DEV classifier evaluation. Do not use until explicitly authorized.",
    )
    mode.add_argument(
        "--smoke-real-classifier",
        action="store_true",
        help="Run one non-dataset infrastructure smoke ticket. Do not use until explicitly authorized.",
    )
    args = parser.parse_args()

    if args.dry_run:
        print(json.dumps(dry_run(), indent=2, sort_keys=True))
        return 0
    if args.smoke_real_classifier:
        output = run_smoke()
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0 if output["validation_status"] == "valid" else 1
    output_path = execute_development_evaluation()
    print(f"DEVELOPMENT_EVALUATION_WRITTEN={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
