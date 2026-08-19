import ast
import base64
import importlib
import json
from pathlib import Path
import re
import sys
import time

import pytest


FLOW_PATH = Path("flows/it_request_flow.py")
REQUIRED_FIELDS = {"employee_name", "employee_role", "required_systems"}
SESSION_OUTPUTS = REQUIRED_FIELDS | {"confirmed"}
RESULT_FIELDS = {
    "status",
    "persisted",
    "employee_name",
    "employee_role",
    "required_systems",
    "request_id",
    "object_key",
    "verified",
}
FORBIDDEN_FIELDS = {"company_email", "employee_id", "department", "manager"}
SESSION_PREFIX = "flow.it_request_session.output"
TOP_LEVEL_INPUT_PREFIX = "flow.input"
REVIEW_BRANCHES = {
    "review_employee_name_source": (
        "employee_name",
        "review_employee_name_from_input",
        "review_employee_name_from_collected",
        "review_employee_role_source",
    ),
    "review_employee_role_source": (
        "employee_role",
        "review_employee_role_from_input",
        "review_employee_role_from_collected",
        "review_required_systems_source",
    ),
    "review_required_systems_source": (
        "required_systems",
        "review_required_systems_from_input",
        "review_required_systems_from_collected",
        "confirmed",
    ),
}
ALLOWED_REVIEW_TEXTS = {
    "review_employee_name_from_input": "Employee name: {flow.input.employee_name}",
    "review_employee_name_from_collected": "Employee name: {parent.employee_name.output.value}",
    "review_employee_role_from_input": "Employee role: {flow.input.employee_role}",
    "review_employee_role_from_collected": "Employee role: {parent.employee_role.output.value}",
    "review_required_systems_from_input": "Required systems: {flow.input.required_systems}",
    "review_required_systems_from_collected": "Required systems: {parent.required_systems.output.value}",
}
ALLOWED_SIMPLE_PLACEHOLDERS = {
    "flow.input.employee_name",
    "parent.employee_name.output.value",
    "flow.input.employee_role",
    "parent.employee_role.output.value",
    "flow.input.required_systems",
    "parent.required_systems.output.value",
}


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
        if name == "flows.it_request_flow":
            sys.modules.pop(name)


@pytest.fixture()
def flow_module(tmp_path, monkeypatch):
    install_local_orchestrate_config(tmp_path, monkeypatch)
    return importlib.import_module("flows.it_request_flow")


@pytest.fixture()
def built_flow(flow_module):
    return flow_module.build_it_request_flow()


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


def branch_conditions(branch):
    conditions = branch.spec.evaluator.to_json()["conditions"]
    return [
        {"expression": condition.get("expression"), **condition, "metadata": None}
        for condition in conditions
    ]


def regular_edges(graph):
    return {(edge.start, edge.end) for edge in graph.edges}


def expression_strings(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"expression", "value_expression"} and isinstance(item, str):
                yield item
            yield from expression_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from expression_strings(item)


def text_field(session, name):
    field = session.nodes[name].spec.fields[0]
    assert field.kind.value == "text"
    return field


def placeholders(text):
    return re.findall(r"\{([^{}]+)\}", text)


def test_public_business_schemas_are_frozen(flow_module):
    assert set(flow_module.ITRequestInput.model_fields) == REQUIRED_FIELDS
    assert all(
        not field.is_required() for field in flow_module.ITRequestInput.model_fields.values()
    )
    assert set(flow_module.ITRequestResult.model_fields) == RESULT_FIELDS
    source = FLOW_PATH.read_text(encoding="utf-8")
    assert not FORBIDDEN_FIELDS.intersection(source)


def test_missing_field_helpers_preserve_supplied_values(flow_module):
    draft = flow_module.normalize_it_request_input(" Ada ", None, "  ")
    assert draft.employee_name == "Ada"
    assert draft.missing_fields == ["employee_role", "required_systems"]
    merged = flow_module.merge_collected_values(
        draft,
        {
            "employee_name": "ignored replacement",
            "employee_role": "Platform Engineer",
            "required_systems": "Slack, Jira",
        },
    )
    assert merged.model_dump() == {
        "employee_name": "Ada",
        "employee_role": "Platform Engineer",
        "required_systems": "Slack, Jira",
        "missing_fields": [],
    }


@pytest.mark.parametrize(
    ("employee_name", "employee_role", "required_systems", "missing_fields"),
    [
        (None, None, None, ["employee_name", "employee_role", "required_systems"]),
        (None, "QA Engineer", "Slack, GitHub", ["employee_name"]),
        ("Alex Doe", "QA Engineer", "Slack, GitHub", []),
        (None, None, "Slack, GitHub", ["employee_name", "employee_role"]),
        ("Alex Doe", None, None, ["employee_role", "required_systems"]),
        (None, "QA Engineer", None, ["employee_name", "required_systems"]),
    ],
)
def test_prefilled_it_request_combinations_identify_only_missing_fields(
    flow_module,
    employee_name,
    employee_role,
    required_systems,
    missing_fields,
):
    draft = flow_module.normalize_it_request_input(
        employee_name,
        employee_role,
        required_systems,
    )
    assert draft.missing_fields == missing_fields


def test_pure_business_helpers_enforce_zero_or_one_persistence(flow_module):
    draft = flow_module.normalize_it_request_input("Ada", "Engineer", "Slack")
    cancelled = flow_module.cancel_it_request(draft)
    assert cancelled["status"] == "cancelled"
    assert cancelled["persisted"] is False

    calls = []

    def persist(**kwargs):
        calls.append(kwargs)
        return {
            "record_id": "req-1",
            "object_key": "it_requests/req-1.json",
            "verified": True,
        }

    submitted = flow_module.submit_it_request(draft, persist=persist)
    assert len(calls) == 1
    assert calls[0] == {
        "employee_name": "Ada",
        "employee_role": "Engineer",
        "required_systems": "Slack",
    }
    assert submitted["status"] == "submitted"
    assert submitted["persisted"] is True


def test_incomplete_request_cannot_reach_business_confirmation(flow_module):
    draft = flow_module.normalize_it_request_input("Ada", None, "Slack")
    with pytest.raises(ValueError, match="missing required fields"):
        flow_module.confirmation_summary(draft)


def test_source_has_exactly_one_module_level_flow_wrapper():
    tree = ast.parse(FLOW_PATH.read_text(encoding="utf-8"))
    decorated = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if any(
            (isinstance(decorator, ast.Name) and decorator.id == "flow")
            or (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and decorator.func.id == "flow")
            for decorator in node.decorator_list
        ):
            decorated.append(node.name)
    assert decorated == ["it_request_flow"]


def test_flow_uses_one_field_based_userflow_without_forms_llm_or_private_state(built_flow):
    userflows = [node for node in built_flow.nodes.values() if type(node).__name__ == "UserFlow"]
    assert [node.spec.name for node in userflows] == ["it_request_session"]
    source = FLOW_PATH.read_text(encoding="utf-8")
    assert ".form(" not in source
    assert ".prompt(" not in source
    assert ".agent(" not in source
    assert "flow.private" not in source
    assert "capture_" not in source


def test_all_interactive_fields_share_the_single_session(built_flow):
    session = built_flow.nodes["it_request_session"]
    assert set(session.nodes) == {
        "__start__",
        "__end__",
        "need_employee_name",
        "employee_name",
        "need_employee_role",
        "employee_role",
        "need_required_systems",
        "required_systems",
        "proposed_it_request",
        "review_employee_name_source",
        "review_employee_name_from_input",
        "review_employee_name_from_collected",
        "review_employee_role_source",
        "review_employee_role_from_input",
        "review_employee_role_from_collected",
        "review_required_systems_source",
        "review_required_systems_from_input",
        "review_required_systems_from_collected",
        "confirmed",
    }
    fields = {
        name: session.nodes[name].spec.fields[0]
        for name in [
            "employee_name",
            "employee_role",
            "required_systems",
            "proposed_it_request",
            *ALLOWED_REVIEW_TEXTS,
            "confirmed",
        ]
    }
    assert all(fields[name].direction == "input" for name in REQUIRED_FIELDS)
    assert all(fields[name].kind.value == "text" for name in REQUIRED_FIELDS)
    assert fields["proposed_it_request"].direction == "output"
    assert fields["proposed_it_request"].kind.value == "text"
    assert all(
        fields[name].direction == "output" and fields[name].kind.value == "text"
        for name in ALLOWED_REVIEW_TEXTS
    )
    assert fields["confirmed"].direction == "input"
    assert fields["confirmed"].kind.value == "boolean"
    assert fields["confirmed"].output_schema.properties["value"].type == "boolean"


@pytest.mark.parametrize(
    ("branch_name", "field_name", "default_target"),
    [
        ("need_employee_name", "employee_name", "need_employee_role"),
        ("need_employee_role", "employee_role", "need_required_systems"),
        ("need_required_systems", "required_systems", "proposed_it_request"),
    ],
)
def test_missing_field_branches_skip_supplied_and_request_missing(
    built_flow,
    branch_name,
    field_name,
    default_target,
):
    session = built_flow.nodes["it_request_session"]
    assert branch_conditions(session.nodes[branch_name]) == [
        {
            "expression": (
                f"not {TOP_LEVEL_INPUT_PREFIX}.{field_name} or "
                f"not {TOP_LEVEL_INPUT_PREFIX}.{field_name}.strip()"
            ),
            "node_id": field_name,
            "default": False,
            "metadata": None,
        },
        {
            "expression": None,
            "node_id": default_target,
            "default": True,
            "metadata": None,
        },
    ]


@pytest.mark.parametrize(
    ("branch_name", "field_name", "input_target", "collected_target", "_next_target"),
    [
        (branch_name, *branch_contract)
        for branch_name, branch_contract in REVIEW_BRANCHES.items()
    ],
)
def test_review_source_branches_use_only_input_presence_and_default_to_collected(
    built_flow,
    branch_name,
    field_name,
    input_target,
    collected_target,
    _next_target,
):
    session = built_flow.nodes["it_request_session"]
    assert branch_conditions(session.nodes[branch_name]) == [
        {
            "expression": (
                f"{TOP_LEVEL_INPUT_PREFIX}.{field_name} and "
                f"{TOP_LEVEL_INPUT_PREFIX}.{field_name}.strip()"
            ),
            "node_id": input_target,
            "default": False,
            "metadata": None,
        },
        {
            "expression": None,
            "node_id": collected_target,
            "default": True,
            "metadata": None,
        },
    ]


def test_session_edges_have_no_post_field_capture_scripts(built_flow):
    session = built_flow.nodes["it_request_session"]
    assert regular_edges(session) == {
        ("__start__", "need_employee_name"),
        ("need_employee_name", "employee_name"),
        ("need_employee_name", "need_employee_role"),
        ("employee_name", "need_employee_role"),
        ("need_employee_role", "employee_role"),
        ("need_employee_role", "need_required_systems"),
        ("employee_role", "need_required_systems"),
        ("need_required_systems", "required_systems"),
        ("need_required_systems", "proposed_it_request"),
        ("required_systems", "proposed_it_request"),
        ("proposed_it_request", "review_employee_name_source"),
        ("review_employee_name_source", "review_employee_name_from_input"),
        ("review_employee_name_source", "review_employee_name_from_collected"),
        ("review_employee_name_from_input", "review_employee_role_source"),
        ("review_employee_name_from_collected", "review_employee_role_source"),
        ("review_employee_role_source", "review_employee_role_from_input"),
        ("review_employee_role_source", "review_employee_role_from_collected"),
        ("review_employee_role_from_input", "review_required_systems_source"),
        ("review_employee_role_from_collected", "review_required_systems_source"),
        ("review_required_systems_source", "review_required_systems_from_input"),
        ("review_required_systems_source", "review_required_systems_from_collected"),
        ("review_required_systems_from_input", "confirmed"),
        ("review_required_systems_from_collected", "confirmed"),
        ("confirmed", "__end__"),
    }
    assert not any(type(node).__name__ == "Script" for node in session.nodes.values())


def test_authoritative_expressions_are_lazy_supplied_or_collected(flow_module):
    expected = {
        "employee_name": flow_module.AUTHORITATIVE_EMPLOYEE_NAME,
        "employee_role": flow_module.AUTHORITATIVE_EMPLOYEE_ROLE,
        "required_systems": flow_module.AUTHORITATIVE_REQUIRED_SYSTEMS,
    }
    for field_name, expression in expected.items():
        tree = ast.parse(expression, mode="eval")
        assert isinstance(tree.body, ast.IfExp)
        assert expression.startswith(f"{TOP_LEVEL_INPUT_PREFIX}.{field_name} if ")
        assert expression.endswith(f"else parent.{field_name}.output.value")


def test_proposed_request_is_static_heading_and_review_texts_are_simple(
    built_flow,
):
    session = built_flow.nodes["it_request_session"]
    field = session.nodes["proposed_it_request"].spec.fields[0]
    assert field.kind.value == "text"
    assert field.direction == "output"
    assert field.input_map is None
    assert field.text == "Proposed IT access request"
    assert placeholders(field.text) == []

    dynamic_review_nodes = {
        name: text_field(session, name).text for name in ALLOWED_REVIEW_TEXTS
    }
    assert dynamic_review_nodes == ALLOWED_REVIEW_TEXTS
    for text in dynamic_review_nodes.values():
        refs = placeholders(text)
        assert len(refs) == 1
        assert refs[0] in ALLOWED_SIMPLE_PLACEHOLDERS
        assert " if " not in refs[0]
        assert " else " not in refs[0]
        assert " and " not in refs[0]
        assert " or " not in refs[0]
        assert ".strip()" not in refs[0]
        assert "(" not in refs[0]
        assert ")" not in refs[0]
        assert "+" not in refs[0]
        assert "-" not in refs[0]
        assert "*" not in refs[0]
        assert "/" not in refs[0]
        assert "flow.private" not in text
        assert "G2 Single Session No 20260816-A" not in text
        assert "QA Engineer" not in text
        assert "Github, Slack" not in text


def test_compiled_review_request_preserves_static_heading_and_simple_texts(
    built_flow,
):
    model = built_flow.compile().flow.model_dump()
    session = model["nodes"]["it_request_session"]
    heading = session["nodes"]["proposed_it_request"]["spec"][
        "fields"
    ][0]
    assert heading["kind"] == "text"
    assert heading["direction"] == "output"
    assert heading["text"] == "Proposed IT access request"
    assert heading["input_map"] is None
    for node_name, expected_text in ALLOWED_REVIEW_TEXTS.items():
        field = session["nodes"][node_name]["spec"]["fields"][0]
        assert field["kind"] == "text"
        assert field["direction"] == "output"
        assert field["text"] == expected_text
        assert field["input_map"] is None
        refs = placeholders(field["text"])
        assert len(refs) == 1
        assert refs[0] in ALLOWED_SIMPLE_PLACEHOLDERS


def test_session_has_exact_explicit_output_schema_and_maps(built_flow, flow_module):
    session = built_flow.nodes["it_request_session"]
    schema_name = session.spec.output_schema.ref.removeprefix("#/schemas/")
    assert set(built_flow.schemas[schema_name].properties) == SESSION_OUTPUTS
    assert data_map(session.input_map) == {}
    assert data_map(session.output_map) == {
        "flow.output.employee_name": flow_module.AUTHORITATIVE_EMPLOYEE_NAME,
        "flow.output.employee_role": flow_module.AUTHORITATIVE_EMPLOYEE_ROLE,
        "flow.output.required_systems": flow_module.AUTHORITATIVE_REQUIRED_SYSTEMS,
        "flow.output.confirmed": flow_module.SESSION_CONFIRMED,
    }


def test_top_level_graph_matches_single_session_side_effect_boundary(built_flow):
    assert set(built_flow.nodes) == {
        "__start__",
        "__end__",
        "it_request_session",
        "persist_it_request_once",
        "cancelled_result",
        "submitted_result",
        "confirmation_branch",
    }
    assert regular_edges(built_flow) == {
        ("__start__", "it_request_session"),
        ("it_request_session", "confirmation_branch"),
        ("confirmation_branch", "persist_it_request_once"),
        ("confirmation_branch", "cancelled_result"),
        ("persist_it_request_once", "submitted_result"),
        ("submitted_result", "__end__"),
        ("cancelled_result", "__end__"),
    }


def test_parent_confirmation_branch_reads_only_session_confirmation(built_flow):
    assert branch_conditions(built_flow.nodes["confirmation_branch"]) == [
        {
            "expression": f"{SESSION_PREFIX}.confirmed",
            "node_id": "persist_it_request_once",
            "default": False,
            "metadata": None,
        },
        {
            "expression": None,
            "node_id": "cancelled_result",
            "default": True,
            "metadata": None,
        },
    ]


def test_cancelled_and_persist_inputs_come_only_from_session_outputs(built_flow):
    expected = {
        f"self.input.{field_name}": f"{SESSION_PREFIX}.{field_name}"
        for field_name in REQUIRED_FIELDS
    }
    assert data_map(built_flow.nodes["cancelled_result"].input_map) == expected
    assert data_map(built_flow.nodes["persist_it_request_once"].input_map) == expected
    cancelled_script = built_flow.nodes["cancelled_result"].spec.fn
    assert "self.output.persisted = False" in cancelled_script
    assert "self.output.request_id = None" in cancelled_script
    assert "self.output.object_key = None" in cancelled_script
    assert "self.output.verified = None" in cancelled_script


def test_no_path_cannot_reach_persistence_and_yes_is_the_only_entry(built_flow):
    conditions = branch_conditions(built_flow.nodes["confirmation_branch"])
    yes_target = conditions[0]["node_id"]
    no_target = conditions[1]["node_id"]
    assert yes_target == "persist_it_request_once"
    assert no_target == "cancelled_result"
    assert [edge.start for edge in built_flow.edges if edge.end == "persist_it_request_once"] == [
        "confirmation_branch"
    ]
    assert all(edge.end != "persist_it_request_once" for edge in built_flow.edges if edge.start == no_target)
    assert regular_edges(built_flow).issuperset(
        {
            (yes_target, "submitted_result"),
            ("submitted_result", "__end__"),
            (no_target, "__end__"),
        }
    )


def test_exactly_one_persistence_tool_node_exists_at_top_level(built_flow):
    persistence_nodes = [
        node
        for node in built_flow.nodes.values()
        if getattr(node.spec, "tool", None) == "persist_it_request"
    ]
    assert [node.spec.name for node in persistence_nodes] == ["persist_it_request_once"]
    session = built_flow.nodes["it_request_session"]
    assert not any(getattr(node.spec, "tool", None) for node in session.nodes.values())


def test_submitted_result_uses_session_and_single_persistence_result(built_flow):
    mapping = data_map(built_flow.nodes["submitted_result"].input_map)
    assert {mapping[f"self.input.{field}"] for field in REQUIRED_FIELDS} == {
        f"{SESSION_PREFIX}.{field}" for field in REQUIRED_FIELDS
    }
    assert mapping["self.input.request_id"] == "flow.persist_it_request_once.output.record_id"
    assert mapping["self.input.object_key"] == "flow.persist_it_request_once.output.object_key"
    assert mapping["self.input.verified"] == "flow.persist_it_request_once.output.verified"


def test_public_output_map_selects_exactly_one_terminal_result(built_flow):
    mapping = data_map(built_flow.output_map)
    assert set(mapping) == {f"flow.output.{field}" for field in RESULT_FIELDS}
    for field_name in RESULT_FIELDS:
        assert mapping[f"flow.output.{field_name}"] == (
            f"flow.submitted_result.output.{field_name} if {SESSION_PREFIX}.confirmed "
            f"else flow.cancelled_result.output.{field_name}"
        )


def test_compiled_parent_expressions_never_reference_nested_field_nodes(built_flow):
    assert built_flow.validate_model() is True
    model = built_flow.compile().flow.model_dump()
    parent_model = dict(model)
    parent_model["nodes"] = dict(model["nodes"])
    session = parent_model["nodes"].pop("it_request_session")
    parent_expressions = list(expression_strings(parent_model))
    assert parent_expressions
    assert all("flow.private" not in expression for expression in parent_expressions)
    assert all(
        not re.search(r"flow\.it_request_session\.(?!output\.)", expression)
        for expression in parent_expressions
    )
    assert all(
        f"{SESSION_PREFIX}.{field_name}" in " ".join(parent_expressions)
        for field_name in SESSION_OUTPUTS
    )
    assert set(session["nodes"]).issuperset(
        REQUIRED_FIELDS
        | {"proposed_it_request", "confirmed"}
        | set(REVIEW_BRANCHES)
        | set(ALLOWED_REVIEW_TEXTS)
    )


def test_compiled_session_preserves_branches_fields_and_output_contract(built_flow):
    model = built_flow.compile().flow.model_dump()
    session = model["nodes"]["it_request_session"]
    schema_name = session["spec"]["output_schema"]["ref"].removeprefix("#/schemas/")
    assert set(model["schemas"][schema_name]["properties"]) == SESSION_OUTPUTS
    assert set(session["nodes"]) == {
        "need_employee_name",
        "employee_name",
        "need_employee_role",
        "employee_role",
        "need_required_systems",
        "required_systems",
        "proposed_it_request",
        "review_employee_name_source",
        "review_employee_name_from_input",
        "review_employee_name_from_collected",
        "review_employee_role_source",
        "review_employee_role_from_input",
        "review_employee_role_from_collected",
        "review_required_systems_source",
        "review_required_systems_from_input",
        "review_required_systems_from_collected",
        "confirmed",
        "__start__",
        "__end__",
    }
    assert set(model_data_map(session["output_map"])) == {
        f"flow.output.{field_name}" for field_name in SESSION_OUTPUTS
    }


def test_compiled_session_uses_top_level_prefilled_scope_without_nested_input_map(built_flow):
    model = built_flow.compile().flow.model_dump()
    compiled_session = model["nodes"]["it_request_session"]
    assert compiled_session.get("input_map") is None

    session = built_flow.nodes["it_request_session"]
    serialized_parts = []
    for branch_name in [
        "need_employee_name",
        "need_employee_role",
        "need_required_systems",
        *REVIEW_BRANCHES,
    ]:
        serialized_parts.extend(
            condition["expression"] or ""
            for condition in branch_conditions(session.nodes[branch_name])
        )
    serialized_parts.extend(text_field(session, name).text for name in ALLOWED_REVIEW_TEXTS)
    serialized_parts.extend(data_map(session.output_map).values())
    serialized = "\n".join(serialized_parts)

    assert "parent.input" not in serialized
    for field_name in REQUIRED_FIELDS:
        assert f"{TOP_LEVEL_INPUT_PREFIX}.{field_name}" in serialized
        assert f"{TOP_LEVEL_INPUT_PREFIX}.{field_name}.strip()" in serialized
        assert f"parent.{field_name}.output.value" in serialized


def test_installed_loader_discovers_the_single_session_contract(tmp_path, monkeypatch):
    install_local_orchestrate_config(tmp_path, monkeypatch)
    from ibm_watsonx_orchestrate.cli.commands.tools.tools_controller import (
        load_flow_model_from_file,
    )

    model = load_flow_model_from_file(str(FLOW_PATH.resolve()))
    assert model["spec"]["name"] == "it_request_flow"
    assert set(model["nodes"]) == {
        "it_request_session",
        "persist_it_request_once",
        "cancelled_result",
        "submitted_result",
        "confirmation_branch",
        "__start__",
        "__end__",
    }
    session = model["nodes"]["it_request_session"]
    assert set(session["nodes"]) == {
        "need_employee_name",
        "employee_name",
        "need_employee_role",
        "employee_role",
        "need_required_systems",
        "required_systems",
        "proposed_it_request",
        "review_employee_name_source",
        "review_employee_name_from_input",
        "review_employee_name_from_collected",
        "review_employee_role_source",
        "review_employee_role_from_input",
        "review_employee_role_from_collected",
        "review_required_systems_source",
        "review_required_systems_from_input",
        "review_required_systems_from_collected",
        "confirmed",
        "__start__",
        "__end__",
    }
    assert set(model_data_map(session["output_map"])) == {
        f"flow.output.{field_name}" for field_name in SESSION_OUTPUTS
    }
    proposed_field = session["nodes"]["proposed_it_request"]["spec"]["fields"][0]
    assert proposed_field["text"] == "Proposed IT access request"
    assert proposed_field.get("input_map") is None
    for node_name, expected_text in ALLOWED_REVIEW_TEXTS.items():
        field = session["nodes"][node_name]["spec"]["fields"][0]
        assert field["text"] == expected_text
        refs = placeholders(field["text"])
        assert len(refs) == 1
        assert refs[0] in ALLOWED_SIMPLE_PLACEHOLDERS
    assert sum(
        1
        for node in model["nodes"].values()
        if node["spec"].get("tool") == "persist_it_request"
    ) == 1
