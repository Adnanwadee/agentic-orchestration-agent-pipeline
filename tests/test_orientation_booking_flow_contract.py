import ast
import base64
import importlib
import json
from pathlib import Path
import re
import sys
import time

import pytest


FLOW_PATH = Path("flows/orientation_booking_flow.py")
PROJECT_SPEC_PATH = Path("artifacts/development_history/PROJECT_SPEC_HISTORY.md")
APPROVED_SLOTS = (
    "Monday 09:00-10:00",
    "Wednesday 13:00-14:00",
    "Thursday 15:00-16:00",
)
SESSION_OUTPUTS = {"selected_slot", "confirmed"}
RESULT_FIELDS = {
    "status",
    "persisted",
    "selected_slot",
    "booking_id",
    "object_key",
    "verified",
}
SESSION_PREFIX = "flow.orientation_booking_session.output"
FORBIDDEN_SLOT_VALUES = {
    "Friday 09:00-10:00",
    "Monday 10:00-11:00",
    "2026-08-17T09:00:00Z",
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
        if name == "ibm_watsonx_orchestrate.cli.commands.tools.tools_controller":
            sys.modules.pop(name)
        if name == "flows.orientation_booking_flow":
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
    return branch.model_dump()["spec"]["evaluator"]["conditions"]


def expression_strings(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"expression", "value_expression"} and isinstance(item, str):
                yield item
            yield from expression_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from expression_strings(item)


def choice_list_from_field(field):
    mapping = data_map(field.input_map)
    return tuple(ast.literal_eval(mapping["self.input.choices"]))


def model_choice_list_from_field(field):
    mapping = model_data_map(field["input_map"])
    return tuple(ast.literal_eval(mapping["self.input.choices"]))


def placeholders(text):
    return re.findall(r"\{([^{}]+)\}", text)


@pytest.fixture()
def flow_module(tmp_path, monkeypatch):
    install_local_orchestrate_config(tmp_path, monkeypatch)
    return importlib.import_module("flows.orientation_booking_flow")


@pytest.fixture()
def built_flow(flow_module):
    return flow_module.build_orientation_booking_flow()


def test_source_has_exactly_one_module_level_flow_wrapper():
    tree = ast.parse(FLOW_PATH.read_text(encoding="utf-8"))
    decorated = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if any(
            (isinstance(decorator, ast.Name) and decorator.id == "flow")
            or (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Name)
                and decorator.func.id == "flow"
            )
            for decorator in node.decorator_list
        ):
            decorated.append(node.name)
    assert decorated == ["orientation_booking_flow"]


def test_canonical_slots_are_exact_unique_and_recorded(flow_module):
    assert flow_module.approved_orientation_slots() == APPROVED_SLOTS
    assert len(APPROVED_SLOTS) == 3
    assert len(set(APPROVED_SLOTS)) == 3
    assert all(not flow_module.is_approved_orientation_slot(slot) for slot in FORBIDDEN_SLOT_VALUES)
    spec = PROJECT_SPEC_PATH.read_text(encoding="utf-8")
    for slot in APPROVED_SLOTS:
        assert slot in spec


def test_public_business_schemas_are_stable(flow_module):
    assert set(flow_module.OrientationBookingInput.model_fields) == set()
    assert set(flow_module.OrientationBookingSessionOutput.model_fields) == SESSION_OUTPUTS
    assert set(flow_module.OrientationBookingResult.model_fields) == RESULT_FIELDS


def test_pure_helpers_enforce_zero_or_one_persistence(flow_module):
    slot = APPROVED_SLOTS[0]
    cancelled = flow_module.cancel_orientation_booking(slot)
    assert cancelled == {
        "status": "cancelled",
        "persisted": False,
        "selected_slot": slot,
        "booking_id": None,
        "object_key": None,
        "verified": None,
    }
    calls = []

    def persist(**kwargs):
        calls.append(kwargs)
        return {
            "record_id": "book-1",
            "object_key": "orientation_bookings/book-1.json",
            "verified": True,
        }

    booked = flow_module.submit_orientation_booking(slot, persist=persist)
    assert calls == [{"selected_slot": slot}]
    assert booked == {
        "status": "booked",
        "persisted": True,
        "selected_slot": slot,
        "booking_id": "book-1",
        "object_key": "orientation_bookings/book-1.json",
        "verified": True,
    }


def test_no_parallel_runtime_slot_validation_architecture(flow_module):
    assert flow_module.is_approved_orientation_slot(APPROVED_SLOTS[1]) is True
    assert flow_module.is_approved_orientation_slot("Tuesday 11:00-12:00") is False
    source = FLOW_PATH.read_text(encoding="utf-8")
    assert "datetime" not in source
    assert "calendar" not in source.lower()
    assert "Google Calendar" not in source
    assert "Outlook" not in source


def test_flow_uses_one_field_based_userflow_without_forms_llm_private_or_capture(built_flow):
    userflows = [node for node in built_flow.nodes.values() if type(node).__name__ == "UserFlow"]
    assert [node.spec.name for node in userflows] == ["orientation_booking_session"]
    source = FLOW_PATH.read_text(encoding="utf-8")
    assert ".form(" not in source
    assert ".prompt(" not in source
    assert ".agent(" not in source
    assert "flow.private" not in source
    assert "capture_" not in source


def test_slot_selection_is_native_single_choice_with_only_approved_choices(
    built_flow,
):
    session = built_flow.nodes["orientation_booking_session"]
    field = session.nodes["selected_slot"].spec.fields[0]
    assert field.direction == "input"
    assert field.kind.value == "any"
    assert field.kind.name == "Choice"
    assert field.kind.value != "text"
    assert field.display_name == "Orientation slot"
    assert choice_list_from_field(field) == APPROVED_SLOTS
    assert set(choice_list_from_field(field)) == set(APPROVED_SLOTS)
    assert all(slot not in choice_list_from_field(field) for slot in FORBIDDEN_SLOT_VALUES)


def test_compiled_choice_field_exposes_exactly_three_choices(built_flow):
    model = built_flow.compile().flow.model_dump()
    field = model["nodes"]["orientation_booking_session"]["nodes"]["selected_slot"]["spec"][
        "fields"
    ][0]
    assert field["kind"] == "any"
    assert field["direction"] == "input"
    assert model_choice_list_from_field(field) == APPROVED_SLOTS
    assert field["input_schema"]["required"] == ["choices"]
    assert field["input_schema"]["properties"]["choices"]["type"] == "array"


def test_session_nodes_and_edges_keep_review_before_confirmation(built_flow):
    session = built_flow.nodes["orientation_booking_session"]
    assert set(session.nodes) == {
        "__start__",
        "__end__",
        "selected_slot",
        "proposed_orientation_booking",
        "review_selected_slot",
        "confirmed",
    }
    assert regular_edges(session) == {
        ("__start__", "selected_slot"),
        ("selected_slot", "proposed_orientation_booking"),
        ("proposed_orientation_booking", "review_selected_slot"),
        ("review_selected_slot", "confirmed"),
        ("confirmed", "__end__"),
    }
    assert not any(type(node).__name__ == "Script" for node in session.nodes.values())


def test_visible_review_uses_simple_selected_slot_reference(built_flow):
    session = built_flow.nodes["orientation_booking_session"]
    heading = session.nodes["proposed_orientation_booking"].spec.fields[0]
    review = session.nodes["review_selected_slot"].spec.fields[0]
    confirmed = session.nodes["confirmed"].spec.fields[0]
    assert heading.direction == "output"
    assert heading.kind.value == "text"
    assert heading.text == "Proposed orientation booking"
    assert placeholders(heading.text) == []
    assert review.direction == "output"
    assert review.kind.value == "text"
    assert review.text == "Selected slot: {parent.selected_slot.output.value}"
    assert placeholders(review.text) == ["parent.selected_slot.output.value"]
    assert confirmed.direction == "input"
    assert confirmed.kind.value == "boolean"
    assert confirmed.text == "Book this orientation session?"


def test_session_output_schema_and_maps_are_explicit_same_userflow_boundary(
    built_flow,
    flow_module,
):
    session = built_flow.nodes["orientation_booking_session"]
    schema_name = session.spec.output_schema.ref.removeprefix("#/schemas/")
    assert set(built_flow.schemas[schema_name].properties) == SESSION_OUTPUTS
    assert data_map(session.output_map) == {
        "flow.output.selected_slot": flow_module.SESSION_SELECTED_SLOT,
        "flow.output.confirmed": flow_module.SESSION_CONFIRMED,
    }


def test_top_level_graph_matches_booking_side_effect_boundary(built_flow):
    assert set(built_flow.nodes) == {
        "__start__",
        "__end__",
        "orientation_booking_session",
        "persist_orientation_booking_once",
        "cancelled_result",
        "booked_result",
        "confirmation_branch",
    }
    assert regular_edges(built_flow) == {
        ("__start__", "orientation_booking_session"),
        ("orientation_booking_session", "confirmation_branch"),
        ("confirmation_branch", "persist_orientation_booking_once"),
        ("confirmation_branch", "cancelled_result"),
        ("persist_orientation_booking_once", "booked_result"),
        ("booked_result", "__end__"),
        ("cancelled_result", "__end__"),
    }


def test_parent_consumes_only_explicit_session_outputs(built_flow):
    assert branch_conditions(built_flow.nodes["confirmation_branch"]) == [
        {
            "expression": f"{SESSION_PREFIX}.confirmed",
            "node_id": "persist_orientation_booking_once",
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
    parent_maps = {
        **data_map(built_flow.nodes["persist_orientation_booking_once"].input_map),
        **data_map(built_flow.nodes["cancelled_result"].input_map),
        **data_map(built_flow.nodes["booked_result"].input_map),
        **data_map(built_flow.output_map),
    }
    assert parent_maps
    assert all(
        not re.search(r"flow\.orientation_booking_session\.(?!output\.)", expression)
        for expression in parent_maps.values()
    )
    assert all("parent.selected_slot" not in expression for expression in parent_maps.values())
    assert all("parent.confirmed" not in expression for expression in parent_maps.values())


def test_cancelled_and_persist_inputs_come_only_from_session_output(built_flow):
    expected = {"self.input.selected_slot": f"{SESSION_PREFIX}.selected_slot"}
    assert data_map(built_flow.nodes["cancelled_result"].input_map) == expected
    assert data_map(built_flow.nodes["persist_orientation_booking_once"].input_map) == expected
    script = built_flow.nodes["cancelled_result"].spec.fn
    assert "self.output.persisted = False" in script
    assert "self.output.booking_id = None" in script
    assert "self.output.object_key = None" in script
    assert "self.output.verified = None" in script


def test_no_path_cannot_reach_persistence_and_yes_is_sole_entry(built_flow):
    conditions = branch_conditions(built_flow.nodes["confirmation_branch"])
    yes_target = conditions[0]["node_id"]
    no_target = conditions[1]["node_id"]
    assert yes_target == "persist_orientation_booking_once"
    assert no_target == "cancelled_result"
    assert [
        edge.start
        for edge in built_flow.edges
        if edge.end == "persist_orientation_booking_once"
    ] == ["confirmation_branch"]
    assert all(
        edge.end != "persist_orientation_booking_once"
        for edge in built_flow.edges
        if edge.start == no_target
    )


def test_exactly_one_persistence_tool_node_exists_at_top_level(built_flow):
    persistence_nodes = [
        node
        for node in built_flow.nodes.values()
        if getattr(node.spec, "tool", None) == "persist_orientation_booking"
    ]
    assert [node.spec.name for node in persistence_nodes] == [
        "persist_orientation_booking_once"
    ]
    session = built_flow.nodes["orientation_booking_session"]
    assert not any(getattr(node.spec, "tool", None) for node in session.nodes.values())


def test_booked_result_consumes_session_and_single_persistence_result(built_flow):
    mapping = data_map(built_flow.nodes["booked_result"].input_map)
    assert mapping["self.input.selected_slot"] == f"{SESSION_PREFIX}.selected_slot"
    assert mapping["self.input.booking_id"] == (
        "flow.persist_orientation_booking_once.output.record_id"
    )
    assert mapping["self.input.object_key"] == (
        "flow.persist_orientation_booking_once.output.object_key"
    )
    assert mapping["self.input.verified"] == (
        "flow.persist_orientation_booking_once.output.verified"
    )


def test_public_output_map_selects_exactly_one_terminal_result(built_flow):
    mapping = data_map(built_flow.output_map)
    assert set(mapping) == {f"flow.output.{field}" for field in RESULT_FIELDS}
    for field_name in RESULT_FIELDS:
        assert mapping[f"flow.output.{field_name}"] == (
            f"flow.booked_result.output.{field_name} if {SESSION_PREFIX}.confirmed "
            f"else flow.cancelled_result.output.{field_name}"
        )


def test_compiled_model_preserves_booking_contract(built_flow):
    assert built_flow.validate_model() is True
    model = built_flow.compile().flow.model_dump()
    session = model["nodes"]["orientation_booking_session"]
    schema_name = session["spec"]["output_schema"]["ref"].removeprefix("#/schemas/")
    assert set(model["schemas"][schema_name]["properties"]) == SESSION_OUTPUTS
    assert set(session["nodes"]) == {
        "__start__",
        "__end__",
        "selected_slot",
        "proposed_orientation_booking",
        "review_selected_slot",
        "confirmed",
    }
    assert model_data_map(session["output_map"]) == {
        "flow.output.selected_slot": "parent.selected_slot.output.value",
        "flow.output.confirmed": "parent.confirmed.output.value",
    }


def test_installed_loader_discovers_single_booking_session_contract(tmp_path, monkeypatch):
    install_local_orchestrate_config(tmp_path, monkeypatch)
    from ibm_watsonx_orchestrate.cli.commands.tools.tools_controller import (
        load_flow_model_from_file,
    )

    model = load_flow_model_from_file(str(FLOW_PATH.resolve()))
    assert model["spec"]["name"] == "orientation_booking_flow"
    assert set(model["nodes"]) == {
        "__start__",
        "__end__",
        "orientation_booking_session",
        "persist_orientation_booking_once",
        "cancelled_result",
        "booked_result",
        "confirmation_branch",
    }
    session = model["nodes"]["orientation_booking_session"]
    assert set(session["nodes"]) == {
        "__start__",
        "__end__",
        "selected_slot",
        "proposed_orientation_booking",
        "review_selected_slot",
        "confirmed",
    }
    choice_field = session["nodes"]["selected_slot"]["spec"]["fields"][0]
    assert model_choice_list_from_field(choice_field) == APPROVED_SLOTS
    review_field = session["nodes"]["review_selected_slot"]["spec"]["fields"][0]
    assert review_field["text"] == "Selected slot: {parent.selected_slot.output.value}"
    assert sum(
        1
        for node in model["nodes"].values()
        if node["spec"].get("tool") == "persist_orientation_booking"
    ) == 1


def test_it_flow_source_remains_unmodified_regression_reference():
    source = Path("flows/it_request_flow.py").read_text(encoding="utf-8")
    assert "it_request_session" in source
    assert "persist_it_request_once" in source
    assert "orientation_booking" not in source
