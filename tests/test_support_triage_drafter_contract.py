import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts import run_support_triage_draft_review as draft_harness
from tools import support_triage_classifier as classifier
from tools import support_triage_drafter as drafter
from tools.support_triage_classifier import (
    ClassificationResult,
    ClassifierExecutionResult,
    TicketIntake,
    build_structured_output,
)
from tools.support_triage_drafter import (
    DraftModelCallResult,
    DraftOutputValidationError,
    DraftProblemSummaryResult,
    DraftRequest,
    compose_draft_response,
    draft_auto_route_response,
    draft_support_response,
    draft_with_bounded_attempts,
    parse_draft_response,
)


ROOT = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT / "data" / "support_tickets_seed.json"
DRAFTER_SOURCE_PATH = ROOT / "tools" / "support_triage_drafter.py"
HARNESS_SOURCE_PATH = ROOT / "scripts" / "run_support_triage_draft_review.py"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def valid_problem_summary(problem="export report failure"):
    return problem


def request(**overrides):
    payload = {
        "ticket_id": "DRAFT-UNIT-001",
        "ticket_text": "The export report fails with an error.",
        "assigned_team": "Engineering — Support",
        "sla": "1 business day",
    }
    payload.update(overrides)
    return DraftRequest.model_validate(payload)


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


def execution(**overrides):
    return ClassifierExecutionResult(
        ticket_id="T99",
        classification=classification(**overrides),
        validation_status="valid",
        attempt_count=1,
    )


def structured_output(**overrides):
    return build_structured_output(
        TicketIntake(ticket_id="T99", ticket_text="The export report fails with an error."),
        execution(**overrides),
    )


def model_json(text):
    return json.dumps({"problem_summary": text})


def test_draft_request_and_result_schema_are_strict():
    assert request().assigned_team == "Engineering — Support"
    with pytest.raises(ValidationError):
        DraftRequest(ticket_id="", ticket_text="Issue", assigned_team="Team", sla="1 hour")
    with pytest.raises(ValidationError):
        DraftRequest(ticket_id="D1", ticket_text="Issue", assigned_team=" ", sla="1 hour")
    with pytest.raises(ValidationError):
        DraftProblemSummaryResult(problem_summary="ok", extra_key=True)


def test_valid_strict_json_draft_is_accepted():
    req = request()
    parsed = parse_draft_response(model_json(valid_problem_summary()), req)
    assert parsed.problem_summary == "export report failure"


@pytest.mark.parametrize(
    "raw_text",
    [
        "not json",
        json.dumps(["not", "an", "object"]),
        json.dumps({"message": "missing required key"}),
        json.dumps({"problem_summary": valid_problem_summary(), "assigned_team": "Engineering — Support"}),
        json.dumps({"problem_summary": "   "}),
        json.dumps({"problem_summary": "x" * 301}),
    ],
)
def test_invalid_draft_shapes_are_rejected(raw_text):
    with pytest.raises(DraftOutputValidationError):
        parse_draft_response(raw_text, request())


@pytest.mark.parametrize(
    "problem_summary",
    [
        "export error assigned to Engineering — Support",
        "export error with SLA: 1 business day",
        "we are assisting with the export error",
        "we will provide the requested information",
        "the team has been notified about the export error",
    ],
)
def test_route_sla_context_and_company_action_claims_are_rejected_in_problem_summary(problem_summary):
    with pytest.raises(DraftOutputValidationError):
        parse_draft_response(model_json(problem_summary), request())


def test_final_draft_appends_team_and_sla_deterministically():
    req = request()
    problem_summary = valid_problem_summary()

    final_draft = compose_draft_response(problem_summary, req)

    assert final_draft == (
        "Thank you for reaching out about export report failure.\n\n"
        "Assigned team: Engineering — Support. SLA target: 1 business day."
    )


def test_invalid_first_attempt_then_valid_repair_attempt_aggregates_telemetry():
    calls = []

    def responder(req, attempt):
        calls.append(attempt)
        if attempt == 1:
            return DraftModelCallResult(
                raw_text="{bad json",
                latency_seconds=0.2,
                token_usage={"prompt_tokens": 5, "completion_tokens": 1, "total_tokens": 6},
            )
        return DraftModelCallResult(
            raw_text=model_json(valid_problem_summary()),
            latency_seconds=0.4,
            token_usage={"prompt_tokens": 7, "completion_tokens": 4, "total_tokens": 11},
        )

    result = draft_with_bounded_attempts(request(), responder)
    assert result.validation_status == "valid"
    assert result.attempt_count == 2
    assert result.latency_seconds == pytest.approx(0.6)
    assert result.token_usage == {
        "prompt_tokens": 12,
        "completion_tokens": 5,
        "total_tokens": 17,
    }
    assert calls == [1, 2]


def test_invalid_draft_exhausts_after_two_attempts():
    calls = []

    def responder(req, attempt):
        calls.append(attempt)
        return DraftModelCallResult(raw_text="{bad json", latency_seconds=0.1)

    result = draft_with_bounded_attempts(request(), responder)
    assert result.validation_status == "invalid_exhausted"
    assert result.draft_response is None
    assert result.error_code == "DRAFT_INVALID_EXHAUSTED"
    assert result.attempt_count == drafter.MAX_DRAFT_ATTEMPTS == 2
    assert calls == [1, 2]


def test_runtime_failure_on_first_attempt_does_not_retry_and_sanitizes_error():
    calls = []

    def responder(req, attempt):
        calls.append(attempt)
        raise RuntimeError("call failed api_key=abc123456789 token=secret-token")

    result = draft_with_bounded_attempts(request(), responder)
    assert result.validation_status == "execution_error"
    assert result.error_code == "DRAFT_EXECUTION_ERROR"
    assert "abc123456789" not in result.error_message
    assert "secret-token" not in result.error_message
    assert "[redacted]" in result.error_message
    assert result.token_usage is None
    assert calls == [1]


def test_runtime_failure_on_repair_attempt_does_not_retry_or_invent_usage():
    calls = []

    def responder(req, attempt):
        calls.append(attempt)
        if attempt == 1:
            return DraftModelCallResult(
                raw_text="{bad json",
                latency_seconds=0.25,
                token_usage={"prompt_tokens": 3, "completion_tokens": 1, "total_tokens": 4},
            )
        raise RuntimeError("repair host failed")

    result = draft_with_bounded_attempts(request(), responder)
    assert result.validation_status == "execution_error"
    assert result.attempt_count == 2
    assert result.token_usage == {"prompt_tokens": 3, "completion_tokens": 1, "total_tokens": 4}
    assert calls == [1, 2]


def test_public_draft_tool_initialization_failure_is_structured_and_sanitized(monkeypatch):
    calls = []

    def fail_initialization(*, project_id, url):
        calls.append((project_id, url))
        raise RuntimeError(
            "init failed api_key=abc123 Authorization: Bearer token-secret password: bad-secret"
        )

    monkeypatch.setattr(drafter, "orchestrate_connection_drafter", fail_initialization)

    result = draft_support_response(
        ticket_id="DRAFT-INIT-001",
        ticket_text="The export report fails with an error.",
        assigned_team="Engineering — Support",
        sla="1 business day",
        wx_project_id="project-1",
    ).content

    assert result["ticket_id"] == "DRAFT-INIT-001"
    assert result["draft_response"] is None
    assert result["validation_status"] == "execution_error"
    assert result["attempt_count"] == 0
    assert result["error_code"] == "DRAFTER_INITIALIZATION_ERROR"
    assert result["token_usage"] is None
    assert "abc123" not in result["error_message"]
    assert "token-secret" not in result["error_message"]
    assert "bad-secret" not in result["error_message"]
    assert "[redacted]" in result["error_message"]
    assert calls == [("project-1", drafter.WATSONX_URL_DEFAULT)]


def test_auto_route_invokes_drafter_once_and_sets_draft_response():
    calls = []

    def responder(req, attempt):
        calls.append((req.ticket_id, req.assigned_team, req.sla, attempt))
        return DraftModelCallResult(raw_text=model_json(valid_problem_summary()))

    output, draft = draft_auto_route_response(structured_output(), responder)
    assert draft is not None
    assert draft.validation_status == "valid"
    assert output.draft_response == draft.draft_response
    assert output.draft_response.endswith(
        "Assigned team: Engineering — Support. SLA target: 1 business day."
    )
    assert "Engineering — Support" not in json.loads(model_json(valid_problem_summary()))["problem_summary"]
    assert "1 business day" not in json.loads(model_json(valid_problem_summary()))["problem_summary"]
    assert calls == [("T99", "Engineering — Support", "1 business day", 1)]


@pytest.mark.parametrize(
    "output",
    [
        structured_output(confidence=0.79),
        structured_output(secondary_category="billing"),
        structured_output(urgency=None),
        structured_output(category="account", urgency="critical"),
        build_structured_output(
            TicketIntake(ticket_id="T99", ticket_text="Issue"),
            ClassifierExecutionResult(
                ticket_id="T99",
                classification=None,
                validation_status="invalid_exhausted",
                attempt_count=2,
            ),
        ),
    ],
)
def test_review_paths_never_call_drafter_and_keep_null_draft(output):
    def fail_if_called(req, attempt):
        raise AssertionError("drafter must not be called for review paths")

    result, draft = draft_auto_route_response(output, fail_if_called)
    assert draft is None
    assert result.draft_response is None


def test_prompt_version_hash_model_and_tool_contract_are_stable():
    assert drafter.DRAFT_PROMPT_V1_VERSION == "support-triage-drafter-v1"
    assert drafter.DRAFT_PROMPT_V1_SHA256 == (
        "6affc72421c9a3f1ed23326befff93c6f6f4341e327d78093f638913d510ac23"
    )
    assert hashlib.sha256(drafter.DRAFT_PROMPT_V1.encode("utf-8")).hexdigest() == (
        drafter.DRAFT_PROMPT_V1_SHA256
    )
    assert drafter.DRAFT_PROMPT_V2_VERSION == "support-triage-drafter-v2"
    assert drafter.DRAFT_PROMPT_V2_SHA256 == (
        "69c47e42b7061c23afea7a23b5dc45db0cf3649e2b65482ac9750c6ae8aa948d"
    )
    assert hashlib.sha256(drafter.DRAFT_PROMPT_V2.encode("utf-8")).hexdigest() == (
        drafter.DRAFT_PROMPT_V2_SHA256
    )
    assert drafter.DRAFT_PROMPT_VERSION == "support-triage-drafter-v3"
    assert drafter.DRAFT_PROMPT_SHA256 == (
        "80fc2ccaa4a0f14ec918a6324140b3da074388ab1f1a61d19e16556d9b8ddc23"
    )
    assert hashlib.sha256(drafter.DRAFT_PROMPT.encode("utf-8")).hexdigest() == (
        drafter.DRAFT_PROMPT_SHA256
    )
    assert drafter.DRAFT_REPAIR_INSTRUCTION_V1_VERSION == "support-triage-drafter-repair-v1"
    assert drafter.DRAFT_REPAIR_INSTRUCTION_V1_SHA256 == (
        "f8a5585aa80be9788b9c4de2b19962a3bad8d30e5615a4d70765c5eb4e23d600"
    )
    assert drafter.DRAFT_REPAIR_INSTRUCTION_V2_VERSION == "support-triage-drafter-repair-v2"
    assert drafter.DRAFT_REPAIR_INSTRUCTION_VERSION == "support-triage-drafter-repair-v3"
    assert drafter.MODEL_ID == classifier.MODEL_ID
    assert drafter.DRAFT_MODEL_PARAMS["temperature"] == 0.0
    assert drafter.MAX_DRAFT_ATTEMPTS == 2
    assert draft_support_response.name == "draft_support_response"
    assert draft_support_response.expected_credentials[0].app_id == "watsonx_ai"


def test_drafter_prompt_and_source_do_not_leak_frozen_ticket_fixtures():
    all_ticket_texts = [ticket["text"] for ticket in load_json(SEED_PATH)]
    all_ticket_ids = [f"T{index:02d}" for index in range(1, 31)]
    source = DRAFTER_SOURCE_PATH.read_text(encoding="utf-8")
    prompt_and_source = drafter.DRAFT_PROMPT + "\n" + source
    for forbidden in [*all_ticket_ids, *all_ticket_texts, "expected_category", "expected_urgency"]:
        assert forbidden not in prompt_and_source


def test_manual_draft_review_harness_is_synthetic_and_drafter_only():
    cases = draft_harness.SYNTHETIC_DRAFT_REVIEW_CASES
    assert [case["ticket_id"] for case in cases] == [
        "DRAFT-SMOKE-001",
        "DRAFT-SMOKE-002",
        "DRAFT-SMOKE-003",
        "DRAFT-SMOKE-004",
    ]
    frozen_texts = {ticket["text"] for ticket in load_json(SEED_PATH)}
    assert all(case["ticket_id"] not in [f"T{index:02d}" for index in range(1, 31)] for case in cases)
    assert all(case["ticket_text"] not in frozen_texts for case in cases)

    source = HARNESS_SOURCE_PATH.read_text(encoding="utf-8")
    assert "classify_with_bounded_attempts" not in source
    assert "local_env_classifier" not in source
    assert "support_tickets_ground_truth" not in source
    assert "support_tickets_split" not in source
    assert "held_out_ids" not in source
    assert '"HELD_OUT_CALLS": 0' in source


def test_manual_harness_with_mocked_drafter_reports_zero_classifier_and_held_out_calls():
    calls = []

    def responder(req, attempt):
        calls.append((req.ticket_id, attempt))
        return DraftModelCallResult(
            raw_text=model_json(valid_problem_summary(problem="customer issue"))
        )

    output = draft_harness.run_manual_draft_review_harness(call_model=responder)
    assert output["DRAFT_REVIEW_CASES"] == 4
    assert output["CLASSIFIER_CALLS"] == 0
    assert output["HELD_OUT_CALLS"] == 0
    assert len(calls) == 4
    assert all(result["validation_status"] == "valid" for result in output["results"])


def test_manual_harness_initialization_failure_reports_zero_executed_cases(monkeypatch):
    def fail_initialization():
        raise RuntimeError("init failed token=secret-token Authorization: Bearer auth-secret")

    monkeypatch.setattr(draft_harness, "local_env_drafter", fail_initialization)

    output = draft_harness.run_manual_draft_review_harness()

    assert output["planned_case_count"] == 4
    assert output["executed_case_count"] == 0
    assert output["results"] == []
    assert output["DRAFT_REVIEW_CASES"] == 0
    assert output["CLASSIFIER_CALLS"] == 0
    assert output["HELD_OUT_CALLS"] == 0
    assert output["error_code"] == "DRAFTER_INITIALIZATION_ERROR"
    assert output["final_status"] == "DRAFT_REVIEW_HARNESS=INITIALIZATION_ERROR"
    assert "secret-token" not in output["error_message"]
    assert "auth-secret" not in output["error_message"]
    assert "[redacted]" in output["error_message"]


def test_manual_harness_success_reports_structurally_valid_status():
    def responder(req, attempt):
        return DraftModelCallResult(
            raw_text=model_json(valid_problem_summary(problem="customer issue"))
        )

    output = draft_harness.run_manual_draft_review_harness(call_model=responder)

    assert output["planned_case_count"] == 4
    assert output["executed_case_count"] == 4
    assert output["DRAFT_REVIEW_CASES"] == 4
    assert output["final_status"] == "DRAFT_REVIEW_HARNESS=STRUCTURALLY_VALID"
    assert all(result["validation_status"] == "valid" for result in output["results"])
    assert "MANUAL_REVIEW" not in output


def test_manual_harness_case_failure_reports_structural_invalid_status_without_manual_pass():
    calls = []

    def responder(req, attempt):
        calls.append((req.ticket_id, attempt))
        if req.ticket_id == "DRAFT-SMOKE-002":
            raise RuntimeError("model host unavailable")
        return DraftModelCallResult(
            raw_text=model_json(valid_problem_summary(problem="customer issue"))
        )

    output = draft_harness.run_manual_draft_review_harness(call_model=responder)

    assert output["planned_case_count"] == 4
    assert output["executed_case_count"] == 4
    assert output["DRAFT_REVIEW_CASES"] == 4
    assert output["final_status"] == "DRAFT_REVIEW_HARNESS=EXECUTION_INVALID"
    assert [call for call in calls if call[0] == "DRAFT-SMOKE-002"] == [("DRAFT-SMOKE-002", 1)]
    assert any(result["validation_status"] == "execution_error" for result in output["results"])
    assert "MANUAL_REVIEW" not in output


def test_manual_harness_cli_returns_zero_only_for_structurally_valid_status(monkeypatch, capsys):
    monkeypatch.setattr(
        draft_harness,
        "run_manual_draft_review_harness",
        lambda: {"final_status": "DRAFT_REVIEW_HARNESS=STRUCTURALLY_VALID"},
    )
    monkeypatch.setattr("sys.argv", ["run_support_triage_draft_review.py", "--smoke-real-drafter"])

    assert draft_harness.main() == 0
    assert "STRUCTURALLY_VALID" in capsys.readouterr().out


@pytest.mark.parametrize(
    "final_status",
    [
        "DRAFT_REVIEW_HARNESS=INITIALIZATION_ERROR",
        "DRAFT_REVIEW_HARNESS=EXECUTION_INVALID",
    ],
)
def test_manual_harness_cli_returns_nonzero_for_non_structural_success(
    final_status, monkeypatch, capsys
):
    monkeypatch.setattr(
        draft_harness,
        "run_manual_draft_review_harness",
        lambda: {"final_status": final_status},
    )
    monkeypatch.setattr("sys.argv", ["run_support_triage_draft_review.py", "--smoke-real-drafter"])

    assert draft_harness.main() == 1
    assert final_status in capsys.readouterr().out
