from typing import Any, Callable

from pydantic import BaseModel

from ibm_watsonx_orchestrate.flow_builder.flows import END, START, Flow, flow
from ibm_watsonx_orchestrate.flow_builder.types import UserFieldKind

from tools.onboarding_persistence import persist_it_request


REQUIRED_IT_FIELDS = ("employee_name", "employee_role", "required_systems")
EMPLOYEE_NAME_USER_FIELD = "Employee name"
EMPLOYEE_ROLE_USER_FIELD = "Employee role"
REQUIRED_SYSTEMS_USER_FIELD = "Required systems"
CONFIRMED_USER_FIELD = "Submit IT access request"
TOP_LEVEL_INPUT_PREFIX = "flow.input"

AUTHORITATIVE_EMPLOYEE_NAME = (
    "flow.input.employee_name if flow.input.employee_name and "
    "flow.input.employee_name.strip() else parent.employee_name.output.value"
)
AUTHORITATIVE_EMPLOYEE_ROLE = (
    "flow.input.employee_role if flow.input.employee_role and "
    "flow.input.employee_role.strip() else parent.employee_role.output.value"
)
AUTHORITATIVE_REQUIRED_SYSTEMS = (
    "flow.input.required_systems if flow.input.required_systems and "
    "flow.input.required_systems.strip() else parent.required_systems.output.value"
)
SESSION_CONFIRMED = "parent.confirmed.output.value"
SESSION_OUTPUT_PREFIX = "flow.it_request_session.output"


class ITRequestInput(BaseModel):
    employee_name: str | None = None
    employee_role: str | None = None
    required_systems: str | None = None


class ITRequestDraft(BaseModel):
    employee_name: str = ""
    employee_role: str = ""
    required_systems: str = ""
    missing_fields: list[str] = []


class ITRequestFields(BaseModel):
    employee_name: str
    employee_role: str
    required_systems: str


class ITRequestSessionOutput(ITRequestFields):
    confirmed: bool


class ITRequestResult(BaseModel):
    status: str
    persisted: bool
    employee_name: str
    employee_role: str
    required_systems: str
    request_id: str | None = None
    object_key: str | None = None
    verified: bool | None = None


def _clean(value: str | None) -> str:
    return value.strip() if isinstance(value, str) else ""


def normalize_it_request_input(
    employee_name: str | None = None,
    employee_role: str | None = None,
    required_systems: str | None = None,
) -> ITRequestDraft:
    draft = ITRequestDraft(
        employee_name=_clean(employee_name),
        employee_role=_clean(employee_role),
        required_systems=_clean(required_systems),
    )
    draft.missing_fields = missing_required_fields(draft)
    return draft


def missing_required_fields(state: ITRequestDraft | dict[str, Any]) -> list[str]:
    values = state if isinstance(state, dict) else state.model_dump()
    return [field for field in REQUIRED_IT_FIELDS if not _clean(values.get(field))]


def merge_collected_values(
    state: ITRequestDraft,
    collected: dict[str, str],
) -> ITRequestDraft:
    data = state.model_dump()
    for field in REQUIRED_IT_FIELDS:
        if data[field]:
            continue
        if field in collected:
            data[field] = _clean(collected[field])
    merged = ITRequestDraft(**{field: data[field] for field in REQUIRED_IT_FIELDS})
    merged.missing_fields = missing_required_fields(merged)
    return merged


def confirmation_summary(state: ITRequestDraft) -> str:
    complete = normalize_it_request_input(
        state.employee_name,
        state.employee_role,
        state.required_systems,
    )
    if complete.missing_fields:
        raise ValueError("Cannot confirm IT request with missing required fields")
    return (
        "Proposed IT request: "
        f"employee_name={complete.employee_name}; "
        f"employee_role={complete.employee_role}; "
        f"required_systems={complete.required_systems}"
    )


def cancel_it_request(state: ITRequestDraft) -> dict[str, Any]:
    confirmation_summary(state)
    return {
        "status": "cancelled",
        "persisted": False,
        "employee_name": state.employee_name,
        "employee_role": state.employee_role,
        "required_systems": state.required_systems,
    }


def submit_it_request(
    state: ITRequestDraft,
    persist: Callable[..., Any] = persist_it_request,
) -> dict[str, Any]:
    confirmation_summary(state)
    response = persist(
        employee_name=state.employee_name,
        employee_role=state.employee_role,
        required_systems=state.required_systems,
    )
    content = getattr(response, "content", response)
    return {
        "status": "submitted",
        "persisted": True,
        "employee_name": state.employee_name,
        "employee_role": state.employee_role,
        "required_systems": state.required_systems,
        "request_id": content["record_id"],
        "object_key": content["object_key"],
        "verified": content["verified"],
    }


def _missing_input_expression(field_name: str) -> str:
    return f"not {TOP_LEVEL_INPUT_PREFIX}.{field_name} or not {TOP_LEVEL_INPUT_PREFIX}.{field_name}.strip()"


def _supplied_input_expression(field_name: str) -> str:
    return f"{TOP_LEVEL_INPUT_PREFIX}.{field_name} and {TOP_LEVEL_INPUT_PREFIX}.{field_name}.strip()"


def _session_output(field_name: str) -> str:
    return f"{SESSION_OUTPUT_PREFIX}.{field_name}"


def _configure_it_request_flow(aflow: Flow) -> Flow:
    session = aflow.userflow(
        name="it_request_session",
        display_name="IT Request Session",
        input_schema=ITRequestInput,
        output_schema=ITRequestSessionOutput,
    )

    need_name = session.branch(name="need_employee_name")
    employee_name = session.field(
        name="employee_name",
        kind=UserFieldKind.Text,
        display_name=EMPLOYEE_NAME_USER_FIELD,
        direction="input",
        text="What is the employee name for this IT access request?",
        required=True,
    )
    need_role = session.branch(name="need_employee_role")
    employee_role = session.field(
        name="employee_role",
        kind=UserFieldKind.Text,
        display_name=EMPLOYEE_ROLE_USER_FIELD,
        direction="input",
        text="What is the employee role for this IT access request?",
        required=True,
    )
    need_systems = session.branch(name="need_required_systems")
    required_systems = session.field(
        name="required_systems",
        kind=UserFieldKind.Text,
        display_name=REQUIRED_SYSTEMS_USER_FIELD,
        direction="input",
        text="Which systems, software, or tools are required?",
        required=True,
    )

    proposed = session.field(
        name="proposed_it_request",
        kind=UserFieldKind.Text,
        direction="output",
        text="Proposed IT access request",
    )
    review_name_source = session.branch(name="review_employee_name_source")
    review_name_from_input = session.field(
        name="review_employee_name_from_input",
        kind=UserFieldKind.Text,
        direction="output",
        text="Employee name: {flow.input.employee_name}",
    )
    review_name_from_collected = session.field(
        name="review_employee_name_from_collected",
        kind=UserFieldKind.Text,
        direction="output",
        text="Employee name: {parent.employee_name.output.value}",
    )
    review_role_source = session.branch(name="review_employee_role_source")
    review_role_from_input = session.field(
        name="review_employee_role_from_input",
        kind=UserFieldKind.Text,
        direction="output",
        text="Employee role: {flow.input.employee_role}",
    )
    review_role_from_collected = session.field(
        name="review_employee_role_from_collected",
        kind=UserFieldKind.Text,
        direction="output",
        text="Employee role: {parent.employee_role.output.value}",
    )
    review_systems_source = session.branch(name="review_required_systems_source")
    review_systems_from_input = session.field(
        name="review_required_systems_from_input",
        kind=UserFieldKind.Text,
        direction="output",
        text="Required systems: {flow.input.required_systems}",
    )
    review_systems_from_collected = session.field(
        name="review_required_systems_from_collected",
        kind=UserFieldKind.Text,
        direction="output",
        text="Required systems: {parent.required_systems.output.value}",
    )
    confirmed = session.field(
        name="confirmed",
        kind=UserFieldKind.Boolean,
        display_name=CONFIRMED_USER_FIELD,
        direction="input",
        text="Submit this IT access request?",
        required=True,
    )

    session.edge(START, need_name)
    need_name.condition(
        employee_name,
        expression=_missing_input_expression("employee_name"),
    ).condition(need_role, default=True)
    session.edge(employee_name, need_role)
    need_role.condition(
        employee_role,
        expression=_missing_input_expression("employee_role"),
    ).condition(need_systems, default=True)
    session.edge(employee_role, need_systems)
    need_systems.condition(
        required_systems,
        expression=_missing_input_expression("required_systems"),
    ).condition(proposed, default=True)
    session.edge(required_systems, proposed)
    session.edge(proposed, review_name_source)
    review_name_source.condition(
        review_name_from_input,
        expression=_supplied_input_expression("employee_name"),
    ).condition(review_name_from_collected, default=True)
    session.edge(review_name_from_input, review_role_source)
    session.edge(review_name_from_collected, review_role_source)
    review_role_source.condition(
        review_role_from_input,
        expression=_supplied_input_expression("employee_role"),
    ).condition(review_role_from_collected, default=True)
    session.edge(review_role_from_input, review_systems_source)
    session.edge(review_role_from_collected, review_systems_source)
    review_systems_source.condition(
        review_systems_from_input,
        expression=_supplied_input_expression("required_systems"),
    ).condition(review_systems_from_collected, default=True)
    session.edge(review_systems_from_input, confirmed)
    session.edge(review_systems_from_collected, confirmed)
    session.sequence(confirmed, END)

    session.map_output("employee_name", AUTHORITATIVE_EMPLOYEE_NAME)
    session.map_output("employee_role", AUTHORITATIVE_EMPLOYEE_ROLE)
    session.map_output("required_systems", AUTHORITATIVE_REQUIRED_SYSTEMS)
    session.map_output("confirmed", SESSION_CONFIRMED)

    persist_once = aflow.tool(
        persist_it_request,
        name="persist_it_request_once",
        display_name="Persist IT Request",
    )
    for field_name in REQUIRED_IT_FIELDS:
        persist_once.map_input(field_name, _session_output(field_name))

    cancelled = aflow.script(
        name="cancelled_result",
        description="Return a cancellation result without persistence.",
        input_schema=ITRequestFields,
        output_schema=ITRequestResult,
        script=(
            "self.output.status = 'cancelled'\n"
            "self.output.persisted = False\n"
            "self.output.employee_name = self.input.employee_name\n"
            "self.output.employee_role = self.input.employee_role\n"
            "self.output.required_systems = self.input.required_systems\n"
            "self.output.request_id = None\n"
            "self.output.object_key = None\n"
            "self.output.verified = None\n"
        ),
    )
    for field_name in REQUIRED_IT_FIELDS:
        cancelled.map_input(field_name, _session_output(field_name))

    submitted = aflow.script(
        name="submitted_result",
        description="Return the submitted IT request result using session and persistence outputs.",
        input_schema=ITRequestResult,
        output_schema=ITRequestResult,
        script=(
            "self.output.status = 'submitted'\n"
            "self.output.persisted = True\n"
            "self.output.employee_name = self.input.employee_name\n"
            "self.output.employee_role = self.input.employee_role\n"
            "self.output.required_systems = self.input.required_systems\n"
            "self.output.request_id = self.input.request_id\n"
            "self.output.object_key = self.input.object_key\n"
            "self.output.verified = self.input.verified\n"
        ),
    )
    for field_name in REQUIRED_IT_FIELDS:
        submitted.map_input(field_name, _session_output(field_name))
    submitted.map_input("request_id", "flow.persist_it_request_once.output.record_id")
    submitted.map_input("object_key", "flow.persist_it_request_once.output.object_key")
    submitted.map_input("verified", "flow.persist_it_request_once.output.verified")

    confirmation_branch = aflow.branch(name="confirmation_branch")
    aflow.sequence(START, session, confirmation_branch)
    confirmation_branch.condition(
        persist_once,
        expression=_session_output("confirmed"),
    ).condition(cancelled, default=True)
    aflow.edge(persist_once, submitted)
    aflow.edge(submitted, END)
    aflow.edge(cancelled, END)

    for field_name in ITRequestResult.model_fields:
        aflow.map_output(
            field_name,
            (
                f"flow.submitted_result.output.{field_name} if "
                f"{_session_output('confirmed')} else "
                f"flow.cancelled_result.output.{field_name}"
            ),
        )
    return aflow


@flow(
    name="it_request_flow",
    display_name="IT Request Flow",
    description="Collect and confirm a bounded onboarding IT access request before persistence.",
    input_schema=ITRequestInput,
    output_schema=ITRequestResult,
)
def it_request_flow(aflow: Flow) -> Flow:
    return _configure_it_request_flow(aflow)


def build_it_request_flow():
    return it_request_flow()
