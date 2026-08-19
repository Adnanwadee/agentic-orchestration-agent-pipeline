from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.support_triage_classifier import (
    CLASSIFIER_PROMPT_SHA256,
    CLASSIFIER_PROMPT_VERSION,
    CLASSIFIER_REPAIR_INSTRUCTION_SHA256,
    CLASSIFIER_REPAIR_INSTRUCTION_VERSION,
    CONFIDENCE_THRESHOLD,
    MODEL_ID,
    ClassifierExecutionResult,
    TicketIntake,
    build_structured_output,
    lookup_authoritative_route,
)
from tools.support_triage_drafter import DRAFT_PROMPT_SHA256, DRAFT_PROMPT_VERSION


SEED_PATH = ROOT / "data" / "support_tickets_seed.json"
GROUND_TRUTH_PATH = ROOT / "data" / "support_tickets_ground_truth.json"
SPLIT_PATH = ROOT / "data" / "support_tickets_split.json"
FREEZE_MANIFEST_PATH = ROOT / "data" / "support_tickets_freeze_manifest.json"
DEV_ROOT = ROOT / "artifacts" / "evaluations" / "support_triage" / "dev_initial"
HELD_OUT_PATH = (
    ROOT
    / "artifacts"
    / "evaluations"
    / "support_triage"
    / "held_out_final"
    / "20260818T031003.013996Z"
    / "heldout_results.json"
)
OUTPUT_PATH = ROOT / "artifacts" / "evaluations" / "support_triage" / "full30_frozen_combined.json"

EXPECTED_HELD_OUT_SHA256 = "91e767b936272cd3363f46006b5f24f9862e4ae9131ce5717bdda9180a924584"
IBM_PRICING_SOURCE = "https://www.ibm.com/products/watsonx-ai/pricing"
IBM_PRICING_ACCESS_DATE = "2026-08-18"
IBM_INPUT_RATE_USD_PER_MILLION = 0.371
IBM_OUTPUT_RATE_USD_PER_MILLION = 1.484


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def percent(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def rate(numerator: int, denominator: int) -> str:
    value = percent(numerator, denominator)
    return "n/a" if value is None else f"{value:.2%}"


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
            "G4_FREEZE_HASH_MISMATCH "
            + json.dumps({"expected": expected, "actual": actual}, sort_keys=True)
        )
    return actual


def select_canonical_dev_artifact() -> tuple[Path, dict[str, Any], str]:
    split = load_json(SPLIT_PATH)
    candidates: list[tuple[Path, dict[str, Any], str]] = []
    for path in sorted(DEV_ROOT.glob("*/development_results.json")):
        payload = load_json(path)
        if payload.get("development_ids") != split["development_ids"]:
            continue
        if set(payload.get("development_ids", [])).intersection(split["held_out_ids"]):
            continue
        if payload.get("prompt_version") != CLASSIFIER_PROMPT_VERSION:
            continue
        if payload.get("prompt_sha256") != CLASSIFIER_PROMPT_SHA256:
            continue
        if payload.get("model_id") != MODEL_ID:
            continue
        if len(payload.get("results", [])) != len(split["development_ids"]):
            continue
        candidates.append((path, payload, sha256_file(path)))
    if not candidates:
        raise SystemExit("G4_CANONICAL_DEV_ARTIFACT_MISSING")
    return candidates[-1]


def verify_held_out_artifact() -> tuple[dict[str, Any], str]:
    payload = load_json(HELD_OUT_PATH)
    actual_sha = sha256_file(HELD_OUT_PATH)
    split = load_json(SPLIT_PATH)
    if actual_sha != EXPECTED_HELD_OUT_SHA256:
        raise SystemExit(
            "G4_HELD_OUT_SHA_MISMATCH "
            + json.dumps({"expected": EXPECTED_HELD_OUT_SHA256, "actual": actual_sha}, sort_keys=True)
        )
    required = {
        "classifier_prompt_version": CLASSIFIER_PROMPT_VERSION,
        "classifier_prompt_sha256": CLASSIFIER_PROMPT_SHA256,
        "classifier_repair_instruction_version": CLASSIFIER_REPAIR_INSTRUCTION_VERSION,
        "classifier_repair_instruction_sha256": CLASSIFIER_REPAIR_INSTRUCTION_SHA256,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "drafter_prompt_version": DRAFT_PROMPT_VERSION,
        "drafter_prompt_sha256": DRAFT_PROMPT_SHA256,
        "model_id": MODEL_ID,
        "scored": True,
    }
    mismatches = {
        key: {"expected": value, "actual": payload.get(key)}
        for key, value in required.items()
        if payload.get(key) != value
    }
    if mismatches:
        raise SystemExit("G4_HELD_OUT_METADATA_MISMATCH " + json.dumps(mismatches, sort_keys=True))
    if payload.get("held_out_ids") != split["held_out_ids"]:
        raise SystemExit("G4_HELD_OUT_IDS_MISMATCH")
    if set(payload["held_out_ids"]).intersection(split["development_ids"]):
        raise SystemExit("G4_HELD_OUT_DEV_OVERLAP")
    if len(payload.get("results", [])) != 15:
        raise SystemExit("G4_HELD_OUT_RECORD_COUNT_MISMATCH")
    return payload, actual_sha


def ground_truth_by_id() -> dict[str, dict[str, Any]]:
    return {record["ticket_id"]: record for record in load_json(GROUND_TRUTH_PATH)}


def source_tickets_by_id() -> dict[str, dict[str, Any]]:
    return {record["id"]: record for record in load_json(SEED_PATH)}


def dev_structured_record(result: dict[str, Any], ticket_text: str) -> dict[str, Any]:
    ticket = TicketIntake(ticket_id=result["ticket_id"], ticket_text=ticket_text)
    execution_payload = {key: value for key, value in result.items() if key != "ticket_text"}
    execution = ClassifierExecutionResult.model_validate(execution_payload)
    structured = build_structured_output(ticket, execution).model_dump()
    reporting_status = "auto_routed" if structured["status"] == "auto_route_pending" else structured["status"]
    return {
        "source_record": result,
        "structured_result": structured,
        "reporting_status": reporting_status,
        "draft_evidence": (
            "g3_manual_draft_quality_approved_v3"
            if structured["status"] == "auto_route_pending"
            else "not_applicable_review_or_invalid_path"
        ),
        "source_limitation": (
            "development source artifact contains classifier telemetry only; deterministic "
            "policy projection is used for routing metrics and approved v3 draft-quality "
            "evidence is used only for auto-route correctness gating"
        ),
    }


def held_out_structured_record(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_record": result,
        "structured_result": result,
        "reporting_status": result["status"],
        "draft_evidence": "held_out_recorded_draft" if result["status"] == "auto_routed" else "not_applicable_review_or_invalid_path",
        "source_limitation": None,
    }


def route_matches(classification: dict[str, Any] | None, record: dict[str, Any]) -> bool:
    if not classification:
        return False
    route = lookup_authoritative_route(classification.get("category"), classification.get("urgency"))
    return route is not None and record.get("assigned_team") == route.assigned_team and record.get("sla") == route.sla


def draft_path_valid(record: dict[str, Any], wrapper: dict[str, Any]) -> bool:
    if wrapper["source_split"] == "development":
        return wrapper["draft_evidence"] == "g3_manual_draft_quality_approved_v3"
    return bool(record.get("draft_response")) and record.get("draft_validation_status") == "valid"


def telemetry(records: list[dict[str, Any]], *, token_key: str, latency_key: str) -> dict[str, Any]:
    token_totals = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    token_call_count = 0
    latencies: list[float] = []
    for wrapper in records:
        structured = wrapper["structured_result"]
        usage = structured.get(token_key)
        if usage:
            token_call_count += 1
            for key in token_totals:
                token_totals[key] += int(usage.get(key, 0))
        latency = structured.get(latency_key)
        if isinstance(latency, (int, float)):
            latencies.append(float(latency))
    summary = {
        "calls_with_token_usage": token_call_count,
        "prompt_tokens": token_totals["prompt_tokens"],
        "completion_tokens": token_totals["completion_tokens"],
        "total_tokens": token_totals["total_tokens"],
        "latency_sample_count": len(latencies),
        "mean_latency_seconds": statistics.fmean(latencies) if latencies else None,
        "median_latency_seconds": statistics.median(latencies) if latencies else None,
        "p95_latency_seconds": None,
    }
    if len(latencies) >= 2:
        summary["p95_latency_seconds"] = statistics.quantiles(latencies, n=20, method="inclusive")[18]
    return summary


def compute_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    truth = ground_truth_by_id()
    total = len(records)
    category_correct = 0
    urgency_correct = 0
    urgency_denominator = 0
    null_urgency = []
    auto_route_correct = 0
    auto_route_records = []

    for wrapper in records:
        ticket_id = wrapper["ticket_id"]
        structured = wrapper["structured_result"]
        expected = truth[ticket_id]
        classification = structured.get("classification") or {}
        if classification.get("category") == expected["expected_category"]:
            category_correct += 1
        if expected["expected_urgency"] is None:
            null_urgency.append(
                {
                    "ticket_id": ticket_id,
                    "predicted_urgency": classification.get("urgency"),
                    "status": wrapper["reporting_status"],
                    "handled_as_null": classification.get("urgency") is None,
                }
            )
        else:
            urgency_denominator += 1
            if classification.get("urgency") == expected["expected_urgency"]:
                urgency_correct += 1
        if wrapper["reporting_status"] == "auto_routed":
            category_ok = classification.get("category") == expected["expected_category"]
            urgency_ok = (
                expected["expected_urgency"] is None
                or classification.get("urgency") == expected["expected_urgency"]
            )
            route_ok = route_matches(classification, structured)
            draft_ok = draft_path_valid(structured, wrapper)
            is_correct = category_ok and urgency_ok and route_ok and draft_ok
            auto_route_correct += int(is_correct)
            auto_route_records.append(
                {
                    "ticket_id": ticket_id,
                    "correct": is_correct,
                    "category_ok": category_ok,
                    "urgency_ok": urgency_ok,
                    "route_ok": route_ok,
                    "draft_ok": draft_ok,
                    "source_split": wrapper["source_split"],
                }
            )

    review_count = sum(1 for wrapper in records if wrapper["structured_result"].get("review_required") is True)
    auto_count = len(auto_route_records)
    draft_failed_count = sum(1 for wrapper in records if wrapper["reporting_status"] == "draft_failed")
    return {
        "total_records": total,
        "category_correct": category_correct,
        "category_denominator": total,
        "category_accuracy": percent(category_correct, total),
        "category_threshold": 0.80,
        "category_threshold_result": "PASS" if percent(category_correct, total) is not None and percent(category_correct, total) >= 0.80 else "FAIL",
        "urgency_correct": urgency_correct,
        "urgency_denominator": urgency_denominator,
        "urgency_accuracy": percent(urgency_correct, urgency_denominator),
        "urgency_threshold": 0.75,
        "urgency_threshold_result": "PASS" if percent(urgency_correct, urgency_denominator) is not None and percent(urgency_correct, urgency_denominator) >= 0.75 else "FAIL",
        "null_urgency_handling": null_urgency,
        "structured_output_count": total,
        "structured_output_rate": percent(total, total),
        "human_review_count": review_count,
        "human_review_rate": percent(review_count, total),
        "auto_routed_count": auto_count,
        "auto_routed_rate": percent(auto_count, total),
        "draft_failed_count": draft_failed_count,
        "draft_failed_rate": percent(draft_failed_count, total),
        "auto_route_correct": auto_route_correct,
        "auto_route_denominator": auto_count,
        "auto_route_correctness": percent(auto_route_correct, auto_count),
        "auto_route_correctness_definition": (
            "For reporting_status == auto_routed: primary category matches ground truth; "
            "urgency matches non-null ground truth; assigned_team/SLA match the authoritative "
            "routing table; and draft path is valid from held-out recorded draft telemetry or "
            "approved frozen v3 manual draft-quality evidence for classifier-only DEV records."
        ),
        "auto_route_records": auto_route_records,
    }


def model_inference_cost_usd(input_tokens: float, output_tokens: float) -> float:
    return (
        input_tokens / 1_000_000 * IBM_INPUT_RATE_USD_PER_MILLION
        + output_tokens / 1_000_000 * IBM_OUTPUT_RATE_USD_PER_MILLION
    )


def operational_estimate(metrics: dict[str, Any], classifier: dict[str, Any], drafter: dict[str, Any]) -> dict[str, Any]:
    tickets_per_day = 1000
    classifier_input_tokens_per_ticket = classifier["prompt_tokens"] / metrics["total_records"]
    classifier_output_tokens_per_ticket = classifier["completion_tokens"] / metrics["total_records"]
    classifier_tokens_per_ticket = classifier["total_tokens"] / metrics["total_records"]
    drafter_input_tokens_per_actual_call = (
        drafter["prompt_tokens"] / drafter["calls_with_token_usage"]
        if drafter["calls_with_token_usage"]
        else 0
    )
    drafter_output_tokens_per_actual_call = (
        drafter["completion_tokens"] / drafter["calls_with_token_usage"]
        if drafter["calls_with_token_usage"]
        else 0
    )
    drafter_tokens_per_actual_call = drafter_input_tokens_per_actual_call + drafter_output_tokens_per_actual_call
    auto_route_rate = metrics["auto_routed_rate"] or 0
    review_rate = metrics["human_review_rate"] or 0
    combined_input_tokens_per_ticket = (
        classifier_input_tokens_per_ticket + drafter_input_tokens_per_actual_call * auto_route_rate
    )
    combined_output_tokens_per_ticket = (
        classifier_output_tokens_per_ticket + drafter_output_tokens_per_actual_call * auto_route_rate
    )
    classifier_cost_per_ticket = model_inference_cost_usd(
        classifier_input_tokens_per_ticket, classifier_output_tokens_per_ticket
    )
    drafter_cost_per_actual_call = model_inference_cost_usd(
        drafter_input_tokens_per_actual_call, drafter_output_tokens_per_actual_call
    )
    combined_cost_per_ticket = model_inference_cost_usd(
        combined_input_tokens_per_ticket, combined_output_tokens_per_ticket
    )
    return {
        "tickets_per_day": tickets_per_day,
        "expected_classifier_calls_per_day": tickets_per_day,
        "expected_drafter_calls_per_day": tickets_per_day * auto_route_rate,
        "expected_human_review_tickets_per_day": tickets_per_day * review_rate,
        "classifier_input_tokens_per_ticket": classifier_input_tokens_per_ticket,
        "classifier_output_tokens_per_ticket": classifier_output_tokens_per_ticket,
        "average_classifier_tokens_per_ticket": classifier_tokens_per_ticket,
        "drafter_input_tokens_per_actual_call": drafter_input_tokens_per_actual_call,
        "drafter_output_tokens_per_actual_call": drafter_output_tokens_per_actual_call,
        "average_drafter_tokens_per_recorded_draft_call": drafter_tokens_per_actual_call,
        "expected_combined_input_tokens_per_ticket": combined_input_tokens_per_ticket,
        "expected_combined_output_tokens_per_ticket": combined_output_tokens_per_ticket,
        "estimated_classifier_tokens_per_day": classifier_tokens_per_ticket * tickets_per_day,
        "estimated_drafter_tokens_per_day": drafter_tokens_per_actual_call * tickets_per_day * auto_route_rate,
        "classifier_cost_per_ticket_usd": classifier_cost_per_ticket,
        "drafter_cost_per_actual_call_usd": drafter_cost_per_actual_call,
        "estimated_model_inference_cost_per_ticket_usd": combined_cost_per_ticket,
        "estimated_model_inference_cost_per_1000_tickets_usd": combined_cost_per_ticket * tickets_per_day,
        "dollar_cost_status": "ESTIMATED_FROM_OFFICIAL_IBM_PUBLIC_RATE",
        "pricing": {
            "source": IBM_PRICING_SOURCE,
            "access_date": IBM_PRICING_ACCESS_DATE,
            "model": MODEL_ID,
            "input_rate_usd_per_million_tokens": IBM_INPUT_RATE_USD_PER_MILLION,
            "output_rate_usd_per_million_tokens": IBM_OUTPUT_RATE_USD_PER_MILLION,
            "input_rate_usd_per_1000_tokens": IBM_INPUT_RATE_USD_PER_MILLION / 1000,
            "output_rate_usd_per_1000_tokens": IBM_OUTPUT_RATE_USD_PER_MILLION / 1000,
        },
        "cost_formula": (
            "model_inference_cost = input_tokens / 1,000,000 * 0.371 "
            "+ output_tokens / 1,000,000 * 1.484"
        ),
        "pricing_note": (
            "Public IBM pricing is indicative, may vary by locale/account/offering, and excludes "
            "taxes/duties. Estimate includes model-inference token cost only; it excludes fixed "
            "plan charges, Orchestrate charges, COS/storage, networking, human-review labor, "
            "taxes/duties, and account-specific costs."
        ),
    }


def build_report() -> dict[str, Any]:
    frozen_hashes = verify_frozen_hashes()
    split = load_json(SPLIT_PATH)
    manifest = load_json(FREEZE_MANIFEST_PATH)
    tickets = source_tickets_by_id()
    dev_path, dev_payload, dev_sha = select_canonical_dev_artifact()
    held_payload, held_sha = verify_held_out_artifact()

    records: list[dict[str, Any]] = []
    for result in dev_payload["results"]:
        wrapped = dev_structured_record(result, tickets[result["ticket_id"]]["text"])
        wrapped.update({"ticket_id": result["ticket_id"], "source_split": "development"})
        records.append(wrapped)
    for result in held_payload["results"]:
        wrapped = held_out_structured_record(result)
        wrapped.update({"ticket_id": result["ticket_id"], "source_split": "held_out"})
        records.append(wrapped)

    ids = [record["ticket_id"] for record in records]
    dev_ids = [record["ticket_id"] for record in records if record["source_split"] == "development"]
    held_ids = [record["ticket_id"] for record in records if record["source_split"] == "held_out"]
    metrics = compute_metrics(records)
    classifier_telemetry = telemetry(records, token_key="token_usage", latency_key="latency_seconds")
    drafter_telemetry = telemetry(records, token_key="draft_token_usage", latency_key="draft_latency_seconds")

    return {
        "artifact_type": "g4_derived_full30_support_triage_report",
        "inference_performed": False,
        "source_selection": {
            "development": {
                "path": dev_path.relative_to(ROOT).as_posix(),
                "sha256": dev_sha,
                "selection_reason": "Only frozen v2 DEV artifact with exact development IDs, no held-out IDs, selected model, and selected prompt SHA.",
            },
            "held_out": {
                "path": HELD_OUT_PATH.relative_to(ROOT).as_posix(),
                "sha256": held_sha,
                "expected_sha256": EXPECTED_HELD_OUT_SHA256,
                "sha256_status": "PASS",
            },
        },
        "frozen_configuration": {
            "model_id": MODEL_ID,
            "classifier_prompt_version": CLASSIFIER_PROMPT_VERSION,
            "classifier_prompt_sha256": CLASSIFIER_PROMPT_SHA256,
            "classifier_repair_instruction_version": CLASSIFIER_REPAIR_INSTRUCTION_VERSION,
            "classifier_repair_instruction_sha256": CLASSIFIER_REPAIR_INSTRUCTION_SHA256,
            "max_classifier_attempts": 2,
            "confidence_threshold": CONFIDENCE_THRESHOLD,
            "drafter_prompt_version": DRAFT_PROMPT_VERSION,
            "drafter_prompt_sha256": DRAFT_PROMPT_SHA256,
        },
        "frozen_dataset": {
            "freeze_version": manifest["freeze_version"],
            "hashes": frozen_hashes,
            "development_ids": split["development_ids"],
            "held_out_ids": split["held_out_ids"],
        },
        "integrity": {
            "total_records": len(records),
            "unique_ids": len(set(ids)),
            "development_count": len(dev_ids),
            "held_out_count": len(held_ids),
            "overlap": len(set(dev_ids).intersection(held_ids)),
            "dropped": len(set(split["development_ids"] + split["held_out_ids"]) - set(ids)),
            "duplicates": len(ids) - len(set(ids)),
            "every_record_structured": all(isinstance(record["structured_result"], dict) for record in records),
        },
        "records": records,
        "metrics": metrics,
        "telemetry": {
            "classifier": classifier_telemetry,
            "drafter_recorded_held_out_only": drafter_telemetry,
            "pipeline": {
                "average_model_tokens_per_incoming_ticket_recorded": (
                    classifier_telemetry["total_tokens"] + drafter_telemetry["total_tokens"]
                )
                / len(records),
                "average_classifier_tokens_per_ticket": classifier_telemetry["total_tokens"] / len(records),
                "average_drafting_tokens_per_auto_routed_ticket_recorded": (
                    drafter_telemetry["total_tokens"] / metrics["auto_routed_count"]
                    if metrics["auto_routed_count"]
                    else None
                ),
                "tickets_requiring_drafting_rate": metrics["auto_routed_rate"],
                "human_review_rate": metrics["human_review_rate"],
                "latency_scope_note": "Recorded classifier/drafter model-tool telemetry only; not end-to-end Orchestrate Flow latency.",
            },
        },
        "operational_estimate": operational_estimate(metrics, classifier_telemetry, drafter_telemetry),
        "validation": {
            "TOTAL_RECORDS": len(records),
            "UNIQUE_IDS": len(set(ids)),
            "DEV_COUNT": len(dev_ids),
            "HELD_OUT_COUNT": len(held_ids),
            "OVERLAP": len(set(dev_ids).intersection(held_ids)),
            "DROPPED": len(set(split["development_ids"] + split["held_out_ids"]) - set(ids)),
            "DUPLICATES": len(ids) - len(set(ids)),
        },
    }


def write_report(path: Path = OUTPUT_PATH) -> Path:
    report = build_report()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the derived G4 frozen full-30 support-triage report.")
    parser.add_argument("--check", action="store_true", help="Build and validate without writing the artifact.")
    args = parser.parse_args()
    report = build_report()
    if args.check:
        print(json.dumps({"status": "PASS", "validation": report["validation"], "metrics": report["metrics"]}, sort_keys=True))
        return 0
    output_path = write_report()
    print(f"G4_FULL30_REPORT_WRITTEN={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
