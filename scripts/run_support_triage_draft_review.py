from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.support_triage_drafter import (
    DRAFT_PROMPT_SHA256,
    DRAFT_PROMPT_VERSION,
    MODEL_ID,
    DraftRequest,
    _sanitize_error_message,
    draft_with_bounded_attempts,
    local_env_drafter,
)


SYNTHETIC_DRAFT_REVIEW_CASES: list[dict[str, str]] = [
    {
        "ticket_id": "DRAFT-SMOKE-001",
        "ticket_text": "My renewal invoice includes a cancellation fee I do not recognize.",
        "assigned_team": "Billing — Standard",
        "sla": "4 hours",
    },
    {
        "ticket_id": "DRAFT-SMOKE-002",
        "ticket_text": "The dashboard export button returns an error when I download today's report.",
        "assigned_team": "Engineering — Support",
        "sla": "2 hours",
    },
    {
        "ticket_id": "DRAFT-SMOKE-003",
        "ticket_text": "I need help updating the admin email on my account before an access handoff.",
        "assigned_team": "Customer Success",
        "sla": "4 hours",
    },
    {
        "ticket_id": "DRAFT-SMOKE-004",
        "ticket_text": "Where can I find the product release notes for this month?",
        "assigned_team": "Customer Success",
        "sla": "2 business days",
    },
]


def _base_harness_output() -> dict[str, Any]:
    planned_case_count = len(SYNTHETIC_DRAFT_REVIEW_CASES)
    return {
        "mode": "manual_draft_quality_review_harness",
        "model_id": MODEL_ID,
        "draft_prompt_version": DRAFT_PROMPT_VERSION,
        "draft_prompt_sha256": DRAFT_PROMPT_SHA256,
        "planned_case_count": planned_case_count,
        "executed_case_count": 0,
        "results": [],
        "DRAFT_REVIEW_CASES": 0,
        "CLASSIFIER_CALLS": 0,
        "HELD_OUT_CALLS": 0,
    }


def run_manual_draft_review_harness(call_model=None) -> dict[str, Any]:
    output = _base_harness_output()
    if call_model is None:
        try:
            call_model = local_env_drafter()
        except Exception as exc:
            output.update(
                {
                    "error_code": "DRAFTER_INITIALIZATION_ERROR",
                    "error_message": _sanitize_error_message(str(exc)),
                    "final_status": "DRAFT_REVIEW_HARNESS=INITIALIZATION_ERROR",
                }
            )
            return output

    results = []
    for case in SYNTHETIC_DRAFT_REVIEW_CASES:
        request = DraftRequest.model_validate(case)
        execution = draft_with_bounded_attempts(request, call_model)
        results.append(
            {
                "ticket_id": request.ticket_id,
                "ticket_text": request.ticket_text,
                "assigned_team": request.assigned_team,
                "sla": request.sla,
                "draft_response": execution.draft_response,
                "attempt_count": execution.attempt_count,
                "validation_status": execution.validation_status,
                "error_code": execution.error_code,
                "error_message": execution.error_message,
                "latency_seconds": execution.latency_seconds,
                "token_usage": execution.token_usage,
            }
        )

    executed_case_count = len(results)
    output.update(
        {
            "executed_case_count": executed_case_count,
            "results": results,
            "DRAFT_REVIEW_CASES": executed_case_count,
            "final_status": (
                "DRAFT_REVIEW_HARNESS=STRUCTURALLY_VALID"
                if all(result["validation_status"] == "valid" for result in results)
                else "DRAFT_REVIEW_HARNESS=EXECUTION_INVALID"
            ),
        }
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the four-case synthetic support-triage drafter review harness."
    )
    parser.add_argument(
        "--smoke-real-drafter",
        action="store_true",
        required=True,
        help="Run four synthetic drafter-only cases. Requires explicit MANUAL authorization.",
    )
    parser.parse_args()
    output = run_manual_draft_review_harness()
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if output["final_status"] == "DRAFT_REVIEW_HARNESS=STRUCTURALLY_VALID" else 1


if __name__ == "__main__":
    raise SystemExit(main())
