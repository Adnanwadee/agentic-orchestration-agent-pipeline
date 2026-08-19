# Milestone 8 — Agent Versus Pipeline Reflection

Status: MILESTONE_8_AGENT_PIPELINE_REFLECTION=PASS

## Evidence-Based Comparison

Part A uses a ReAct Agent for conversational autonomy. The Agent decides what the user is asking
for, when to ask a clarifying question, and which approved capability to invoke. Bounded Flows
then control how side effects are performed: IT access requests and orientation bookings collect
required fields, show a review step, require explicit Yes/No confirmation, and persist only on
confirmed paths. This design fits ambiguous onboarding conversations because the user may move
between policy Q&A, IT access, booking, cancellation, and out-of-scope requests in one session.

Part B uses a Flow as the sole orchestrator. The LLM is bounded to classification and drafting;
deterministic code owns validation, human-review decisions, routing, unsupported-route handling,
and final structured output. This design fits repeatable ticket processing because every record
has the same contract and every unsafe or uncertain path can be contained without relying on the
model to decide policy.

## Where Autonomy Is Useful

Autonomy is useful when the user's intent is conversational and underspecified. In Part A, the
Agent can decide whether the user is asking a policy question, starting an IT request, booking
orientation, or asking for something outside scope. That autonomy is acceptable because the
side-effect boundaries are not left to the model alone; protected Flows enforce collection,
review, confirmation, cancellation, and persistence behavior.

## Where Deterministic Approval Or Routing Is Safer

Deterministic control is safer when the business outcome must be auditable and repeatable. In
Part B, the classifier can be wrong or uncertain, but it cannot invent review policy, routing
teams, SLAs, retries, or final statuses. Low confidence, secondary category, null urgency,
unsupported Account + Critical, invalid output, and execution errors all map to fixed containment
paths. Drafting is also bounded: the model supplies only a problem summary and deterministic code
adds the approved team/SLA text.

## Practical Conclusion

The Agent pattern is better for ambiguous multi-turn user assistance when protected workflows
own irreversible actions. The Pipeline pattern is better for high-volume operational processing
where structured records, deterministic policy, and consistent telemetry matter more than open
conversation. This project uses both patterns deliberately: autonomy at the conversational edge,
determinism at approval, routing, persistence, and structured-output boundaries.

## What Would Break If We Swapped Them?

If HR onboarding were implemented as one fixed Pipeline, the user-driven conversation would fit
poorly. Users can ask a policy question, switch to IT access, provide partial data, cancel,
request booking, change topic, or stop. A fixed sequence would either force irrelevant stages or
accumulate branching and state logic that recreates agent-like routing inside the Pipeline. This
does not mean Pipelines cannot support conversations; it means this particular onboarding
assistant needs flexible capability selection at the conversational edge. The bounded
deterministic Flows still remain the right mechanism inside the Agent for side-effect-sensitive
IT and booking actions.

If support triage were implemented as an open-ended Agent, the extra autonomy would add little
value to a known sequence: intake, classify, validate, route, optionally draft, and emit
structured output. The review/routing rules need to be repeatable and auditable. Unnecessary
autonomy could skip validation, invent routing or SLA decisions, or draft when review should
stop. This does not mean Agents are inherently unsafe; it means heavily constraining an Agent for
this fixed operational path would effectively recreate a workflow with less direct auditability.
