from pydantic import BaseModel, Field

from ibm_watsonx_orchestrate.flow_builder.flows import END, START, Flow, flow

from tools.support_triage_classifier import StructuredTicketOutput, classify_support_ticket_configured
from tools.support_triage_drafter import (
    apply_support_triage_policy,
    draft_support_response_configured,
    finalize_support_triage_record,
)


AUTO_ROUTE_EXPRESSION = "flow.apply_support_triage_policy.output.status == 'auto_route_pending'"


class SupportTriageInput(BaseModel):
    ticket_id: str = Field(min_length=1, max_length=64)
    ticket_text: str = Field(min_length=1, max_length=5000)


def _output_expr(field_name: str) -> str:
    return (
        f"flow.finalize_drafted_record.output.{field_name} if {AUTO_ROUTE_EXPRESSION} "
        f"else flow.finalize_skipped_record.output.{field_name}"
    )


def _configure_support_triage_flow(aflow: Flow) -> Flow:
    classify = aflow.tool(
        classify_support_ticket_configured,
        name="classify_support_ticket",
        display_name="Classify Support Ticket",
    )
    classify.map_input("ticket_id", "flow.input.ticket_id")
    classify.map_input("ticket_text", "flow.input.ticket_text")

    apply_policy = aflow.tool(
        apply_support_triage_policy,
        name="apply_support_triage_policy",
        display_name="Apply Support Triage Policy",
    )
    apply_policy.map_input("ticket_id", "flow.input.ticket_id")
    apply_policy.map_input("ticket_text", "flow.input.ticket_text")
    apply_policy.map_input("classifier_execution", "flow.classify_support_ticket.output")

    draft = aflow.tool(
        draft_support_response_configured,
        name="draft_support_response",
        display_name="Draft Support Response",
    )
    draft.map_input("ticket_id", "flow.input.ticket_id")
    draft.map_input("ticket_text", "flow.input.ticket_text")
    draft.map_input("assigned_team", "flow.apply_support_triage_policy.output.assigned_team")
    draft.map_input("sla", "flow.apply_support_triage_policy.output.sla")

    finalize_drafted = aflow.tool(
        finalize_support_triage_record,
        name="finalize_drafted_record",
        display_name="Finalize Drafted Support Triage Record",
    )
    finalize_drafted.map_input("pre_draft_output", "flow.apply_support_triage_policy.output")
    finalize_drafted.map_input("draft_execution", "flow.draft_support_response.output")

    finalize_skipped = aflow.tool(
        finalize_support_triage_record,
        name="finalize_skipped_record",
        display_name="Finalize Non-Drafted Support Triage Record",
    )
    finalize_skipped.map_input("pre_draft_output", "flow.apply_support_triage_policy.output")

    drafting_branch = aflow.branch(name="drafting_branch")
    aflow.sequence(START, classify, apply_policy, drafting_branch)
    drafting_branch.condition(draft, expression=AUTO_ROUTE_EXPRESSION).condition(
        finalize_skipped,
        default=True,
    )
    aflow.edge(draft, finalize_drafted)
    aflow.edge(finalize_drafted, END)
    aflow.edge(finalize_skipped, END)

    for field_name in StructuredTicketOutput.model_fields:
        aflow.map_output(field_name, _output_expr(field_name))

    return aflow


@flow(
    name="support_triage",
    display_name="Support Triage",
    description="Classify, review, route, optionally draft, and return one structured support-triage output.",
    input_schema=SupportTriageInput,
    output_schema=StructuredTicketOutput,
)
def support_triage(aflow: Flow) -> Flow:
    return _configure_support_triage_flow(aflow)


def build_support_triage_flow() -> Flow:
    return support_triage()
