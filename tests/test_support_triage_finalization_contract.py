import json

import pytest

from scripts import run_support_triage_heldout_eval as heldout_runner
from tools import support_triage_classifier as classifier
from tools import support_triage_drafter as drafter
from tools.support_triage_classifier import (
    ClassificationResult,
    ClassifierExecutionResult,
    ModelCallResult,
    TicketIntake,
    build_structured_output,
)
from tools.support_triage_drafter import (
    DraftExecutionResult,
    DraftModelCallResult,
    DraftRequest,
    apply_draft_execution,
    draft_auto_route_response,
    finalize_support_triage_output,
)


def classification(**overrides):
    payload = {
        "category": "technical",
        "secondary_category": None,
        "urgency": "medium",
        "confidence": 0.90,
        "reasoning": "A technical product issue is described.",
    }
    payload.update(overrides)
    return ClassificationResult.model_validate(payload)


def classifier_execution(**overrides):
    return ClassifierExecutionResult(
        ticket_id="T-FINAL",
        classification=classification(**overrides),
        validation_status="valid",
        attempt_count=1,
        latency_seconds=0.12,
        token_usage={"prompt_tokens": 10, "completion_tokens": 3, "total_tokens": 13},
    )


def ticket(ticket_id="T-FINAL", text="The export report fails with an error."):
    return TicketIntake(ticket_id=ticket_id, ticket_text=text)


def model_problem_summary(summary="the export report failure"):
    return json.dumps({"problem_summary": summary})


def valid_drafter(request: DraftRequest, attempt: int) -> DraftModelCallResult:
    return DraftModelCallResult(
        raw_text=model_problem_summary(),
        latency_seconds=0.05,
        token_usage={"prompt_tokens": 4, "completion_tokens": 2, "total_tokens": 6},
    )


def assert_identity_and_classifier_telemetry(output, expected_ticket):
    assert output.ticket_id == expected_ticket.ticket_id
    assert output.ticket_text == expected_ticket.ticket_text
    assert output.latency_seconds == pytest.approx(0.12) or output.latency_seconds is None
    if output.validation_status == "valid":
        assert output.token_usage == {"prompt_tokens": 10, "completion_tokens": 3, "total_tokens": 13}


def test_auto_route_valid_draft_finalizes_as_auto_routed():
    expected_ticket = ticket()
    output = finalize_support_triage_output(expected_ticket, classifier_execution(), valid_drafter)

    assert_identity_and_classifier_telemetry(output, expected_ticket)
    assert output.review_required is False
    assert output.review_reasons == []
    assert output.assigned_team == "Engineering — Support"
    assert output.sla == "1 business day"
    assert output.status == "auto_routed"
    assert output.draft_response == (
        "Thank you for reaching out about the export report failure.\n\n"
        "Assigned team: Engineering — Support. SLA target: 1 business day."
    )
    assert output.draft_validation_status == "valid"
    assert output.draft_attempt_count == 1
    assert output.draft_token_usage == {"prompt_tokens": 4, "completion_tokens": 2, "total_tokens": 6}
    assert output.draft_prompt_version == "support-triage-drafter-v3"


@pytest.mark.parametrize(
    ("execution_result", "expected_reasons"),
    [
        (classifier_execution(confidence=0.79), ["confidence_below_threshold"]),
        (classifier_execution(secondary_category="billing"), ["secondary_category_present"]),
        (classifier_execution(urgency=None), ["urgency_null"]),
        (classifier_execution(category="account", urgency="critical"), ["unsupported_route"]),
    ],
)
def test_human_review_paths_skip_drafter(execution_result, expected_reasons):
    calls = []

    def fail_if_called(request, attempt):
        calls.append(attempt)
        raise AssertionError("drafter must not be called")

    output = finalize_support_triage_output(ticket(), execution_result, fail_if_called)

    assert output.review_required is True
    assert output.review_reasons == expected_reasons
    assert output.assigned_team == "Triage — Human"
    assert output.sla == "Immediate"
    assert output.draft_response is None
    assert output.status == "human_review"
    assert output.draft_validation_status is None
    assert calls == []


@pytest.mark.parametrize("status", ["invalid_exhausted", "execution_error"])
def test_invalid_classifier_paths_finalize_as_invalid_output(status):
    execution_result = ClassifierExecutionResult(
        ticket_id="T-FINAL",
        classification=None,
        validation_status=status,
        attempt_count=2 if status == "invalid_exhausted" else 1,
        error_code="CLASSIFIER_EXECUTION_ERROR" if status == "execution_error" else "CLASSIFICATION_INVALID_EXHAUSTED",
        error_message="classifier failed",
        latency_seconds=0.4,
        token_usage={"prompt_tokens": 2, "completion_tokens": 1, "total_tokens": 3},
    )

    output = finalize_support_triage_output(ticket(), execution_result, valid_drafter)

    assert output.classification is None
    assert output.classification_valid is False
    assert output.review_required is True
    assert output.review_reasons == ["invalid_classification_output"]
    assert output.assigned_team == "Triage — Human"
    assert output.sla == "Immediate"
    assert output.draft_response is None
    assert output.status == "invalid_output"
    assert output.error_code == execution_result.error_code
    assert output.draft_validation_status is None


def test_draft_initialization_error_finalizes_as_draft_failed_without_review_trigger():
    base = build_structured_output(ticket(), classifier_execution())
    draft = DraftExecutionResult(
        ticket_id="T-FINAL",
        draft_response=None,
        validation_status="execution_error",
        attempt_count=0,
        error_code="DRAFTER_INITIALIZATION_ERROR",
        error_message="init failed",
        latency_seconds=0.2,
        token_usage=None,
    )

    output = apply_draft_execution(base, draft)

    assert output.review_required is False
    assert output.review_reasons == []
    assert output.assigned_team == "Engineering — Support"
    assert output.sla == "1 business day"
    assert output.draft_response is None
    assert output.status == "draft_failed"
    assert output.draft_validation_status == "execution_error"
    assert output.draft_attempt_count == 0
    assert output.draft_error_code == "DRAFTER_INITIALIZATION_ERROR"
    assert output.draft_token_usage is None


@pytest.mark.parametrize(
    ("responder", "expected_status", "expected_attempts"),
    [
        (lambda request, attempt: (_ for _ in ()).throw(RuntimeError("draft host failed")), "execution_error", 1),
        (lambda request, attempt: DraftModelCallResult(raw_text="{bad json", latency_seconds=0.01), "invalid_exhausted", 2),
    ],
)
def test_draft_runtime_and_invalid_exhausted_finalize_as_draft_failed(
    responder, expected_status, expected_attempts
):
    base = build_structured_output(ticket(), classifier_execution())
    output, draft = draft_auto_route_response(base, responder)

    assert draft.validation_status == expected_status
    assert draft.attempt_count == expected_attempts
    assert output.status == "draft_failed"
    assert output.review_required is False
    assert output.review_reasons == []
    assert output.assigned_team == "Engineering — Support"
    assert output.sla == "1 business day"
    assert output.draft_response is None
    assert output.draft_validation_status == expected_status


def test_ticket_9_and_ticket_10_contracts_remain_review_paths():
    t09 = finalize_support_triage_output(
        ticket("T09", "I need account access fixed and have a billing question."),
        classifier_execution(category="account", secondary_category="billing", urgency="medium"),
        valid_drafter,
    )
    t10 = finalize_support_triage_output(
        ticket("T10", "it doesnt work fix it"),
        classifier_execution(category="technical", urgency=None, confidence=0.50),
        valid_drafter,
    )

    assert t09.status == "human_review"
    assert t09.review_reasons == ["secondary_category_present"]
    assert t09.draft_response is None
    assert t10.status == "human_review"
    assert t10.review_reasons == ["confidence_below_threshold", "urgency_null"]
    assert t10.draft_response is None


def test_mocked_heldout_preflight_produces_one_record_per_frozen_id(monkeypatch):
    ground_truth_reads = []
    original_load_ground_truth = heldout_runner.load_ground_truth_records

    def tracked_load_ground_truth():
        ground_truth_reads.append("after_inference")
        return original_load_ground_truth()

    monkeypatch.setattr(heldout_runner, "load_ground_truth_records", tracked_load_ground_truth)
    output = heldout_runner.run_mocked_heldout_preflight()

    assert output["MOCKED_HELDOUT_PREFLIGHT"] == "PASS"
    assert output["HELD_OUT_ID_COUNT"] == 15
    assert output["EXECUTED_RECORD_COUNT"] == 15
    assert output["UNIQUE_RECORD_COUNT"] == 15
    assert output["DROPPED_RECORDS"] == 0
    assert output["DUPLICATE_RECORDS"] == 0
    assert output["produced_ids"] == output["held_out_ids"]
    assert ground_truth_reads == ["after_inference"]


def test_heldout_runner_real_initialization_failure_executes_zero_tickets(monkeypatch, tmp_path):
    def fail_classifier_init():
        raise RuntimeError("classifier init failed")

    monkeypatch.setattr(heldout_runner, "local_env_classifier", fail_classifier_init)

    with pytest.raises(SystemExit) as exc_info:
        heldout_runner.execute_real_held_out_evaluation(output_root=tmp_path)

    message = str(exc_info.value)
    assert "HELD_OUT_INITIALIZATION_ERROR" in message
    assert '"executed_ticket_count": 0' in message
    assert '"scored": false' in message
    assert not list(tmp_path.rglob("heldout_results.json"))


def test_heldout_runner_source_keeps_inference_and_scoring_separate():
    source = (heldout_runner.ROOT / "scripts" / "run_support_triage_heldout_eval.py").read_text(
        encoding="utf-8"
    )
    inference_body = source.split("def run_inference_phase", 1)[1].split("def _finalize_ticket", 1)[0]
    assert "GROUND_TRUTH_PATH" not in inference_body
    assert "load_ground_truth_records" not in inference_body
    assert "--execute-real-heldout" in source
    assert "--mocked-preflight" in source
    assert "support-triage-classifier-v2" not in source
    assert heldout_runner.CLASSIFIER_PROMPT_VERSION == "support-triage-classifier-v2"
    assert heldout_runner.DRAFT_PROMPT_VERSION == "support-triage-drafter-v3"
