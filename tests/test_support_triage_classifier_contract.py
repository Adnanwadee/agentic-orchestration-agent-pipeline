import json
import inspect
from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts import run_support_triage_dev_eval as dev_runner
from scripts.run_support_triage_dev_eval import dry_run, compute_metrics, load_development_records
from tools import support_triage_classifier as classifier
from tools.support_triage_classifier import (
    ClassificationResult,
    ClassificationOutputValidationError,
    ClassifierExecutionResult,
    ModelCallResult,
    StructuredTicketOutput,
    TicketIntake,
    build_classifier_messages,
    build_structured_output,
    classify_support_ticket,
    classify_with_bounded_attempts,
    evaluate_pre_routing_review,
    parse_classification_response,
)


ROOT = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT / "data" / "support_tickets_seed.json"
GROUND_TRUTH_PATH = ROOT / "data" / "support_tickets_ground_truth.json"
SPLIT_PATH = ROOT / "data" / "support_tickets_split.json"
FREEZE_MANIFEST_PATH = ROOT / "data" / "support_tickets_freeze_manifest.json"
CLASSIFIER_SOURCE_PATH = ROOT / "tools" / "support_triage_classifier.py"
DEV_RUNNER_SOURCE_PATH = ROOT / "scripts" / "run_support_triage_dev_eval.py"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def ticket_text(ticket_id):
    return {ticket["id"]: ticket["text"] for ticket in load_json(SEED_PATH)}[ticket_id]


def label(ticket_id):
    return {
        record["ticket_id"]: (
            record["expected_category"],
            record["expected_secondary_category"],
            record["expected_urgency"],
        )
        for record in load_json(GROUND_TRUTH_PATH)
    }[ticket_id]


def valid_payload(**overrides):
    payload = {
        "category": "technical",
        "secondary_category": None,
        "urgency": "medium",
        "confidence": 0.75,
        "reasoning": "A technical product issue is described.",
    }
    payload.update(overrides)
    return payload


def test_intake_schema_is_strict():
    assert TicketIntake(ticket_id="T99", ticket_text="A real issue").ticket_id == "T99"
    with pytest.raises(ValidationError):
        TicketIntake(ticket_id="", ticket_text="A real issue")
    with pytest.raises(ValidationError):
        TicketIntake(ticket_id="T99", ticket_text="   ")
    with pytest.raises(ValidationError):
        TicketIntake(ticket_id="T99", ticket_text="A real issue", extra_field=True)


@pytest.mark.parametrize("category", ["billing", "technical", "account", "general"])
def test_classification_accepts_closed_categories(category):
    result = ClassificationResult.model_validate(valid_payload(category=category))
    assert result.category == category


@pytest.mark.parametrize("urgency", ["low", "medium", "high", "critical", None])
def test_classification_accepts_true_urgency_values(urgency):
    result = ClassificationResult.model_validate(valid_payload(urgency=urgency))
    assert result.urgency == urgency


@pytest.mark.parametrize(
    "payload",
    [
        valid_payload(category="sales"),
        valid_payload(urgency="unknown"),
        valid_payload(urgency="null"),
        valid_payload(confidence=-0.01),
        valid_payload(confidence=1.01),
        valid_payload(reasoning=""),
        {k: v for k, v in valid_payload().items() if k != "reasoning"},
        valid_payload(review_required=True),
        valid_payload(category="billing", secondary_category="billing"),
    ],
)
def test_classification_rejects_invalid_payloads(payload):
    with pytest.raises(ValidationError):
        ClassificationResult.model_validate(payload)


@pytest.mark.parametrize("confidence", [0.0, 1.0])
def test_classification_accepts_confidence_boundaries(confidence):
    assert ClassificationResult.model_validate(valid_payload(confidence=confidence)).confidence == confidence


def test_raw_output_parsing():
    valid = json.dumps(valid_payload())
    assert parse_classification_response(valid).category == "technical"

    for raw in [
        "not json",
        json.dumps(["not", "an", "object"]),
        json.dumps({k: v for k, v in valid_payload().items() if k != "category"}),
        json.dumps(valid_payload(extra_key=True)),
    ]:
        with pytest.raises(ClassificationOutputValidationError):
            parse_classification_response(raw)


def test_retry_policy_valid_first_response_uses_one_attempt():
    calls = []

    def responder(ticket, attempt):
        calls.append((ticket.ticket_id, attempt))
        return ModelCallResult(raw_text=json.dumps(valid_payload()))

    result = classify_with_bounded_attempts(
        TicketIntake(ticket_id="T99", ticket_text="Issue"),
        responder,
    )
    assert result.validation_status == "valid"
    assert result.attempt_count == 1
    assert calls == [("T99", 1)]


def test_retry_policy_invalid_then_valid_uses_two_attempts():
    calls = []

    def responder(ticket, attempt):
        calls.append(attempt)
        if attempt == 1:
            return ModelCallResult(raw_text="{bad json")
        return ModelCallResult(raw_text=json.dumps(valid_payload()))

    result = classify_with_bounded_attempts(
        TicketIntake(ticket_id="T99", ticket_text="Issue"),
        responder,
    )
    assert result.validation_status == "valid"
    assert result.attempt_count == 2
    assert calls == [1, 2]


def test_execution_error_on_first_attempt_does_not_retry():
    calls = []

    def responder(ticket, attempt):
        calls.append(attempt)
        raise RuntimeError("auth failed")

    result = classify_with_bounded_attempts(
        TicketIntake(ticket_id="T99", ticket_text="Issue"),
        responder,
    )
    assert result.validation_status == "execution_error"
    assert result.classification is None
    assert result.attempt_count == 1
    assert result.error_code == "CLASSIFIER_EXECUTION_ERROR"
    assert result.token_usage is None
    assert calls == [1]


def test_invalid_then_execution_error_is_execution_error():
    calls = []

    def responder(ticket, attempt):
        calls.append(attempt)
        if attempt == 1:
            return ModelCallResult(
                raw_text="{bad json",
                latency_seconds=0.25,
                token_usage={"prompt_tokens": 4, "completion_tokens": 2, "total_tokens": 6},
            )
        raise RuntimeError("network failed")

    result = classify_with_bounded_attempts(
        TicketIntake(ticket_id="T99", ticket_text="Issue"),
        responder,
    )
    assert result.validation_status == "execution_error"
    assert result.attempt_count == 2
    assert result.error_code == "CLASSIFIER_EXECUTION_ERROR"
    assert result.token_usage == {"prompt_tokens": 4, "completion_tokens": 2, "total_tokens": 6}
    assert calls == [1, 2]


def test_invalid_then_execution_error_latency_uses_whole_operation(monkeypatch):
    calls = []
    perf_counter_values = iter([10.0, 11.2])

    monkeypatch.setattr(classifier.time, "perf_counter", lambda: next(perf_counter_values))

    def responder(ticket, attempt):
        calls.append(attempt)
        if attempt == 1:
            return ModelCallResult(
                raw_text="{bad json",
                latency_seconds=0.3,
                token_usage={"prompt_tokens": 4, "completion_tokens": 2, "total_tokens": 6},
            )
        raise RuntimeError("network failed after waiting")

    result = classify_with_bounded_attempts(
        TicketIntake(ticket_id="T99", ticket_text="Issue"),
        responder,
    )
    assert result.validation_status == "execution_error"
    assert result.attempt_count == 2
    assert result.latency_seconds == pytest.approx(1.2)
    assert result.token_usage == {"prompt_tokens": 4, "completion_tokens": 2, "total_tokens": 6}
    assert calls == [1, 2]


def test_retry_policy_exhausts_after_two_attempts():
    calls = []

    def responder(ticket, attempt):
        calls.append(attempt)
        return ModelCallResult(raw_text="{bad json")

    result = classify_with_bounded_attempts(
        TicketIntake(ticket_id="T99", ticket_text="Issue"),
        responder,
    )
    assert result.validation_status == "invalid_exhausted"
    assert result.classification is None
    assert result.attempt_count == classifier.MAX_CLASSIFIER_ATTEMPTS == 2
    assert calls == [1, 2]


def test_attempt_messages_add_repair_instruction_only_on_second_attempt():
    sample_ticket_text = "The same original ticket text."
    first = build_classifier_messages(sample_ticket_text, attempt=1)
    second = build_classifier_messages(sample_ticket_text, attempt=2)

    assert classifier.CLASSIFIER_REPAIR_INSTRUCTION not in [message["content"] for message in first]
    assert classifier.CLASSIFIER_REPAIR_INSTRUCTION in [message["content"] for message in second]
    assert first[-1]["content"] == second[-1]["content"] == f"Ticket text:\n{sample_ticket_text}"
    assert classifier.CLASSIFIER_PROMPT in [message["content"] for message in first]
    assert classifier.CLASSIFIER_PROMPT in [message["content"] for message in second]
    for forbidden in ["T09", "T10", "T21", ticket_text("T09"), ticket_text("T10"), ticket_text("T21")]:
        assert forbidden not in classifier.CLASSIFIER_REPAIR_INSTRUCTION


def test_multi_attempt_telemetry_is_aggregated():
    calls = []

    def responder(ticket, attempt):
        calls.append(attempt)
        if attempt == 1:
            return ModelCallResult(
                raw_text="{bad json",
                latency_seconds=0.3,
                token_usage={"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
            )
        return ModelCallResult(
            raw_text=json.dumps(valid_payload()),
            latency_seconds=0.7,
            token_usage={"prompt_tokens": 11, "completion_tokens": 5, "total_tokens": 16},
        )

    result = classify_with_bounded_attempts(
        TicketIntake(ticket_id="T99", ticket_text="Issue"),
        responder,
    )
    assert result.validation_status == "valid"
    assert result.attempt_count == 2
    assert result.latency_seconds == pytest.approx(1.0)
    assert result.token_usage == {
        "prompt_tokens": 21,
        "completion_tokens": 7,
        "total_tokens": 28,
    }
    assert calls == [1, 2]


def execution(**overrides):
    classification = ClassificationResult.model_validate(valid_payload(**overrides))
    return ClassifierExecutionResult(
        ticket_id="T99",
        classification=classification,
        validation_status="valid",
        attempt_count=1,
    )


SUPPORTED_ROUTE_EXPECTATIONS = [
    ("billing", "critical", "Billing — Senior", "1 hour"),
    ("billing", "high", "Billing — Standard", "4 hours"),
    ("billing", "medium", "Billing — Standard", "1 business day"),
    ("billing", "low", "Billing — Standard", "3 business days"),
    ("technical", "critical", "Engineering — On-call", "30 minutes"),
    ("technical", "high", "Engineering — Support", "2 hours"),
    ("technical", "medium", "Engineering — Support", "1 business day"),
    ("technical", "low", "Engineering — Backlog", "5 business days"),
    ("account", "high", "Customer Success", "4 hours"),
    ("account", "medium", "Customer Success", "1 business day"),
    ("account", "low", "Customer Success", "3 business days"),
    ("general", "critical", "Customer Success", "2 business days"),
    ("general", "high", "Customer Success", "2 business days"),
    ("general", "medium", "Customer Success", "2 business days"),
    ("general", "low", "Customer Success", "2 business days"),
]


def test_pre_routing_review_uses_frozen_confidence_threshold_behavior():
    assert classifier.CONFIDENCE_THRESHOLD == 0.80
    assert evaluate_pre_routing_review(
        execution(confidence=0.79)
    ) == (True, ["confidence_below_threshold"])
    assert evaluate_pre_routing_review(
        execution(confidence=0.80)
    ) == (False, [])
    assert evaluate_pre_routing_review(
        execution(confidence=0.81)
    ) == (False, [])


def test_frozen_confidence_threshold_is_not_externally_overridable():
    source = CLASSIFIER_SOURCE_PATH.read_text(encoding="utf-8")
    assert "confidence_threshold" not in inspect.signature(evaluate_pre_routing_review).parameters
    assert "confidence_threshold" not in inspect.signature(build_structured_output).parameters
    assert source.count("CONFIDENCE_THRESHOLD = 0.80") == 1
    assert "os.environ.get(\"CONFIDENCE_THRESHOLD" not in source
    assert "os.environ.get('CONFIDENCE_THRESHOLD" not in source


def test_pre_routing_review_policy_triggers_and_order():
    result = evaluate_pre_routing_review(
        execution(secondary_category="billing", urgency=None, confidence=0.20)
    )
    assert result == (
        True,
        ["confidence_below_threshold", "secondary_category_present", "urgency_null"],
    )

    invalid = ClassifierExecutionResult(
        ticket_id="T99",
        classification=None,
        validation_status="invalid_exhausted",
        attempt_count=2,
    )
    assert evaluate_pre_routing_review(invalid) == (
        True,
        ["invalid_classification_output"],
    )


@pytest.mark.parametrize(
    ("overrides", "expected_reasons"),
    [
        (
            {"confidence": 0.79, "secondary_category": "billing"},
            ["confidence_below_threshold", "secondary_category_present"],
        ),
        (
            {"confidence": 0.79, "urgency": None},
            ["confidence_below_threshold", "urgency_null"],
        ),
        (
            {"secondary_category": "billing", "urgency": None, "confidence": 0.90},
            ["secondary_category_present", "urgency_null"],
        ),
        (
            {"category": "account", "urgency": "critical", "confidence": 0.79},
            ["confidence_below_threshold", "unsupported_route"],
        ),
        (
            {
                "category": "account",
                "secondary_category": "billing",
                "urgency": "critical",
                "confidence": 0.90,
            },
            ["secondary_category_present", "unsupported_route"],
        ),
    ],
)
def test_pre_routing_review_composes_valid_classification_triggers(overrides, expected_reasons):
    assert evaluate_pre_routing_review(execution(**overrides)) == (True, expected_reasons)


@pytest.mark.parametrize(
    ("category", "urgency", "assigned_team", "sla"),
    SUPPORTED_ROUTE_EXPECTATIONS,
)
def test_authoritative_routing_table_covers_all_supported_combinations(
    category, urgency, assigned_team, sla
):
    assert len(classifier.AUTHORITATIVE_ROUTING_TABLE) == 15

    route = classifier.lookup_authoritative_route(category, urgency)
    assert route is not None
    assert route.assigned_team == assigned_team
    assert route.sla == sla

    output = build_structured_output(
        TicketIntake(ticket_id="T99", ticket_text="Issue"),
        execution(category=category, urgency=urgency, confidence=0.90),
    )
    assert output.review_required is False
    assert output.review_reasons == []
    assert output.assigned_team == assigned_team
    assert output.sla == sla
    assert output.draft_response is None
    assert output.status == "auto_route_pending"


def test_authoritative_route_lookup_is_case_normalized_and_fails_safely():
    route = classifier.lookup_authoritative_route(" Technical ", " HIGH ")
    assert route is not None
    assert route.assigned_team == "Engineering — Support"
    assert route.sla == "2 hours"

    assert classifier.lookup_authoritative_route("account", "critical") is None
    assert classifier.lookup_authoritative_route("sales", "high") is None
    assert classifier.lookup_authoritative_route("billing", None) is None


def test_all_sixteen_valid_taxonomy_pairs_are_accounted_for():
    pairs = {
        (category, urgency)
        for category in ["billing", "technical", "account", "general"]
        for urgency in ["low", "medium", "high", "critical"]
    }
    supported = set(classifier.AUTHORITATIVE_ROUTING_TABLE)
    assert supported == pairs - {("account", "critical")}
    assert ("account", "critical") not in supported


def test_structured_output_supports_review_and_invalid_paths():
    ticket = TicketIntake(ticket_id="T99", ticket_text="Issue")
    reviewed = build_structured_output(
        ticket,
        execution(urgency=None, confidence=0.90),
    )
    assert isinstance(reviewed, StructuredTicketOutput)
    assert reviewed.review_required is True
    assert reviewed.review_reasons == ["urgency_null"]
    assert reviewed.assigned_team == "Triage — Human"
    assert reviewed.sla == "Immediate"
    assert reviewed.draft_response is None
    assert reviewed.status == "human_review"

    invalid = build_structured_output(
        ticket,
        ClassifierExecutionResult(
            ticket_id="T99",
            classification=None,
            validation_status="invalid_exhausted",
            attempt_count=2,
        ),
    )
    assert invalid.status == "invalid_output"
    assert invalid.classification_valid is False
    assert invalid.review_required is True
    assert invalid.review_reasons == ["invalid_classification_output"]
    assert invalid.assigned_team == "Triage — Human"
    assert invalid.sla == "Immediate"
    assert invalid.draft_response is None


def test_secondary_category_review_precedes_supported_business_routing():
    output = build_structured_output(
        TicketIntake(ticket_id="T09", ticket_text="Issue"),
        execution(
            category="account",
            secondary_category="billing",
            urgency="medium",
            confidence=0.90,
        ),
    )
    assert output.review_required is True
    assert output.review_reasons == ["secondary_category_present"]
    assert output.assigned_team == "Triage — Human"
    assert output.sla == "Immediate"
    assert output.draft_response is None
    assert output.status == "human_review"


def test_null_urgency_review_precedes_business_routing():
    output = build_structured_output(
        TicketIntake(ticket_id="T10", ticket_text="it doesnt work fix it"),
        execution(category="technical", urgency=None, confidence=0.50),
    )
    assert output.review_required is True
    assert output.review_reasons == ["confidence_below_threshold", "urgency_null"]
    assert output.assigned_team == "Triage — Human"
    assert output.sla == "Immediate"
    assert output.draft_response is None
    assert output.status == "human_review"


def test_account_critical_is_unsupported_and_routes_to_human_review():
    output = build_structured_output(
        TicketIntake(ticket_id="T99", ticket_text="Issue"),
        execution(category="account", urgency="critical", confidence=0.90),
    )
    assert output.review_required is True
    assert output.review_reasons == ["unsupported_route"]
    assert output.assigned_team == "Triage — Human"
    assert output.sla == "Immediate"
    assert output.draft_response is None
    assert output.status == "human_review"


def test_t09_t10_t21_frozen_contracts_and_review_triggers():
    expected = {
        "T09": ("account", "billing", "medium", 0.90, ["secondary_category_present"]),
        "T10": (
            "technical",
            None,
            None,
            0.50,
            ["confidence_below_threshold", "urgency_null"],
        ),
        "T21": ("technical", None, None, 0.90, ["urgency_null"]),
    }
    for ticket_id, (category, secondary, urgency, confidence, reasons) in expected.items():
        assert label(ticket_id) == (category, secondary, urgency)
        payload = valid_payload(
            category=category,
            secondary_category=secondary,
            urgency=urgency,
            confidence=confidence,
            reasoning="Frozen fixture classification for local contract validation.",
        )
        execution_result = ClassifierExecutionResult(
            ticket_id=ticket_id,
            classification=ClassificationResult.model_validate(payload),
            validation_status="valid",
            attempt_count=1,
        )
        assert evaluate_pre_routing_review(execution_result) == (True, reasons)
        output = build_structured_output(
            TicketIntake(ticket_id=ticket_id, ticket_text=ticket_text(ticket_id)),
            execution_result,
        )
        assert output.assigned_team == "Triage — Human"
        assert output.sla == "Immediate"
        assert output.draft_response is None
    assert ticket_text("T10") == "it doesnt work fix it"
    assert ticket_text("T21") == "Something looks wrong in my workspace."


def test_tool_static_readiness_and_model_config():
    assert classifier.MODEL_ID == "meta-llama/llama-4-maverick-17b-128e-instruct-fp8"
    assert classifier.ORCHESTRATE_MODEL_ID == (
        "watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8"
    )
    assert classifier.CONFIDENCE_THRESHOLD == 0.80
    assert classifier.MODEL_PARAMS["temperature"] == 0.0
    assert classifier.MODEL_PARAMS["max_tokens"] == 300
    assert classifier.MAX_CLASSIFIER_ATTEMPTS == 2
    assert classify_support_ticket.name == "classify_support_ticket"
    assert classify_support_ticket.expected_credentials[0].app_id == "watsonx_ai"
    assert str(classify_support_ticket.expected_credentials[0].type) == "api_key_auth"


def test_prompt_contract_and_no_fixture_leakage():
    prompt = classifier.CLASSIFIER_PROMPT
    all_ticket_texts = [ticket["text"] for ticket in load_json(SEED_PATH)]
    all_ticket_ids = [f"T{index:02d}" for index in range(1, 31)]

    assert classifier.INITIAL_CLASSIFIER_PROMPT_VERSION == "support-triage-classifier-v1"
    assert classifier.INITIAL_CLASSIFIER_PROMPT_SHA256 == (
        "5ae597bc3fe6af83df93c3b29f062a770186f5281ca27d1a046bd8e4ec689210"
    )
    assert classifier.CLASSIFIER_PROMPT_VERSION == "support-triage-classifier-v2"
    assert classifier.CLASSIFIER_PROMPT_SHA256 == (
        "a78f13a71cb344429502ca2aeb0b36281608cfbea6c45c6bb509b678e3d3e9b6"
    )
    assert classifier.CLASSIFIER_REPAIR_INSTRUCTION_VERSION == (
        "support-triage-classifier-repair-v1"
    )
    assert classifier.CLASSIFIER_REPAIR_INSTRUCTION_SHA256 == (
        "b55bf893bba9e0373d70a4f839741b46ebacd82c1da94b622377b465e052b39b"
    )
    assert classifier.CLASSIFIER_REPAIR_INSTRUCTION != classifier.INITIAL_CLASSIFIER_PROMPT
    assert classifier.CLASSIFIER_PROMPT != classifier.INITIAL_CLASSIFIER_PROMPT
    for required in [
        "billing",
        "technical",
        "account",
        "general",
        "secondary_category",
        "urgency null",
        "confidence",
        "Return raw JSON only",
        "Do not decide review_required",
    ]:
        assert required in prompt
    for forbidden in [*all_ticket_ids, *all_ticket_texts, "expected_category", "expected_urgency"]:
        assert forbidden not in prompt


def test_v2_prompt_contains_generic_taxonomy_and_urgency_calibration():
    prompt = classifier.CLASSIFIER_PROMPT
    for required in [
        "pricing",
        "discounts",
        "malfunction",
        "errors",
        "profile/settings",
        "account administration",
        "general: support requests or information that do not materially belong",
        "multiple users or a team",
        "business-critical operation where work cannot proceed",
        "time-sensitive",
        "same-day/near-term",
        "active problem or requested operational/account/billing change",
        "no evidence of critical/high severity",
        "informational/how-to/general inquiry",
        "no-rush/not-urgent",
        "too little evidence to safely infer urgency",
        "Do not infer critical merely from emotional language",
        "Do not infer high solely because a customer wants an issue fixed",
        "Do not default vague or low-information tickets to medium urgency",
    ]:
        assert required in prompt


def test_production_classifier_source_does_not_read_frozen_labels_or_split():
    source = CLASSIFIER_SOURCE_PATH.read_text(encoding="utf-8")
    forbidden = [
        "support_tickets_ground_truth",
        "support_tickets_split",
        "support_tickets_seed",
        "expected_category",
        "expected_urgency",
    ]
    forbidden.extend(f"T{index:02d}" for index in range(1, 31))
    forbidden.extend(ticket["text"] for ticket in load_json(SEED_PATH))
    for value in forbidden:
        assert value not in source


def test_dev_runner_dry_run_uses_exact_dev_ids_and_excludes_held_out():
    dry = dry_run()
    split = load_json(SPLIT_PATH)
    assert dry["mode"] == "dry_run"
    assert dry["real_classifier_calls"] == 0
    assert dry["development_ids"] == split["development_ids"]
    assert dry["held_out_ids_excluded"] is True
    for held_out_id in split["held_out_ids"]:
        assert held_out_id not in dry["development_ids"]

    runner_source = DEV_RUNNER_SOURCE_PATH.read_text(encoding="utf-8")
    assert "--split" not in runner_source
    assert "heldout" not in runner_source.lower()


def test_smoke_uses_synthetic_ticket_no_data_load_no_artifact(monkeypatch, tmp_path):
    def fail_if_loaded():
        raise AssertionError("DEV data loader must not run during smoke")

    calls = []

    def responder(ticket, attempt):
        calls.append((ticket.ticket_id, ticket.ticket_text, attempt))
        return ModelCallResult(raw_text=json.dumps(valid_payload()), latency_seconds=0.1)

    monkeypatch.setattr(dev_runner, "load_development_records", fail_if_loaded)
    output = dev_runner.run_smoke(call_model=responder)

    assert output["smoke_ticket_id"] == "SMOKE-INFRA-001"
    assert output["smoke_ticket_text"] == "The demo settings page shows an error when I click Save."
    assert output["smoke_ticket_id"] not in [f"T{index:02d}" for index in range(1, 31)]
    assert output["validation_status"] == "valid"
    assert output["attempt_count"] == 1
    assert output["final_status"] == "SMOKE_CLASSIFIER_INTEGRATION=PASS"
    assert calls == [
        (
            "SMOKE-INFRA-001",
            "The demo settings page shows an error when I click Save.",
            1,
        )
    ]
    assert not any(tmp_path.iterdir())


def test_smoke_allows_one_repair_and_stops_on_execution_error():
    invalid_then_valid_calls = []

    def invalid_then_valid(ticket, attempt):
        invalid_then_valid_calls.append(attempt)
        if attempt == 1:
            return ModelCallResult(raw_text="{bad json")
        return ModelCallResult(raw_text=json.dumps(valid_payload()))

    repaired = dev_runner.run_smoke(call_model=invalid_then_valid)
    assert repaired["validation_status"] == "valid"
    assert repaired["attempt_count"] == 2
    assert invalid_then_valid_calls == [1, 2]

    execution_calls = []

    def execution_error(ticket, attempt):
        execution_calls.append(attempt)
        raise RuntimeError("sdk failed")

    failed = dev_runner.run_smoke(call_model=execution_error)
    assert failed["validation_status"] == "execution_error"
    assert failed["attempt_count"] == 1
    assert failed["final_status"] == "SMOKE_CLASSIFIER_INTEGRATION=EXECUTION_ERROR"
    assert execution_calls == [1]


def test_smoke_initialization_failure_returns_structured_execution_error(monkeypatch):
    perf_counter_values = iter([20.0, 20.4])

    monkeypatch.setattr(dev_runner.time, "perf_counter", lambda: next(perf_counter_values))

    def init_failure():
        raise RuntimeError("connect failed")

    monkeypatch.setattr(dev_runner, "local_env_classifier", init_failure)

    output = dev_runner.run_smoke()

    assert output["validation_status"] == "execution_error"
    assert output["attempt_count"] == 0
    assert output["classification"] is None
    assert output["token_usage"] is None
    assert output["error_code"] == "CLASSIFIER_INITIALIZATION_ERROR"
    assert output["error_type"] == "RuntimeError"
    assert output["error_message"] == "connect failed"
    assert output["latency_seconds"] == pytest.approx(0.4)
    assert output["final_status"] == "SMOKE_CLASSIFIER_INTEGRATION=EXECUTION_ERROR"


def test_dev_runner_rejects_initialization_error_without_scoring(monkeypatch, tmp_path):
    def init_failure():
        raise RuntimeError("remote host closed connection")

    def fail_if_called(ticket, call_model):
        raise AssertionError("no DEV ticket should be classified after initialization failure")

    monkeypatch.setattr(dev_runner, "local_env_classifier", init_failure)
    monkeypatch.setattr(dev_runner, "classify_with_bounded_attempts", fail_if_called)

    with pytest.raises(SystemExit) as exc_info:
        dev_runner.execute_development_evaluation(output_root=tmp_path)

    message = str(exc_info.value)
    assert "DEV_EVALUATION_INVALID_INITIALIZATION_ERROR" in message
    assert '"scored": false' in message
    assert '"dev_tickets_executed": 0' in message
    assert '"error_code": "CLASSIFIER_INITIALIZATION_ERROR"' in message
    assert '"error_type": "RuntimeError"' in message
    assert "remote host closed connection" in message
    assert not list(tmp_path.rglob("development_results.json"))


def test_dev_runner_rejects_execution_error_without_scoring(monkeypatch, tmp_path):
    def fake_classifier():
        def responder(ticket, attempt):
            if ticket.ticket_id == "T03":
                raise RuntimeError("project config failed")
            return ModelCallResult(raw_text=json.dumps(valid_payload()))

        return responder

    monkeypatch.setattr(dev_runner, "local_env_classifier", fake_classifier)
    with pytest.raises(SystemExit) as exc_info:
        dev_runner.execute_development_evaluation(output_root=tmp_path)

    message = str(exc_info.value)
    assert "DEV_EVALUATION_INVALID_EXECUTION_ERROR" in message
    assert '"scored": false' in message
    assert '"failed_ticket_id": "T03"' in message
    assert not list(tmp_path.rglob("development_results.json"))


def test_metric_rules_exclude_null_urgency_and_report_null_cases():
    records, ground_truth, _ = load_development_records()
    results = []
    for record in records:
        gt = record["ground_truth"]
        predicted_urgency = gt["expected_urgency"]
        if record["ticket_id"] == "T01":
            predicted_urgency = "low"
        results.append(
            {
                "ticket_id": record["ticket_id"],
                "validation_status": "valid",
                "classification": {
                    "category": gt["expected_category"],
                    "secondary_category": gt["expected_secondary_category"],
                    "urgency": predicted_urgency,
                    "confidence": 0.90,
                    "reasoning": "mock result",
                },
            }
        )

    metrics = compute_metrics(results, ground_truth)
    assert metrics["category_denominator"] == 15
    assert metrics["category_correct"] == 15
    assert metrics["urgency_denominator"] == 13
    assert metrics["urgency_correct"] == 12
    assert [item["ticket_id"] for item in metrics["null_urgency_handling"]] == ["T10", "T21"]
    assert all(item["null_urgency_match"] is True for item in metrics["null_urgency_handling"])
    assert metrics["explicit_ticket_reports"]["T09"]["ticket_id"] == "T09"
    assert metrics["explicit_ticket_reports"]["T10"]["ticket_id"] == "T10"
    assert metrics["explicit_ticket_reports"]["T21"]["ticket_id"] == "T21"


def test_null_urgency_reporting_distinguishes_absent_classification():
    _, ground_truth, _ = load_development_records()
    results = [
        {
            "ticket_id": "T10",
            "validation_status": "invalid_exhausted",
            "classification": None,
        },
        {
            "ticket_id": "T21",
            "validation_status": "valid",
            "classification": valid_payload(urgency=None),
        },
    ]
    metrics = compute_metrics(results, ground_truth)
    by_id = {item["ticket_id"]: item for item in metrics["null_urgency_handling"]}
    assert by_id["T10"]["classification_present"] is False
    assert by_id["T10"]["null_urgency_match"] is False
    assert by_id["T21"]["classification_present"] is True
    assert by_id["T21"]["null_urgency_match"] is True
