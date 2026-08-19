# System Architecture

## Objective

The project demonstrates two orchestration patterns on IBM watsonx.ai and IBM watsonx
Orchestrate: a conversational Agent for HR onboarding and a deterministic Pipeline for support
triage.

## Part A: HR Onboarding Agent

`hr_onboarding_agent` is a native ReAct Core Agent. It owns conversational intent selection:
policy Q&A, IT access request, orientation booking, clarification, out-of-scope handling, and
completion/exit.

Side-effect paths are delegated to bounded Flows:

- [flows/it_request_flow.py](../flows/it_request_flow.py)
- [flows/orientation_booking_flow.py](../flows/orientation_booking_flow.py)

Those Flows collect explicit state, show review text, require Yes/No confirmation, and persist
only on confirmed paths.

## Part B: Support Triage Pipeline

The Part B Orchestrate Flow runtime name is `support_triage`, implemented in
[flows/support_triage_flow.py](../flows/support_triage_flow.py).

The Pipeline sequence is fixed:

```text
intake -> classify -> validate/review -> route -> draft when eligible -> structured output
```

The classifier and drafter use watsonx.ai through Python tools. Deterministic code owns review
rules, routing, unsupported-route containment, draft composition, and terminal statuses.

## Knowledge Strategy

The HR policy Knowledge Base uses five approved mock HR documents:

- leave policy;
- IT access policy;
- code of conduct;
- benefits and compensation;
- new-hire orientation guidance.

The Markdown files in [mock_docs/](../mock_docs/) remain authoritative. Byte-identical `.txt`
representations in [knowledge/sources/](../knowledge/sources/) are used for native Knowledge
Base ingestion.

## Persistence Strategy

IT requests and orientation bookings use IBM Cloud Object Storage as the approved mock/simple
store. Runtime credentials are provided through the Orchestrate `cos_onboarding`
`api_key_auth` connection. Persistence stores bounded JSON objects and uses IBM IAM token
exchange plus COS REST through Python standard-library HTTP.

## Human-In-The-Loop Boundaries

Part A requires explicit confirmation before IT request or booking persistence.

Part B requires Human Review for classifier/routing uncertainty and unsupported routing
conditions. Invalid classifier output and classifier execution errors are human-contained. A
drafter failure after a valid automatic route becomes `draft_failed`; it does not change routing
or create a new Human Review trigger.

## State Management

Critical state is explicit in Flow inputs, User Activity fields, review text, confirmation
branches, persistence payloads, classification objects, review reasons, route decisions, and
terminal output. It is not left only in LLM memory.

## LLM Ownership Versus Deterministic Ownership

LLM-owned:

- HR Agent conversational interpretation;
- support-ticket classification;
- support-draft problem-summary generation.

Deterministic-owned:

- IT/booking confirmation and persistence;
- classifier schema validation;
- review policy;
- routing table lookup;
- final draft composition;
- terminal output contracts.

## Frozen Engineering Decisions

- Model: `meta-llama/llama-4-maverick-17b-128e-instruct-fp8`
- Classifier prompt: `support-triage-classifier-v2`
- Classifier threshold: `0.80`
- Drafter prompt: `support-triage-drafter-v3`
- Max classifier attempts: `2`
- Persistence backend: IBM Cloud Object Storage
- Part B orchestration: watsonx Orchestrate Flow

## Known Limitations

- Generic draft semantic specificity is not independently guaranteed by deterministic schema
  validation.
- Agent loop-pressure output had a residual output-hygiene limitation while execution stayed
  bounded.
- Final cost and latency are model/tool inference scoped, not total operational cost or latency.
- The combined 30-ticket final evaluation view uses DEV projection plus HELD-OUT complete
  Pipeline records.
