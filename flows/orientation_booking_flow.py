from typing import Any, Callable

from pydantic import BaseModel

from ibm_watsonx_orchestrate.flow_builder.data_map import Assignment, DataMap
from ibm_watsonx_orchestrate.flow_builder.flows import END, START, Flow, flow
from ibm_watsonx_orchestrate.flow_builder.types import UserFieldKind

from tools.onboarding_persistence import persist_orientation_booking


ORIENTATION_SLOTS = (
    "Monday 09:00-10:00",
    "Wednesday 13:00-14:00",
    "Thursday 15:00-16:00",
)
SELECTED_SLOT_USER_FIELD = "Orientation slot"
CONFIRMED_USER_FIELD = "Book orientation session"
SESSION_SELECTED_SLOT = "parent.selected_slot.output.value"
SESSION_CONFIRMED = "parent.confirmed.output.value"
SESSION_OUTPUT_PREFIX = "flow.orientation_booking_session.output"


class OrientationBookingInput(BaseModel):
    pass


class OrientationBookingSessionOutput(BaseModel):
    selected_slot: str
    confirmed: bool


class OrientationBookingFields(BaseModel):
    selected_slot: str


class OrientationBookingResult(BaseModel):
    status: str
    persisted: bool
    selected_slot: str
    booking_id: str | None = None
    object_key: str | None = None
    verified: bool | None = None


def approved_orientation_slots() -> tuple[str, str, str]:
    return ORIENTATION_SLOTS


def is_approved_orientation_slot(selected_slot: str) -> bool:
    return selected_slot in ORIENTATION_SLOTS


def _slot_choices_map() -> DataMap:
    return DataMap(
        maps=[
            Assignment(
                target_variable="self.input.choices",
                value_expression=repr(list(ORIENTATION_SLOTS)),
            )
        ]
    )


def _session_output(field_name: str) -> str:
    return f"{SESSION_OUTPUT_PREFIX}.{field_name}"


def _clean_required(value: str, field_name: str) -> str:
    cleaned = value.strip() if isinstance(value, str) else ""
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def cancel_orientation_booking(selected_slot: str) -> dict[str, Any]:
    selected_slot = _clean_required(selected_slot, "selected_slot")
    return {
        "status": "cancelled",
        "persisted": False,
        "selected_slot": selected_slot,
        "booking_id": None,
        "object_key": None,
        "verified": None,
    }


def submit_orientation_booking(
    selected_slot: str,
    persist: Callable[..., Any] = persist_orientation_booking,
) -> dict[str, Any]:
    selected_slot = _clean_required(selected_slot, "selected_slot")
    response = persist(selected_slot=selected_slot)
    content = getattr(response, "content", response)
    return {
        "status": "booked",
        "persisted": True,
        "selected_slot": selected_slot,
        "booking_id": content["record_id"],
        "object_key": content["object_key"],
        "verified": content["verified"],
    }


def _configure_orientation_booking_flow(aflow: Flow) -> Flow:
    session = aflow.userflow(
        name="orientation_booking_session",
        display_name="Orientation Booking Session",
        input_schema=OrientationBookingInput,
        output_schema=OrientationBookingSessionOutput,
    )

    selected_slot = session.field(
        name="selected_slot",
        kind=UserFieldKind.Choice,
        display_name=SELECTED_SLOT_USER_FIELD,
        direction="input",
        text="Select an orientation slot.",
        input_map=_slot_choices_map(),
        required=True,
    )
    proposed = session.field(
        name="proposed_orientation_booking",
        kind=UserFieldKind.Text,
        direction="output",
        text="Proposed orientation booking",
    )
    review = session.field(
        name="review_selected_slot",
        kind=UserFieldKind.Text,
        direction="output",
        text="Selected slot: {parent.selected_slot.output.value}",
    )
    confirmed = session.field(
        name="confirmed",
        kind=UserFieldKind.Boolean,
        display_name=CONFIRMED_USER_FIELD,
        direction="input",
        text="Book this orientation session?",
        required=True,
    )

    session.sequence(START, selected_slot, proposed, review, confirmed, END)
    session.map_output("selected_slot", SESSION_SELECTED_SLOT)
    session.map_output("confirmed", SESSION_CONFIRMED)

    persist_once = aflow.tool(
        persist_orientation_booking,
        name="persist_orientation_booking_once",
        display_name="Persist Orientation Booking",
    )
    persist_once.map_input("selected_slot", _session_output("selected_slot"))

    cancelled = aflow.script(
        name="cancelled_result",
        description="Return a cancellation result without persistence.",
        input_schema=OrientationBookingFields,
        output_schema=OrientationBookingResult,
        script=(
            "self.output.status = 'cancelled'\n"
            "self.output.persisted = False\n"
            "self.output.selected_slot = self.input.selected_slot\n"
            "self.output.booking_id = None\n"
            "self.output.object_key = None\n"
            "self.output.verified = None\n"
        ),
    )
    cancelled.map_input("selected_slot", _session_output("selected_slot"))

    booked = aflow.script(
        name="booked_result",
        description="Return the booked orientation result using session and persistence outputs.",
        input_schema=OrientationBookingResult,
        output_schema=OrientationBookingResult,
        script=(
            "self.output.status = 'booked'\n"
            "self.output.persisted = True\n"
            "self.output.selected_slot = self.input.selected_slot\n"
            "self.output.booking_id = self.input.booking_id\n"
            "self.output.object_key = self.input.object_key\n"
            "self.output.verified = self.input.verified\n"
        ),
    )
    booked.map_input("selected_slot", _session_output("selected_slot"))
    booked.map_input("booking_id", "flow.persist_orientation_booking_once.output.record_id")
    booked.map_input("object_key", "flow.persist_orientation_booking_once.output.object_key")
    booked.map_input("verified", "flow.persist_orientation_booking_once.output.verified")

    confirmation_branch = aflow.branch(name="confirmation_branch")
    aflow.sequence(START, session, confirmation_branch)
    confirmation_branch.condition(
        persist_once,
        expression=_session_output("confirmed"),
    ).condition(cancelled, default=True)
    aflow.edge(persist_once, booked)
    aflow.edge(booked, END)
    aflow.edge(cancelled, END)

    for field_name in OrientationBookingResult.model_fields:
        aflow.map_output(
            field_name,
            (
                f"flow.booked_result.output.{field_name} if "
                f"{_session_output('confirmed')} else "
                f"flow.cancelled_result.output.{field_name}"
            ),
        )
    return aflow


@flow(
    name="orientation_booking_flow",
    display_name="Orientation Booking Flow",
    description="Select and confirm one approved onboarding orientation slot before persistence.",
    input_schema=OrientationBookingInput,
    output_schema=OrientationBookingResult,
)
def orientation_booking_flow(aflow: Flow) -> Flow:
    return _configure_orientation_booking_flow(aflow)


def build_orientation_booking_flow():
    return orientation_booking_flow()
