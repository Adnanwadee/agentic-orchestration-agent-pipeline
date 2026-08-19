# Agentic Orchestration — Agent + Pipeline

## 1. Project Overview

This repository implements the Project 2 assignment on IBM watsonx.ai and IBM watsonx
Orchestrate. It demonstrates two different orchestration patterns:

- **Part A: HR Onboarding Agent** — an open-ended conversational Agent that decides which
  capability should run next: policy Q&A, IT access request, orientation booking, clarification,
  out-of-scope handling, or exit.
- **Part B: Support Triage Pipeline** — a fixed support-ticket workflow that intakes one ticket,
  classifies it, validates/reviews it, routes it, drafts only when eligible, and emits a
  structured terminal output.

Building both systems shows where Agent autonomy is useful and where deterministic Pipeline
control is safer.

The Agent demonstrates ReAct-style reasoning and acting: the model interprets user intent and
chooses which approved capability should happen next. The Pipeline demonstrates fixed
orchestration: every ticket follows the same bounded sequence. Classification uses closed labels
and quantitative evaluation; generation creates free-form draft text and is validated with
manual/quality evidence. Tool and skill names, descriptions, and contracts define the safe
capability boundaries.

## 2. Original Engineer Milestones

| Milestone | Deliverable | Final artifact |
|---|---|---|
| 1 | Agent decision flow, Pipeline taxonomy, sample ticket dataset | [AGENT_DECISION_FLOW.md](docs/AGENT_DECISION_FLOW.md), [SUPPORT_TRIAGE_TAXONOMY.md](docs/SUPPORT_TRIAGE_TAXONOMY.md), [support_tickets_seed.json](data/support_tickets_seed.json) |
| 2 | Callable HR policy Q&A over five HR documents | [hr_policy_knowledge_base.yaml](knowledge/hr_policy_knowledge_base.yaml), [mock_docs/](mock_docs/), [milestone_4_part_a_end_to_end_evidence.md](artifacts/milestone_4_part_a_end_to_end_evidence.md) |
| 3 | Independently testable IT and booking Flows | [flows/](flows/), [tests/](tests/) |
| 4 | Complete end-to-end HR onboarding Agent | [milestone_4_part_a_end_to_end_evidence.md](artifacts/milestone_4_part_a_end_to_end_evidence.md) |
| 5 | Structured classifier and threshold decision | [milestone_5_classifier_evidence.md](artifacts/milestone_5_classifier_evidence.md) |
| 6 | Full Pipeline with routing, review, and drafting | [support_triage_flow.py](flows/support_triage_flow.py), [milestone_6_draft_quality_review.md](artifacts/milestone_6_draft_quality_review.md) |
| 7 | Failure-mode report and mitigations | [FAILURE_MODE_REPORT.md](FAILURE_MODE_REPORT.md), [milestone_7_failure_mode_evidence.md](artifacts/milestone_7_failure_mode_evidence.md) |
| 8 | Final evaluation, cost/latency, and architecture comparison | [EVALUATION_REPORT.md](EVALUATION_REPORT.md), [AGENT_VS_PIPELINE.md](AGENT_VS_PIPELINE.md) |

## 3. Architecture

Part A:

```text
user -> hr_onboarding_agent
     -> HR policy Knowledge Base
     -> IT Request Flow -> explicit confirmation -> COS persistence
     -> Orientation Booking Flow -> explicit confirmation -> COS persistence
     -> out-of-scope / completion
```

The Agent decides which capability runs and when. Bounded Flows decide how side-effect-sensitive
operations complete safely.

Part B:

```text
ticket -> support_triage
       -> classify -> validate/review -> route -> draft if auto-routed -> structured output
```

The Part B Orchestrate Flow runtime name is `support_triage`, implemented in
[flows/support_triage_flow.py](flows/support_triage_flow.py). The LLM is bounded to
classification and draft problem-summary generation; deterministic code owns validation, review,
routing, SLA, and final output.

Architecture details:

- [docs/AGENT_DECISION_FLOW.md](docs/AGENT_DECISION_FLOW.md)
- [docs/SUPPORT_TRIAGE_TAXONOMY.md](docs/SUPPORT_TRIAGE_TAXONOMY.md)
- [docs/SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md)

## 4. Repository Structure

- [agents/](agents/) — Orchestrate Agent YAML.
- [flows/](flows/) — Orchestrate Flow implementations.
- [tools/](tools/) — Python tools for persistence, classification, and drafting.
- [knowledge/](knowledge/) — native Knowledge Base definition and ingestion-ready text sources.
- [mock_docs/](mock_docs/) — authoritative supplied HR policy mock documents.
- [data/](data/) — frozen support-ticket dataset, labels, split, and freeze manifest.
- [evaluations/](evaluations/) — HR policy evaluation config and ground truth.
- [tests/](tests/) — local contract/regression tests.
- [scripts/](scripts/) — local evaluation/report/demo helper scripts.
- [artifacts/](artifacts/) — final evidence, raw provenance, and delivery manifests.
- [docs/](docs/) — final reviewer-facing architecture/taxonomy docs.

## 5. Prerequisites

- Python 3.11 for local validation.
- Repository virtual environment `.venv`.
- IBM watsonx Orchestrate ADK 2.13.0, as verified in project evidence.
- IBM watsonx.ai and watsonx Orchestrate access for supervisor-owned remote execution.

## 6. Core Dependencies

Direct project dependencies are pinned in [requirements.txt](requirements.txt). The production
onboarding persistence tool also has [tools/onboarding_persistence_requirements.txt](tools/onboarding_persistence_requirements.txt),
which is intentionally empty because the remote tool uses Python standard-library HTTP for COS
REST calls.

| Package | Version / constraint | Purpose |
|---|---|---|
| `ibm-watsonx-orchestrate` | `==2.13.0` | Local ADK/CLI, Agent/Flow validation, and Orchestrate asset packaging. |
| `ibm-watsonx-ai` | `==1.6.0` | Local watsonx.ai SDK used by classifier/drafter support tooling. |
| `pydantic` | `==2.13.4` | Structured schemas, validation, and contract models. |
| `pytest` | `==9.1.1` | Local regression and contract test runner. |
| `python-dotenv` | `==1.2.2` | Loads `.env` values for local setup scripts. |
| Python stdlib `urllib` | Python runtime | COS persistence uses REST over standard-library HTTP; no third-party COS SDK is required. |

## 7. IBM Environment Used

These are non-secret platform facts proven in repository evidence. See
[artifacts/platform_validation_evidence.md](artifacts/platform_validation_evidence.md) for IBM
platform, model, Knowledge Base, and persistence validation evidence.

| Item | Value |
|---|---|
| Platform | IBM watsonx.ai + IBM watsonx Orchestrate |
| IBM region | Frankfurt / `eu-de` |
| Orchestrate environment alias used during development/demo | `project2` |
| Local Python runtime | Python 3.11 |
| Remote Orchestrate Python-tool runtime | Python 3.12 |
| watsonx Orchestrate ADK | `2.13.0` |
| Selected watsonx.ai model | `meta-llama/llama-4-maverick-17b-128e-instruct-fp8` |
| Orchestrate model reference | `watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8` |
| Knowledge strategy | Native HR Policy Knowledge Base over the five supplied HR documents |
| Persistence strategy | IBM Cloud Object Storage mock/simple persistence via COS REST |
| Non-secret watsonx.ai endpoint | `https://eu-de.ml.cloud.ibm.com` |
| Non-secret COS endpoint | `https://s3.eu-de.cloud-object-storage.appdomain.cloud` |
| Draft connections | `cos_onboarding`, `watsonx_ai`, `watsonx_ai_config` |

## 8. Local Environment Setup

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill `.env` with local/runtime values. Do not commit `.env`.

After editing `.env`, start the local development environment:

```powershell
.\scripts\start_dev.ps1
```

## 9. Required Environment Variables

The environment template is [.env.example](.env.example). It intentionally contains placeholders
only.

| Variable | Secret? | Local purpose | Remote Orchestrate posture |
|---|---|---|---|
| `WX_API_KEY` | Yes | IBM Cloud API key for local watsonx.ai calls. | Remote classifier/drafter use the `watsonx_ai` app connection instead. |
| `WX_PROJECT_ID` | No | watsonx.ai project ID for local classifier/drafter calls. | Remote classifier/drafter read `project_id` from `watsonx_ai_config`. |
| `WX_URL` | No | watsonx.ai regional endpoint, default `https://eu-de.ml.cloud.ibm.com`. | Mirrored by remote connection configuration. |
| `WXO_ENV_NAME` | No | Existing Orchestrate ADK environment alias, proven as `project2`. | Selects the target environment for local ADK commands. |
| `WXO_SERVICE_URL` | No | Optional Orchestrate service URL reference; not required by `scripts/start_dev.ps1`. | Tenant-specific value, not needed in source. |
| `WXO_API_KEY` | Yes | Credential used by `scripts/start_dev.ps1` to activate the Orchestrate environment. | Runtime credential only; never committed. |
| `COS_API_KEY` | Yes | IBM Cloud Object Storage local-development API key. | Remote persistence uses `cos_onboarding` instead. |
| `COS_BUCKET` | No | COS bucket name for local/development persistence tests. | Remote tool uses configured COS target and credential contract. |
| `COS_ENDPOINT` | No | COS regional endpoint. | Remote persistence uses the same non-secret regional endpoint. |

Remote Orchestrate runtime uses configured connections rather than reading `.env`.

## 10. IBM Orchestrate Connections

The final project uses these Orchestrate app connections:

| Connection | Type | Used for | Secret posture |
|---|---|---|---|
| `cos_onboarding` | `api_key_auth` | IT request and orientation booking COS persistence | API key is secret runtime credential. |
| `watsonx_ai` | `api_key_auth` | Classifier and drafter watsonx.ai API access | API key/server URL are runtime connection data. |
| `watsonx_ai_config` | `key_value` | Non-secret `project_id` for classifier/drafter tools | Project ID is config, not committed in source. |

## 11. Starting The Development Environment

After `.env` and `.venv` are prepared:

```powershell
.\scripts\start_dev.ps1
```

The script verifies `.env`, loads values into the current process, activates the repository
virtual environment, checks the repository-local Python and Orchestrate ADK executable, verifies
the configured Orchestrate environment exists, activates it with `WXO_API_KEY`, and prints no
secret values.

## 12. Import / Deployment Order

Supervisor-owned remote deployment followed the proven Orchestrate process. Use repository-local
executables and the active tenant environment.

### A. One-time IBM connection configuration

Exact values depend on the target tenant and credentials. Do not paste real secrets into Git.
The support-triage connection command shapes proven in project evidence are:

```powershell
.\.venv\Scripts\orchestrate.exe connections add --app-id watsonx_ai
.\.venv\Scripts\orchestrate.exe connections configure --app-id watsonx_ai --environment draft --type team --kind api_key --server-url https://eu-de.ml.cloud.ibm.com
.\.venv\Scripts\orchestrate.exe connections set-credentials --app-id watsonx_ai --environment draft --api-key $env:WX_API_KEY
.\.venv\Scripts\orchestrate.exe connections add --app-id watsonx_ai_config
.\.venv\Scripts\orchestrate.exe connections configure --app-id watsonx_ai_config --environment draft --type team --kind key_value
.\.venv\Scripts\orchestrate.exe connections set-credentials --app-id watsonx_ai_config --environment draft --entries project_id=$env:WX_PROJECT_ID
```

The `cos_onboarding` connection is an Orchestrate `api_key_auth` app connection for COS
persistence. Its credential value is tenant-owned and secret.

### B. Asset import / deployment order

1. Import the Knowledge Base from [knowledge/hr_policy_knowledge_base.yaml](knowledge/hr_policy_knowledge_base.yaml).
2. Import persistence tools from [tools/onboarding_persistence.py](tools/onboarding_persistence.py) with the `cos_onboarding` app connection.
3. Import [flows/it_request_flow.py](flows/it_request_flow.py).
4. Import [flows/orientation_booking_flow.py](flows/orientation_booking_flow.py).
5. Import [agents/hr_onboarding_agent.yaml](agents/hr_onboarding_agent.yaml).
6. Configure `watsonx_ai` and `watsonx_ai_config`.
7. Import classifier/drafter tools from [tools/support_triage_classifier.py](tools/support_triage_classifier.py) and [tools/support_triage_drafter.py](tools/support_triage_drafter.py).
8. Import [flows/support_triage_flow.py](flows/support_triage_flow.py), whose runtime Flow name is `support_triage`.

Exact import syntax may vary by tenant connection state and whether a tool package bundle is
used. The support-triage Flow import command shape proven in project evidence is:

```powershell
.\.venv\Scripts\orchestrate.exe tools import --kind flow --file flows\support_triage_flow.py
```

Do not paste real credentials into documentation or Git.

### C. Running/testing deployed systems

Run Part A through `hr_onboarding_agent` in tenant chat. Run Part B through the `support_triage`
Flow runtime. The final manual Part B visual demo used a temporary `support_triage_flow_test_agent`
wrapper only to display the Flow output in chat; the production Part B runtime is the
`support_triage` Flow.

## 13. Running Part A

Open `hr_onboarding_agent` in watsonx Orchestrate Preview Chat or the target tenant chat UI.

Safe example sequence:

1. `What is the annual leave policy for a full-time employee?`
2. `I need Slack and GitHub access. My role is QA Engineer.`
3. Provide the missing employee name, review values, and confirm Yes or No.
4. `I also want to book my orientation session.`
5. Choose one offered slot, review it, and confirm Yes or No.
6. `Thanks, that's everything. I'm done.`

## 14. Running Part B

Invoke the `support_triage` Flow, implemented in
[flows/support_triage_flow.py](flows/support_triage_flow.py), with:

- `ticket_id`
- `ticket_text`

Automatic route paths produce team/SLA and draft response. Human Review paths assign
`Triage — Human`, SLA `Immediate`, and do not produce an automatic customer draft.

## 15. Running Tests

Full regression:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Latest verified local result: `260 passed`.

Useful targeted checks:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_hr_onboarding_agent_contract.py -q
.\.venv\Scripts\python.exe -m pytest tests\test_support_triage_evaluation_report.py -q
```

## 16. Dataset And Evaluation

The support-triage dataset contains 30 tickets:

- T01-T10 supplied tickets preserved.
- 20 synthetic tickets.
- 15 DEV tickets.
- 15 HELD-OUT tickets.

Dataset files:

- [data/support_tickets_seed.json](data/support_tickets_seed.json)
- [data/support_tickets_ground_truth.json](data/support_tickets_ground_truth.json)
- [data/support_tickets_split.json](data/support_tickets_split.json)
- [data/support_tickets_freeze_manifest.json](data/support_tickets_freeze_manifest.json)

Final reporting uses a combined frozen 30-ticket evaluation view:

- DEV: stored classifier outputs plus deterministic frozen policy projection.
- HELD-OUT: stored one-time complete Pipeline records.

Do not describe this as complete Pipeline execution on all 30 tickets.

## 17. Final Results

- Category accuracy: `27/30 = 90.00%`
- Urgency accuracy: `25/28 = 89.29%`
- Structured output: `30/30 = 100.00%`
- Human Review: `10/30 = 33.33%`
- Auto Route: `20/30 = 66.67%`
- Auto-route correctness: `18/20 = 90.00%`
- Selected confidence threshold: `0.80`

## 18. Cost And Latency

Classifier telemetry across 30 stored records: 19,784 prompt tokens, 1,687 completion tokens,
21,471 total tokens, mean latency `0.9127859199730058s`, median `0.7984469500370324s`, p95
`1.5974319597939028s`.

Drafter telemetry for 12 held-out actual draft calls: 3,285 prompt tokens, 152 completion
tokens, 3,437 total tokens, mean latency `0.4832684666228791s`, median
`0.46698354999534786s`, p95 `0.5870209448738024s`.

Using IBM watsonx.ai public pricing accessed 2026-08-18 for
`meta-llama/llama-4-maverick-17b-128e-instruct-fp8`, the expected combined model-inference cost
is approximately USD `0.00040835146` per incoming ticket, or approximately USD `0.40835146` for
1,000 tickets/day.

This is model/tool inference cost only. It excludes fixed plan/platform charges, Orchestrate
charges, COS/storage, networking, human-review labor, taxes/duties, and account-specific costs.

## 19. Known Limitations

- Generic draft semantic specificity is not independently guaranteed by deterministic schema
  validation. It is enforced by prompt/manual/remote quality evidence.
- Agent loop-pressure execution stayed bounded, but pseudo-tool-call syntax remained as a
  low-severity output-hygiene limitation.
- The final 30-ticket view combines DEV projection and one-time HELD-OUT complete Pipeline
  records.
- Latency and cost are model/tool inference scoped, not total operational latency or total
  platform cost.

## 20. Final Deliverables

- [FAILURE_MODE_REPORT.md](FAILURE_MODE_REPORT.md)
- [EVALUATION_REPORT.md](EVALUATION_REPORT.md)
- [AGENT_VS_PIPELINE.md](AGENT_VS_PIPELINE.md)
- [artifacts/README.md](artifacts/README.md)
- [artifacts/final_acceptance_traceability.md](artifacts/final_acceptance_traceability.md)
- [artifacts/final_remote_demo_evidence.md](artifacts/final_remote_demo_evidence.md)

## 21. Engineer Milestone Checklist

| Milestone | Engineer deliverable | Final repository path | Status |
|---|---|---|---|
| 1 | Agent decision flow | [docs/AGENT_DECISION_FLOW.md](docs/AGENT_DECISION_FLOW.md) | PASS |
| 1 | Pipeline taxonomy | [docs/SUPPORT_TRIAGE_TAXONOMY.md](docs/SUPPORT_TRIAGE_TAXONOMY.md) | PASS |
| 1 | Sample ticket dataset | [data/support_tickets_seed.json](data/support_tickets_seed.json) | PASS |
| 2 | Policy Q&A / Knowledge Base | [knowledge/hr_policy_knowledge_base.yaml](knowledge/hr_policy_knowledge_base.yaml), [mock_docs/](mock_docs/) | PASS |
| 3 | IT Request Flow | [flows/it_request_flow.py](flows/it_request_flow.py) | PASS |
| 3 | Orientation Booking Flow | [flows/orientation_booking_flow.py](flows/orientation_booking_flow.py) | PASS |
| 4 | Complete Part A Agent | [agents/hr_onboarding_agent.yaml](agents/hr_onboarding_agent.yaml), [artifacts/milestone_4_part_a_end_to_end_evidence.md](artifacts/milestone_4_part_a_end_to_end_evidence.md) | PASS |
| 5 | Classifier and threshold | [tools/support_triage_classifier.py](tools/support_triage_classifier.py), [artifacts/milestone_5_classifier_evidence.md](artifacts/milestone_5_classifier_evidence.md) | PASS |
| 6 | Complete Pipeline | [flows/support_triage_flow.py](flows/support_triage_flow.py), [artifacts/milestone_6_draft_quality_review.md](artifacts/milestone_6_draft_quality_review.md) | PASS_WITH_APPROVED_QUALIFICATION |
| 7 | Failure report | [FAILURE_MODE_REPORT.md](FAILURE_MODE_REPORT.md), [artifacts/milestone_7_failure_mode_evidence.md](artifacts/milestone_7_failure_mode_evidence.md) | PASS_WITH_APPROVED_QUALIFICATION |
| 8 | Evaluation report | [EVALUATION_REPORT.md](EVALUATION_REPORT.md) | PASS_WITH_APPROVED_QUALIFICATION |
| 8 | Agent autonomy / approval reflection and architecture comparison | [AGENT_VS_PIPELINE.md](AGENT_VS_PIPELINE.md) | PASS |
| Final | Acceptance traceability | [artifacts/final_acceptance_traceability.md](artifacts/final_acceptance_traceability.md) | PASS |
| Final | Remote demonstration | [artifacts/final_remote_demo_evidence.md](artifacts/final_remote_demo_evidence.md) | PASS |

## 22. Original Acceptance Criteria Checklist

| Area | Acceptance criterion | Status |
|---|---|---|
| Part A | Full onboarding conversation covering Policy Q&A, IT, and Booking | PASS |
| Part A | Confirmation before IT submission and booking persistence | PASS |
| Part A | Missing-information follow-up | PASS |
| Part A | Graceful out-of-scope behavior | PASS |
| Part B | Category accuracy at least 80%; final result `27/30 = 90.00%` | PASS |
| Part B | Urgency accuracy at least 75%; final result `25/28 = 89.29%` | PASS |
| Part B | Below-threshold Human Review at selected threshold `0.80` | PASS |
| Part B | Visibly issue-specific accepted draft evidence | PASS_WITH_APPROVED_QUALIFICATION |
| Part B | Structured output for every path | PASS |
| Both | At least three failure scenarios per system and documented handling | PASS |
| Both | Written Agent-versus-Pipeline comparison and swap analysis | PASS |

Final supervisor approval and final commit/push authorization remain pending.

Stretch Goals were not required and were not added.
