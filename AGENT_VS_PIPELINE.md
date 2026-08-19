# Agent Versus Pipeline


This report explains the architecture selection used in this project. It is based on the
implemented systems and approved evidence, not generic pattern claims alone.

## Agent Pattern In This Project

The Agent pattern is represented by `hr_onboarding_agent`, a native ReAct Core Agent in
watsonx Orchestrate. It handles multi-turn onboarding conversation and decides whether the user
is asking for policy information, IT access, orientation booking, clarification, cancellation,
completion, or something outside scope.

The Agent does not own irreversible side effects directly. IT requests and booking actions are
delegated to bounded Flows that collect fields, show review text, require explicit Yes/No
confirmation, and persist only on confirmed paths.

## Pipeline Pattern In This Project

The Pipeline pattern is represented by the `support_triage` Orchestrate Flow, implemented in
`flows/support_triage_flow.py`. It processes one ticket through a known fixed sequence: intake,
classify, validate/review, route, draft when allowed, and final structured output.

The LLM is bounded to two narrow jobs: classification and draft problem-summary generation.
Deterministic code owns taxonomy validation, threshold review, unsupported-route containment,
team/SLA mapping, draft composition, and terminal status.

## Part A Actual Architecture

Part A includes:

- `agents/hr_onboarding_agent.yaml`
- `knowledge/hr_policy_knowledge_base.yaml`
- `flows/it_request_flow.py`
- `flows/orientation_booking_flow.py`
- `tools/onboarding_persistence.py`

The Agent can move between policy Q&A, IT request, booking, out-of-scope handling, and exit in
one session. Explicit state is carried through Flow fields and persistence payloads rather than
relying only on model memory.

## Part B Actual Architecture

Part B includes:

- `flows/support_triage_flow.py`
- `tools/support_triage_classifier.py`
- `tools/support_triage_drafter.py`
- `data/support_tickets_*.json`

The Pipeline emits structured terminal paths for auto-route, human review, invalid classifier
output, classifier execution error, and draft failure. The confidence threshold is `0.80`.

## Autonomy Boundaries

Autonomy is allowed where the problem is conversational. The HR Agent can interpret user
intent, choose Policy Q&A / IT Request / Orientation Booking, ask clarifying questions, and
decide when the conversation is complete.

Autonomy is constrained where correctness and side effects matter. The HR Agent cannot bypass
IT confirmation, bypass booking confirmation, or directly persist side effects outside the
protected Flow behavior. Support triage routing, SLA selection, review decisions, and structured
output are deterministic Pipeline responsibilities.

## Confirmation And Human Review Boundaries

Part A uses confirmation boundaries. IT and booking Flows review the collected values and
require explicit Yes/No confirmation before persistence. No/cancel paths create zero records.

Part B uses human-review boundaries for classifier/routing uncertainty: low confidence,
secondary category, null urgency, unsupported route, invalid output, and classifier execution
error. A drafter failure after a valid automatic route becomes `draft_failed`; it prevents a
completed automatic customer response without changing the routing decision or creating a new
Human Review trigger.

## State Handling

Part A state is explicit in Flow inputs, UserFlow fields, review text, confirmation branches,
and COS records. This prevents important business fields from existing only in LLM memory.

Part B state is explicit in classification objects, review reasons, route decisions, draft
status, telemetry, and terminal output records.

## Determinism And Auditability

The Agent is less deterministic at the conversational edge, but its side effects are bounded by
deterministic Flow behavior and persistence checks.

The Pipeline is deterministic where policy matters. A model can be uncertain or wrong, but it
cannot invent categories outside the schema, make unsupported route decisions, bypass review, or
change the final terminal contract.

## Cost And Reliability Implications

Part A spends model effort where conversation and intent resolution are valuable. Human approval
and bounded Flows reduce the risk of unintended writes.

Part B limits model work to classification and drafting. Deterministic routing/review makes
telemetry, cost, and failure behavior easier to measure across many tickets.

## Failure-Mode Differences

Agent failure modes are centered on conversational ambiguity, missing inputs, tool selection,
side-effect confirmation, out-of-scope requests, and loop pressure.

Pipeline failure modes are centered on invalid structured output, taxonomy drift,
low-confidence classification, unsupported route combinations, null urgency, drafter failure,
and generic draft quality.

## What Would Break If We Swapped Them?

### Onboarding As Fixed Pipeline

Onboarding would fit poorly as one fixed Pipeline because the user controls the order. A user can
ask a policy question, switch to IT access, provide incomplete data, cancel, ask about
orientation, book a slot, change topic, or stop. A fixed sequence would either force irrelevant
stages or accumulate branching logic for topic switching, incomplete data, cancellation, and
clarification. At that point the Pipeline would be re-creating Agent routing inside workflow
logic.

This does not mean Pipelines cannot converse. It means this onboarding use case needs flexible
capability selection at the conversational edge.

### Support Triage As Open-Ended Agent

Support triage already has a known sequence. An open-ended Agent would add risk without adding
useful autonomy: it might skip validation, invent routing or SLA values, draft when review
should stop, or return inconsistent terminal structures.

Heavily restricting that Agent would effectively recreate the current workflow, but with less
direct auditability.

This does not mean Agents are inherently unsafe. It means deterministic approval, review,
routing, and final-output rules are the safer fit for this operational path.

## Selection Rule

Use an Agent when the value is flexible multi-turn intent handling and capability selection, and
put irreversible actions behind deterministic approval boundaries.

Use a Pipeline when the sequence, validation, routing, and terminal outcomes are known in
advance and must be repeatable, measurable, and auditable.
