import ast
import base64
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest
from pydantic import ValidationError


FLOW_PATH = Path("flows/support_triage_flow.py")
CLASSIFIER_PATH = Path("tools/support_triage_classifier.py")
DRAFTER_PATH = Path("tools/support_triage_drafter.py")

PUBLIC_INPUT_FIELDS = {"ticket_id", "ticket_text"}
FLOW_NODES = {
    "__start__",
    "__end__",
    "classify_support_ticket",
    "apply_support_triage_policy",
    "drafting_branch",
    "draft_support_response",
    "finalize_drafted_record",
    "finalize_skipped_record",
}
AUTO_ROUTE_EXPRESSION = "flow.apply_support_triage_policy.output.status == 'auto_route_pending'"


def future_dummy_jwt():
    header = {"alg": "none", "typ": "JWT"}
    payload = {"exp": int(time.time()) + 3600}

    def enc(data):
        return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")

    return f"{enc(header)}.{enc(payload)}.{enc({'sig': 'local-only'})}"


def install_local_orchestrate_config(tmp_path, monkeypatch):
    home = tmp_path / "home"
    config_dir = home / ".config" / "orchestrate"
    auth_dir = home / ".cache" / "orchestrate"
    config_dir.mkdir(parents=True)
    auth_dir.mkdir(parents=True)
    (config_dir / "config.yaml").write_text(
        "context:\n"
        "  active_environment: local\n"
        "environments:\n"
        "  local:\n"
        "    wxo_url: http://localhost:4321\n",
        encoding="utf-8",
    )
    (auth_dir / "credentials.yaml").write_text(
        "auth:\n"
        "  local:\n"
        f"    wxo_mcsp_token: {future_dummy_jwt()}\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("HOME", str(home))
    for name in list(sys.modules):
        if name.startswith("ibm_watsonx_orchestrate.flow_builder") or name.startswith(
            "ibm_watsonx_orchestrate_clients.common"
        ):
            sys.modules.pop(name)
        if name == "ibm_watsonx_orchestrate_core.utils.config":
            sys.modules.pop(name)
        if name == "flows.support_triage_flow":
            sys.modules.pop(name)


def data_map(mapping):
    if mapping is None:
        return {}
    return {
        item["target_variable"]: item["value_expression"]
        for item in mapping.model_dump()["spec"]["maps"]
    }


def model_data_map(mapping):
    if mapping is None:
        return {}
    return {
        item["target_variable"]: item["value_expression"]
        for item in mapping["spec"]["maps"]
    }


def regular_edges(graph):
    return {(edge.start, edge.end) for edge in graph.edges}


def branch_conditions(branch):
    conditions = branch.spec.evaluator.to_json()["conditions"]
    return [
        {"expression": condition.get("expression"), **condition, "metadata": None}
        for condition in conditions
    ]


def function_arg_names(source_path, function_name):
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return [arg.arg for arg in node.args.args]
    raise AssertionError(f"{function_name} not found")


def omit_transport_nulls(value):
    if isinstance(value, dict):
        return {
            key: omit_transport_nulls(item)
            for key, item in value.items()
            if item is not None
        }
    if isinstance(value, list):
        return [omit_transport_nulls(item) for item in value]
    return value


def tool_content(result):
    return result.content if hasattr(result, "content") else result


def classifier_execution_payload(
    *,
    classification=None,
    validation_status="valid",
    attempt_count=1,
):
    from tools.support_triage_classifier import ClassificationResult, ClassifierExecutionResult

    if classification is None and validation_status == "valid":
        classification = ClassificationResult(
            category="technical",
            secondary_category=None,
            urgency="medium",
            confidence=0.9,
            reasoning="The ticket describes a product issue.",
        )
    return ClassifierExecutionResult(
        ticket_id="REMOTE-LIKE-001",
        classification=classification,
        validation_status=validation_status,
        attempt_count=attempt_count,
        error_code="CLASSIFICATION_INVALID_EXHAUSTED"
        if validation_status == "invalid_exhausted"
        else ("CLASSIFIER_EXECUTION_ERROR" if validation_status == "execution_error" else None),
        error_message="classifier did not return a valid result"
        if validation_status != "valid"
        else None,
    ).model_dump()


def draft_execution_payload(validation_status="valid"):
    from tools.support_triage_drafter import DraftExecutionResult

    return DraftExecutionResult(
        ticket_id="REMOTE-LIKE-001",
        draft_response="Thank you for reaching out about the export failure.\n\n"
        "Assigned team: Engineering \u2014 Support. SLA target: 1 business day."
        if validation_status == "valid"
        else None,
        validation_status=validation_status,
        attempt_count=1,
        error_code="DRAFT_EXECUTION_ERROR" if validation_status == "execution_error" else None,
        error_message="drafter failed" if validation_status == "execution_error" else None,
    ).model_dump()


def test_public_flow_schema_exposes_only_ticket_intake_fields(tmp_path, monkeypatch):
    install_local_orchestrate_config(tmp_path, monkeypatch)
    flow_module = importlib.import_module("flows.support_triage_flow")

    assert set(flow_module.SupportTriageInput.model_fields) == PUBLIC_INPUT_FIELDS
    forbidden_inputs = {
        "classification",
        "category",
        "urgency",
        "confidence",
        "assigned_team",
        "sla",
        "threshold",
        "wx_project_id",
        "wx_url",
        "api_key",
    }
    assert forbidden_inputs.isdisjoint(flow_module.SupportTriageInput.model_fields)


def test_top_level_graph_runs_drafter_only_on_auto_route_branch(tmp_path, monkeypatch):
    install_local_orchestrate_config(tmp_path, monkeypatch)
    flow_module = importlib.import_module("flows.support_triage_flow")
    built_flow = flow_module.build_support_triage_flow()

    assert set(built_flow.nodes) == FLOW_NODES
    assert regular_edges(built_flow) == {
        ("__start__", "classify_support_ticket"),
        ("classify_support_ticket", "apply_support_triage_policy"),
        ("apply_support_triage_policy", "drafting_branch"),
        ("drafting_branch", "draft_support_response"),
        ("drafting_branch", "finalize_skipped_record"),
        ("draft_support_response", "finalize_drafted_record"),
        ("finalize_drafted_record", "__end__"),
        ("finalize_skipped_record", "__end__"),
    }
    assert branch_conditions(built_flow.nodes["drafting_branch"]) == [
        {
            "expression": AUTO_ROUTE_EXPRESSION,
            "node_id": "draft_support_response",
            "default": False,
            "metadata": None,
        },
        {
            "expression": None,
            "node_id": "finalize_skipped_record",
            "default": True,
            "metadata": None,
        },
    ]
    tool_nodes = {
        node_name: getattr(node.spec, "tool", None)
        for node_name, node in built_flow.nodes.items()
        if getattr(node.spec, "tool", None)
    }
    assert tool_nodes == {
        "classify_support_ticket": "classify_support_ticket_configured",
        "apply_support_triage_policy": "apply_support_triage_policy",
        "draft_support_response": "draft_support_response_configured",
        "finalize_drafted_record": "finalize_support_triage_record",
        "finalize_skipped_record": "finalize_support_triage_record",
    }


def test_flow_tool_inputs_keep_classifier_policy_and_draft_boundaries(tmp_path, monkeypatch):
    install_local_orchestrate_config(tmp_path, monkeypatch)
    flow_module = importlib.import_module("flows.support_triage_flow")
    built_flow = flow_module.build_support_triage_flow()

    assert data_map(built_flow.nodes["classify_support_ticket"].input_map) == {
        "self.input.ticket_id": "flow.input.ticket_id",
        "self.input.ticket_text": "flow.input.ticket_text",
    }
    assert data_map(built_flow.nodes["apply_support_triage_policy"].input_map) == {
        "self.input.ticket_id": "flow.input.ticket_id",
        "self.input.ticket_text": "flow.input.ticket_text",
        "self.input.classifier_execution": "flow.classify_support_ticket.output",
    }
    assert data_map(built_flow.nodes["draft_support_response"].input_map) == {
        "self.input.ticket_id": "flow.input.ticket_id",
        "self.input.ticket_text": "flow.input.ticket_text",
        "self.input.assigned_team": "flow.apply_support_triage_policy.output.assigned_team",
        "self.input.sla": "flow.apply_support_triage_policy.output.sla",
    }
    assert data_map(built_flow.nodes["finalize_drafted_record"].input_map) == {
        "self.input.pre_draft_output": "flow.apply_support_triage_policy.output",
        "self.input.draft_execution": "flow.draft_support_response.output",
    }
    assert data_map(built_flow.nodes["finalize_skipped_record"].input_map) == {
        "self.input.pre_draft_output": "flow.apply_support_triage_policy.output",
    }


def test_public_output_map_selects_drafted_or_skipped_final_record(tmp_path, monkeypatch):
    install_local_orchestrate_config(tmp_path, monkeypatch)
    flow_module = importlib.import_module("flows.support_triage_flow")
    built_flow = flow_module.build_support_triage_flow()

    mapping = data_map(built_flow.output_map)
    assert set(mapping) == {
        f"flow.output.{field_name}"
        for field_name in flow_module.StructuredTicketOutput.model_fields
    }
    for field_name in flow_module.StructuredTicketOutput.model_fields:
        assert mapping[f"flow.output.{field_name}"] == (
            f"flow.finalize_drafted_record.output.{field_name} if {AUTO_ROUTE_EXPRESSION} "
            f"else flow.finalize_skipped_record.output.{field_name}"
        )


def test_flow_compiles_and_installed_loader_discovers_production_graph(tmp_path, monkeypatch):
    install_local_orchestrate_config(tmp_path, monkeypatch)
    flow_module = importlib.import_module("flows.support_triage_flow")
    built_flow = flow_module.build_support_triage_flow()

    assert built_flow.validate_model() is True
    compiled = built_flow.compile().flow.model_dump()
    assert compiled["spec"]["name"] == "support_triage"
    assert set(compiled["nodes"]) == FLOW_NODES
    assert set(model_data_map(compiled["output_map"])) == {
        f"flow.output.{field_name}"
        for field_name in flow_module.StructuredTicketOutput.model_fields
    }

    env = os.environ.copy()
    env["USERPROFILE"] = str(tmp_path / "home")
    env["HOME"] = str(tmp_path / "home")
    script = (
        "import json; "
        "from ibm_watsonx_orchestrate.cli.commands.tools.tools_controller "
        "import load_flow_model_from_file; "
        f"model = load_flow_model_from_file({str(FLOW_PATH.resolve())!r}); "
        "print(json.dumps({'name': model['spec']['name'], 'nodes': sorted(model['nodes'])}))"
    )
    completed = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    loaded = json.loads(completed.stdout.splitlines()[-1])
    assert loaded["name"] == "support_triage"
    assert set(loaded["nodes"]) == FLOW_NODES


def test_flow_source_is_not_a_local_eval_or_monolithic_python_pipeline():
    source = FLOW_PATH.read_text(encoding="utf-8")
    forbidden_fragments = {
        "local_env_classifier",
        "local_env_drafter",
        "finalize_support_triage_output",
        "run_support_triage_dev_eval",
        "run_support_triage_heldout_eval",
        "support_tickets_seed",
        "ground_truth",
        "Path(",
        "WX_PROJECT_ID",
        "WX_API_KEY",
    }
    for fragment in forbidden_fragments:
        assert fragment not in source


def test_configured_remote_tools_hide_project_id_from_flow_inputs_and_use_key_value_config():
    assert function_arg_names(
        CLASSIFIER_PATH,
        "classify_support_ticket_configured",
    ) == ["ticket_id", "ticket_text"]
    assert function_arg_names(
        DRAFTER_PATH,
        "draft_support_response_configured",
    ) == ["ticket_id", "ticket_text", "assigned_team", "sla"]

    classifier_source = CLASSIFIER_PATH.read_text(encoding="utf-8")
    drafter_source = DRAFTER_PATH.read_text(encoding="utf-8")
    assert 'key_value(app_id=WATSONX_CONFIG_CONNECTION_APP_ID)' in classifier_source
    assert 'key_value(app_id=WATSONX_CONFIG_CONNECTION_APP_ID)' in drafter_source
    assert '"project_id"' in classifier_source
    assert '"project_id"' in drafter_source
    assert "orchestrate_configured_classifier()" in classifier_source
    assert "orchestrate_configured_drafter()" in drafter_source
    assert "wx_project_id: str" in classifier_source
    assert "wx_project_id: str" in drafter_source


def test_configured_classifier_reads_api_key_url_and_project_id_from_declared_connections(monkeypatch):
    from tools import support_triage_classifier as classifier

    captured = {}

    def fake_api_key_auth(*, app_id):
        captured["api_key_app_id"] = app_id
        return SimpleNamespace(api_key="api-key-1", url="https://watsonx.example")

    def fake_key_value(*, app_id):
        captured["key_value_app_id"] = app_id
        return {"project_id": "project-1"}

    class FakeClassifier:
        def __init__(self, **kwargs):
            captured["classifier_kwargs"] = kwargs

    monkeypatch.setattr(classifier, "api_key_auth", fake_api_key_auth)
    monkeypatch.setattr(classifier, "key_value", fake_key_value)
    monkeypatch.setattr(classifier, "WatsonxChatClassifier", FakeClassifier)

    classifier.orchestrate_configured_classifier()

    assert captured == {
        "api_key_app_id": "watsonx_ai",
        "key_value_app_id": "watsonx_ai_config",
        "classifier_kwargs": {
            "api_key": "api-key-1",
            "project_id": "project-1",
            "url": "https://watsonx.example",
        },
    }


def test_configured_drafter_reads_api_key_url_and_project_id_from_declared_connections(monkeypatch):
    from tools import support_triage_drafter as drafter

    captured = {}

    def fake_api_key_auth(*, app_id):
        captured["api_key_app_id"] = app_id
        return SimpleNamespace(api_key="api-key-1", url="https://watsonx.example")

    def fake_key_value(*, app_id):
        captured["key_value_app_id"] = app_id
        return {"project_id": "project-1"}

    class FakeDrafter:
        def __init__(self, **kwargs):
            captured["drafter_kwargs"] = kwargs

    monkeypatch.setattr(drafter, "api_key_auth", fake_api_key_auth)
    monkeypatch.setattr(drafter, "key_value", fake_key_value)
    monkeypatch.setattr(drafter, "WatsonxChatDrafter", FakeDrafter)

    drafter.orchestrate_configured_drafter()

    assert captured == {
        "api_key_app_id": "watsonx_ai",
        "key_value_app_id": "watsonx_ai_config",
        "drafter_kwargs": {
            "api_key": "api-key-1",
            "project_id": "project-1",
            "url": "https://watsonx.example",
        },
    }


@pytest.mark.parametrize(
    ("module_name", "factory_name"),
    [
        ("tools.support_triage_classifier", "orchestrate_configured_classifier"),
        ("tools.support_triage_drafter", "orchestrate_configured_drafter"),
    ],
)
def test_missing_key_value_project_id_fails_before_model_execution(
    monkeypatch,
    module_name,
    factory_name,
):
    module = importlib.import_module(module_name)

    def fake_api_key_auth(*, app_id):
        return SimpleNamespace(api_key="api-key-1", url="https://watsonx.example")

    def fake_key_value(*, app_id):
        return {"project_id": "   "}

    def fail_if_model_constructed(**kwargs):
        raise AssertionError("model client must not be constructed without project_id")

    monkeypatch.setattr(module, "api_key_auth", fake_api_key_auth)
    monkeypatch.setattr(module, "key_value", fake_key_value)
    if module_name.endswith("classifier"):
        monkeypatch.setattr(module, "WatsonxChatClassifier", fail_if_model_constructed)
    else:
        monkeypatch.setattr(module, "WatsonxChatDrafter", fail_if_model_constructed)

    with pytest.raises(RuntimeError, match="project_id key-value connection configuration"):
        getattr(module, factory_name)()


def test_configured_tool_expected_credentials_include_api_key_and_key_value_contracts():
    from tools.support_triage_classifier import classify_support_ticket_configured
    from tools.support_triage_drafter import draft_support_response_configured

    assert [
        (credential.app_id, str(credential.type))
        for credential in classify_support_ticket_configured.expected_credentials
    ] == [
        ("watsonx_ai", "api_key_auth"),
        ("watsonx_ai_config", "key_value_creds"),
    ]
    assert [
        (credential.app_id, str(credential.type))
        for credential in draft_support_response_configured.expected_credentials
    ] == [
        ("watsonx_ai", "api_key_auth"),
        ("watsonx_ai_config", "key_value_creds"),
    ]


def test_raw_classifier_validation_still_rejects_missing_nullable_model_keys():
    from tools.support_triage_classifier import (
        ClassificationOutputValidationError,
        parse_classification_response,
    )

    with pytest.raises(ClassificationOutputValidationError):
        parse_classification_response(
            json.dumps(
                {
                    "category": "technical",
                    "urgency": "medium",
                    "confidence": 0.9,
                    "reasoning": "The ticket describes a product issue.",
                }
            )
        )
    with pytest.raises(ClassificationOutputValidationError):
        parse_classification_response(
            json.dumps(
                {
                    "category": "technical",
                    "secondary_category": None,
                    "confidence": 0.9,
                    "reasoning": "The ticket describes a product issue.",
                }
            )
        )


def test_remote_transport_normalization_allows_auto_route_and_draft_finalization():
    from tools.support_triage_drafter import apply_support_triage_policy, finalize_support_triage_record

    classifier_payload = omit_transport_nulls(classifier_execution_payload())
    policy_output = tool_content(
        apply_support_triage_policy(
            ticket_id="REMOTE-LIKE-001",
            ticket_text="The export report fails with an error.",
            classifier_execution=classifier_payload,
        )
    )
    assert policy_output["status"] == "auto_route_pending"
    assert policy_output["classification"]["secondary_category"] is None

    final_output = tool_content(
        finalize_support_triage_record(
            pre_draft_output=omit_transport_nulls(policy_output),
            draft_execution=omit_transport_nulls(draft_execution_payload()),
        )
    )

    assert final_output["ticket_id"] == "REMOTE-LIKE-001"
    assert final_output["ticket_text"] == "The export report fails with an error."
    assert final_output["status"] == "auto_routed"
    assert final_output["classification"]["secondary_category"] is None
    assert final_output["draft_validation_status"] == "valid"
    assert final_output["draft_response"]


def test_remote_transport_normalization_allows_null_urgency_review_without_drafting():
    from tools.support_triage_classifier import ClassificationResult
    from tools.support_triage_drafter import apply_support_triage_policy, finalize_support_triage_record

    classifier_payload = omit_transport_nulls(
        classifier_execution_payload(
            classification=ClassificationResult(
                category="technical",
                secondary_category=None,
                urgency=None,
                confidence=0.9,
                reasoning="The ticket is too vague to infer urgency.",
            )
        )
    )
    policy_output = tool_content(
        apply_support_triage_policy(
            ticket_id="REMOTE-LIKE-001",
            ticket_text="it doesnt work fix it",
            classifier_execution=classifier_payload,
        )
    )

    assert policy_output["status"] == "human_review"
    assert policy_output["review_required"] is True
    assert policy_output["review_reasons"] == ["urgency_null"]
    assert policy_output["assigned_team"] == "Triage \u2014 Human"
    assert policy_output["sla"] == "Immediate"

    final_output = tool_content(
        finalize_support_triage_record(pre_draft_output=omit_transport_nulls(policy_output))
    )
    assert final_output["status"] == "human_review"
    assert final_output["draft_response"] is None


@pytest.mark.parametrize("validation_status", ["invalid_exhausted", "execution_error"])
def test_remote_transport_normalization_allows_invalid_classifier_paths_without_drafting(
    validation_status,
):
    from tools.support_triage_drafter import apply_support_triage_policy, finalize_support_triage_record

    classifier_payload = omit_transport_nulls(
        classifier_execution_payload(
            classification=None,
            validation_status=validation_status,
            attempt_count=2 if validation_status == "invalid_exhausted" else 1,
        )
    )
    assert "classification" not in classifier_payload

    policy_output = tool_content(
        apply_support_triage_policy(
            ticket_id="REMOTE-LIKE-001",
            ticket_text="The ticket could not be classified.",
            classifier_execution=classifier_payload,
        )
    )
    assert policy_output["status"] == "invalid_output"
    assert policy_output["classification"] is None
    assert policy_output["assigned_team"] == "Triage \u2014 Human"
    assert policy_output["sla"] == "Immediate"

    transported_policy_output = omit_transport_nulls(policy_output)
    assert "classification" not in transported_policy_output
    final_output = tool_content(
        finalize_support_triage_record(pre_draft_output=transported_policy_output)
    )
    assert final_output["status"] == "invalid_output"
    assert final_output["classification"] is None
    assert final_output["draft_response"] is None


def test_remote_transport_drafter_execution_error_finalizes_as_draft_failed():
    from tools.support_triage_drafter import apply_support_triage_policy, finalize_support_triage_record

    policy_output = tool_content(
        apply_support_triage_policy(
            ticket_id="REMOTE-LIKE-001",
            ticket_text="The export report fails with an error.",
            classifier_execution=omit_transport_nulls(classifier_execution_payload()),
        )
    )
    draft_payload = omit_transport_nulls(draft_execution_payload(validation_status="execution_error"))
    assert "draft_response" not in draft_payload

    final_output = tool_content(
        finalize_support_triage_record(
            pre_draft_output=omit_transport_nulls(policy_output),
            draft_execution=draft_payload,
        )
    )

    assert final_output["status"] == "draft_failed"
    assert final_output["review_required"] is False
    assert final_output["draft_response"] is None
    assert final_output["draft_validation_status"] == "execution_error"


def test_transport_normalization_does_not_default_missing_valid_classification():
    from tools.support_triage_drafter import apply_support_triage_policy

    payload = omit_transport_nulls(classifier_execution_payload())
    payload.pop("classification")

    with pytest.raises(ValidationError):
        apply_support_triage_policy(
            ticket_id="REMOTE-LIKE-001",
            ticket_text="The export report fails with an error.",
            classifier_execution=payload,
        )


def test_finalizer_transport_normalization_does_not_default_missing_valid_classification():
    from tools.support_triage_drafter import apply_support_triage_policy, finalize_support_triage_record

    policy_output = tool_content(
        apply_support_triage_policy(
            ticket_id="REMOTE-LIKE-001",
            ticket_text="The export report fails with an error.",
            classifier_execution=omit_transport_nulls(classifier_execution_payload()),
        )
    )
    transported_policy_output = omit_transport_nulls(policy_output)
    transported_policy_output.pop("classification")

    with pytest.raises(ValidationError):
        finalize_support_triage_record(
            pre_draft_output=transported_policy_output,
            draft_execution=omit_transport_nulls(draft_execution_payload()),
        )


@pytest.mark.parametrize("missing_field", ["category", "confidence", "reasoning"])
def test_transport_normalization_does_not_default_required_classification_fields(missing_field):
    from tools.support_triage_drafter import apply_support_triage_policy

    payload = omit_transport_nulls(classifier_execution_payload())
    payload["classification"].pop(missing_field)

    with pytest.raises(ValidationError):
        apply_support_triage_policy(
            ticket_id="REMOTE-LIKE-001",
            ticket_text="The export report fails with an error.",
            classifier_execution=payload,
        )


@pytest.mark.parametrize(
    ("field_name", "bad_value"),
    [("secondary_category", "sales"), ("urgency", "urgent")],
)
def test_transport_normalization_does_not_rewrite_invalid_nullable_values(field_name, bad_value):
    from tools.support_triage_drafter import apply_support_triage_policy

    payload = classifier_execution_payload()
    payload["classification"][field_name] = bad_value

    with pytest.raises(ValidationError):
        apply_support_triage_policy(
            ticket_id="REMOTE-LIKE-001",
            ticket_text="The export report fails with an error.",
            classifier_execution=payload,
        )
