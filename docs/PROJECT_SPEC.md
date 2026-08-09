# Project Specification

Status: G0 control-plane specification
Selected model: `PENDING_G1`

This document is the technical source of truth for the supervised Agentic Orchestration —
Agent + Pipeline project. It separates supervisor requirements from approved engineering
decisions, platform facts that must govern implementation, explicit fallbacks, non-goals,
and acceptance criteria. It contains no implementation code.

## System overview

The project demonstrates two orchestration patterns on IBM watsonx.ai and watsonx
Orchestrate:

- Part A is a conversational HR onboarding Agent with grounded policy knowledge and two
  confirmation-protected side-effect capabilities.
- Part B is a support-triage Flow that uses an LLM only for bounded classification and
  response drafting, while deterministic policy controls review and routing.

Development proceeds through the six gates in `docs/EXECUTION_PLAN.md`. Evidence progresses
from implementation to local validation, required remote/platform validation, observed
business outcome, and supervisor approval. A file or implementation alone is not completion.

# A. Original project requirements

This section contains only requirements supplied by the original project task. The approved
implementation-specific interpretations and contracts are separately recorded in section B.

## A1. Part A — HR onboarding Agent

The completed Agent must provide:

1. A conversational interface.
2. Retrieval-backed HR policy question answering using these five supplied mock documents:
   - `benefits-and-compensation.md`
   - `code-of-conduct.md`
   - `it-access-policy.md`
   - `leave-policy.md`
   - `new-hire-orientation-guide.md`
3. An IT access-request capability.
4. An orientation-session booking capability; its available slots may be hardcoded.
5. Explicit confirmation before any side effect.

An IT request must collect employee name, employee role, and required systems. The Agent must
ask for missing values and must never invent them. Both IT request submission and orientation
booking require confirmation before persistence.

The complete Agent must support multi-turn conversation, policy Q&A, IT access requests,
orientation booking, missing-information follow-up, confirmation, graceful out-of-scope
handling, and a clear completion/exit behavior.

## A2. Part B — support-triage Pipeline

The Pipeline must perform this sequence:

Ticket intake → classification → validation/human-review decision → routing → personalized
first-response drafting when eligible → structured output.

The classification taxonomy is closed:

- `category`: `billing`, `technical`, `account`, or `general`.
- `urgency`: `low`, `medium`, `high`, or `critical`.

The classifier must return:

- `category`;
- `urgency`;
- numeric `confidence` from 0.0 through 1.0 inclusive;
- short `reasoning` or `rationale`.

Low-confidence tickets must be sent to human review. Routing, response drafting, and the final
result must be represented in structured output.

## A3. Supplied routing table

The following externally supplied business routing table is authoritative:

| Category | Urgency | Assigned team | SLA |
|---|---|---|---|
| Billing | Critical | Billing — Senior | 1 hour |
| Billing | High | Billing — Standard | 4 hours |
| Billing | Medium | Billing — Standard | 1 business day |
| Billing | Low | Billing — Standard | 3 business days |
| Technical | Critical | Engineering — On-call | 30 minutes |
| Technical | High | Engineering — Support | 2 hours |
| Technical | Medium | Engineering — Support | 1 business day |
| Technical | Low | Engineering — Backlog | 5 business days |
| Account | High | Customer Success | 4 hours |
| Account | Medium | Customer Success | 1 business day |
| Account | Low | Customer Success | 3 business days |
| General | Any | Customer Success | 2 business days |
| Human Review | N/A | Triage — Human | Immediate |

The table intentionally supplies no Account + Critical route. Section B records the approved
handling decision for that absent combination.

## A4. Quality, failure-mode, and evaluation requirements

Automatically routed tickets require a visibly personalized first response. Every ticket must
receive structured output. Required acceptance is category accuracy of at least 80% and urgency
accuracy of at least 75%, including eventual evaluation of the complete ticket test set.

Each system must document at least three meaningful failure scenarios and address/fix at least
two failure modes. Project evaluation must include regression evidence, category and urgency
accuracy, review and automatic-routing behavior, latency, token usage when available, estimated
cost per ticket, and estimated implication at 1,000 tickets/day. The project must close with an
Agent-versus-Pipeline architectural comparison and an Agent autonomy-versus-approval reflection.

# B. Approved engineering decisions

These are project architecture decisions, not restatements of externally supplied
requirements. They remain frozen unless a documented capability test activates an explicit
fallback or a supervisor approves a change.

## B1. Part A architecture

The primary architecture is a native watsonx Orchestrate HR Agent in the default Agent style,
with:

- a native HR Policy Knowledge Base;
- an IT Request capability/workflow;
- an Orientation Booking capability/workflow; and
- remote mock persistence behind the two side-effect capabilities.

Default style is selected because the capability set is small and clearly bounded. ReAct is
understood as an iterative reason/action/observation approach useful for open-ended tool
selection, but a ReAct runtime is not required merely for appearance and is not selected for
this bounded Agent.

Native watsonx Orchestrate Knowledge Base is the primary grounding strategy. Custom RAG is
not a parallel implementation and is available only through the fallback in D1.

## B2. Agent instruction and capability contract

The Agent is an HR onboarding assistant with exactly these supported capabilities:

1. Answer HR policy questions using the HR Policy Knowledge Base.
2. Process actual IT/software/system access requests through the IT Request capability.
3. Book orientation sessions through the Orientation Booking capability.

The Agent must follow these approved behavior rules:

- Ground HR policy answers in the HR Policy Knowledge Base and do not invent policy.
- Do not invent missing employee or request information; ask for it.
- Use the IT Request capability only for an actual request for IT/software/system access.
- Use the Orientation Booking capability only for an actual scheduling request.
- Never bypass the confirmation required before a side effect.
- Politely decline requests outside HR onboarding scope.
- After a successful submission or booking, do not repeat the side effect unless the user
  explicitly starts a new request.
- Clearly report completion and provide a clear conversational exit.

Capability descriptions must not overlap:

- **Policy Knowledge:** Use only for questions about HR policy, leave, benefits,
  compensation, code of conduct, IT access policy, and orientation guidance. Do not use it to
  create requests or bookings.
- **IT Request:** Use only when the user actually wants IT/software/system access. Do not use
  it merely to explain what an IT policy says.
- **Orientation Booking:** Use only when the user wants to schedule or book orientation. Do
  not use it merely for general orientation-information questions.

## B3. Confirmation and conversational state

The primary design uses watsonx Orchestrate Flow/User Activity behavior to enforce the state
transition around both side effects:

collect required values → retain values across turns → present the complete proposed action →
ask for explicit confirmation → branch Yes/No → persist only on Yes.

Prompt-only confirmation is unacceptable. One cancelled action must create zero records, and
one confirmed action must create exactly one record. The Agent must not autonomously repeat a
completed side effect unless the user explicitly starts a new request.

G1 must test the minimal sequence “ask for a value → retain the value → ask for confirmation
→ branch Yes/No” before either production capability is built.

Storage-level replay/idempotency protection is a production consideration, not a required
implementation or acceptance criterion for this training project.

## B4. Remote persistence

IBM Cloudant Lite is the primary mock persistence service. The minimal design uses one
database, `onboarding_mock`, with document types `it_request` and `orientation_booking`.
Remote credentials are supplied at runtime through Watson/Orchestrate connections and are
never committed.

The design intentionally has no ORM, migrations, repository framework, PostgreSQL, Redis, or
unnecessary storage abstraction. Exact minimal document fields are frozen in G2 after G1 proves
the tenant-compatible Cloudant transport.

## B5. Part B architecture

The watsonx Orchestrate Flow remains the sole orchestrator. Its stage ownership is:

- deterministic intake and schema validation;
- an LLM-backed classifier producing only the classification contract;
- deterministic bounded invalid-output handling and review policy;
- deterministic table lookup for routing;
- an LLM drafting call only for automatically routed tickets; and
- deterministic structured-output assembly for every path.

The preferred LLM integration is Prompt Node, subject to the G1 proof in D3. This is not a
standalone Python pipeline. The review threshold is not chosen in G0.

## B6. Extended classifier contract

The approved structured classifier output adds `secondary_category`, which is optional. It also
permits `urgency = null` only when urgency genuinely cannot be determined; `unknown` is not a
fifth urgency label. The classifier therefore returns category, optional secondary category,
nullable urgency under that narrow rule, numeric confidence from 0.0 to 1.0 inclusive, and a
short rationale.

The classifier must not produce or decide `review_required`. A deterministic policy owns that
decision. Category/urgency enum validity, confidence bounds, nullable semantics, rationale, and
the absence of classifier-owned review state are validated with Pydantic and tests.

## B7. Deterministic review policy

Human review is required when any one of these approved conditions is true:

- classifier confidence is below the frozen calibrated threshold;
- `secondary_category` is not null;
- `urgency` is null;
- structured classification remains invalid after the bounded invalid-output policy; or
- the category/urgency combination has no supported route.

All human-review paths route to `Triage — Human` with an `Immediate` SLA. Human-review tickets
must not consume a response-drafting call. No LLM may invent review or routing rules.

## B8. Routing interpretation and required edge cases

Routing is deterministic and case-normalized for lookup. The supplied `General + Any` row is
implemented for each supported urgency (`low`, `medium`, `high`, and `critical`), always routing
to Customer Success with a 2-business-day SLA.

There is no supplied Account + Critical route. The approved behavior is human review; no team or
SLA may be invented.

- **Ticket 9:** It contains Account and Billing work. The approved classification is
  `category = account`, `secondary_category = billing`, `urgency = medium`. The secondary
  category requires human review; automatic routing is forbidden.
- **Ticket 10:** For `it doesnt work fix it`, the approved classification is
  `category = technical`, `secondary_category = null`, `urgency = null`, with low confidence.
  Null expresses insufficient urgency information without changing the taxonomy. Both null
  urgency and low confidence require human review. Evaluation reports this unknown-urgency
  behavior explicitly rather than disguising it as normal urgency classification.

## B9. Bounded invalid-output policy

G3 must implement and test a small, deterministic, bounded policy rather than an unbounded
retry loop. Its exact retry/repair count is frozen with the G3 classifier design. Regardless
of that count, if the structured classification remains invalid when the bound is exhausted,
the ticket must go to human review, must not be automatically routed, must not invoke drafting,
and must still receive a structured output record describing the invalid state.

## B10. Drafting and structured-output contracts

Drafting occurs only after automatic routing. A draft must reference the customer's actual
problem, be visibly personalized, use an appropriate professional tone, remain consistent with
the assigned team and SLA, and never claim a resolution or action that did not occur. A generic
acknowledgement alone is insufficient.

Ticket intake preserves a stable ticket identifier and original text. Ground truth separately
stores expected category, optional secondary category, and nullable urgency. Every path produces
one structured record containing at minimum the ticket reference, normalized classification and
validation status, deterministic review value and reasons, assigned team/SLA, a draft only when
automatically routed, and error/status metadata for bounded invalid-output handling. No ticket is
silently dropped. Exact field names and schemas are finalized in G3 without changing these
semantics.

## B11. Evaluation strategy

The approved target dataset contains 30 tickets: 15 development/calibration and 15 held-out
final tickets. Originally supplied tickets remain represented. Ground-truth labels become
immutable once classifier evaluation starts and must never be changed to improve results.

The approved process is:

Initial classifier → development-set evaluation → at most one meaningful classifier improvement
cycle → threshold candidate evaluation → freeze model, prompt, and threshold → held-out/final
evaluation → complete ticket-set evaluation.

Initial threshold candidates are exactly 0.50, 0.60, 0.70, and 0.80. Selection follows observed
development behavior rather than intuition. In addition to the original evaluation requirements,
report Ticket 10 unknown-urgency handling explicitly, human-review rate, auto-route rate,
auto-route correctness, latency, token usage when available, estimated cost per ticket, and the
estimated implication at 1,000 tickets/day.

## B12. Model-selection policy

Selected model: `PENDING_G1`.

G1 must list the models actually available in the Watson environment, then select one suitable
available model for the project. Formal benchmarking is avoided unless that selected model
fails the required quality targets. Once supported by real tenant evidence, the chosen model
is recorded and frozen with the Part B LLM mode.

# C. Watson platform constraints

The following constraints govern implementation and must be verified where they depend on the
actual tenant:

- Local project runtime: Python 3.11.
- Remote watsonx Orchestrate Python-tool runtime: Python 3.12.
- Remote Python-tool filesystem: read-only; remote local-file persistence is forbidden.
- Third-party packages are avoided unless required. Every approved dependency must be pinned
  to an exact version, and package/version compatibility must be verified against the Watson
  tenant before dependent logic is implemented.
- Tool and remote Python filenames use only safe alphanumeric characters and underscores.
- Remote tool packages remain well below the Watson compressed-package limit.
- Prompt Node is an unproven tenant capability until the G1 spike succeeds; documentation
  alone is not evidence.
- Remote Orchestrate, watsonx.ai, native Knowledge Base, User Activity, and Cloudant behavior
  may be claimed only after direct observation with recorded evidence.

Remote validation is performed at meaningful component boundaries: a focused batch for the IT
flow, a focused batch for the booking flow, and one final end-to-end batch for the complete
Agent, rather than after every local edit.

# D. Explicit fallbacks and their boundaries

These fallbacks are approved engineering decisions for conditional paths, not authorization
to implement parallel architectures.

## D1. Knowledge fallback

Primary: native watsonx Orchestrate Knowledge Base. If answer quality materially fails after
one reasonable tuning attempt, stop, preserve evidence, and request supervisor approval to
activate custom RAG. Do not build custom RAG preemptively.

## D2. User Activity fallback

Primary: User Activity collects/retains values and enforces confirmation. If the G1 tenant
spike shows that behavior is unsuitable, the Agent may collect missing fields conversationally
and pass a complete payload to a small confirmation workflow before persistence. The workflow,
not a prompt alone, must still protect the side effect. Freeze the chosen strategy in G1.

## D3. Prompt Node fallback

G1 must run a minimal real flow: input → Prompt Node → strict structured output → end.

- If reliable in the actual tenant, freeze `PIPELINE_LLM_MODE = PROMPT_NODE`.
- If unreliable, freeze `PIPELINE_LLM_MODE = PYTHON_WATSONX_TOOL` and use a Python LLM tool
  that calls watsonx.ai, validates the structured result, and returns control to the Flow.

The fallback does not authorize a second standalone Python pipeline; the Flow remains the
orchestrator.

## D4. Cloudant transport/dependency fallback boundary

G1 must prove a real write/read and determine the smallest tenant-compatible transport. If the
preferred client/package is incompatible, stop and select a minimal compatible transport with
supervisor approval. Do not introduce a general persistence layer or unrelated datastore.

# E. Frozen non-goals

Unless a proven requirement or failure forces reconsideration and a supervisor approves it,
the following are out of scope:

- LangChain or LangGraph;
- a custom Python Agent runtime or multi-agent architecture;
- FastAPI, Streamlit, or a React frontend;
- Docker or local Orchestrate Developer Edition;
- PostgreSQL, Redis, or a custom vector database unless native KB materially fails under D1;
- CI/CD or watsonx.governance implementation;
- sentiment analysis or duplicate-ticket detection;
- batch CSV processing;
- production authentication;
- real HR, IT, or calendar integrations;
- booking concurrency/race-condition implementation;
- formal model benchmarking unless the selected model fails quality targets;
- unnecessary framework or abstraction layers.

# F. Acceptance criteria

## F1. Part A acceptance

Observed evidence must prove:

- one full onboarding conversation includes policy Q&A, an IT request, and orientation booking;
- policy answers are grounded and unknown-policy questions abstain rather than hallucinate;
- missing required IT information triggers follow-up and is not invented;
- explicit confirmation occurs before IT submission;
- IT cancellation creates no record and confirmation creates exactly one record;
- explicit confirmation occurs before orientation booking;
- booking cancellation creates no record and confirmation creates exactly one record;
- out-of-scope requests are handled gracefully; and
- the conversation has clear completion/exit behavior, and the Agent does not autonomously
  repeat a completed side effect unless the user explicitly starts a new request.

## F2. Part B acceptance

Observed evaluation evidence must prove:

- category accuracy is at least 80%;
- urgency accuracy is at least 75%, with Ticket 10 null-urgency handling separately reported;
- low-confidence and every other policy-triggering case goes to human review;
- Account + Critical never receives an invented automatic route;
- automatically routed responses are visibly personalized and contract-compliant;
- human-review tickets consume no drafting call; and
- every ticket receives a structured output record.

## F3. Whole-project acceptance

The project must additionally provide:

- at least three documented failure scenarios for each system;
- at least two addressed/fixed failure modes for each system;
- regression and full ticket-set evidence;
- latency, token usage when available, estimated cost per ticket, and estimated implication at
  1,000 tickets/day;
- an Agent autonomy-versus-approval reflection; and
- a closing architectural comparison of Agent versus Pipeline.

All required remote behaviors and business outcomes remain MANUAL checkpoints until a human
supervisor supplies evidence. Final acceptance, gate advancement, and delivery approval are
human decisions.
