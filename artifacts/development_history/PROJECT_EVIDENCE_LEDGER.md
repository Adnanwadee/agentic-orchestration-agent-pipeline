Current Gate: G5
Current Checkpoint: G5 - CODEX Final Git delivery
Code Freeze: ACTIVE

## IBM Tenant Migration Note

The previous remote IBM tenant became unavailable. Local source code, tests, architecture
decisions, and historical evidence remain valid and preserved while the replacement tenant is
being rehydrated. The replacement active persistence bucket is
`agentic-onboarding-p2-9g821-01`. G1 architecture decisions are not reset: COS remains the
persistence backend, the `cos_onboarding` API-key connection, eu-de endpoint, IAM token
exchange, COS REST transport, stdlib HTTP implementation, and least-privilege bucket access
remain the active design. Remaining G2 remote behavior must be reproven on the replacement
tenant. Current Gate remains G2. Isolated remote IT Request Flow, Orientation Booking Flow, and
complete final ReAct Core Agent proofs were completed later from supervisor-provided
replacement-tenant evidence. The final IT Flow prefilled-input boundary regression passed
remotely, G2 is approved, and the project has advanced to G3 for Part B dataset/ground-truth
and split freeze work.

# Execution Plan

This is the current execution/progress source. Work only on the current unchecked checkpoint;
do not begin a later gate until the current gate's MANUAL exit approval is recorded.

## Legend

- `[ ]` incomplete
- `[x]` verified complete
- **Owner: CODEX** — Codex may check the item only after its stated validation succeeds.
- **Owner: MANUAL** — requires supervisor execution, observation, or supplied evidence; Codex
  must never check it based on inference.
- **Evidence: PENDING** — no qualifying evidence has been recorded yet.

## Established local project foundation

- [x] **Owner: CODEX** — **Requirement / purpose:** Verify the local Python runtime.
  **Validation method:** Run `.\.venv\Scripts\python.exe --version`. **Evidence:**
  `Python 3.11.8` observed from the repository virtual environment during the G0 correction.
- [x] **Owner: CODEX** — **Requirement / purpose:** Verify every pinned local dependency and
  the environment test. **Validation method:** Run
  `.\.venv\Scripts\python.exe -m pytest -q` and require all tests to pass. **Evidence:**
  `2 passed in 0.09s` from the repository virtual environment during the G0 correction.
- [x] **Owner: CODEX** — **Requirement / purpose:** Record current branch and clean pre-change
  working-tree state without changing Git configuration. **Validation method:** Run Git status
  and branch commands with a command-scoped safe-directory override. **Evidence:** branch
  `main`; `git status --short` returned no entries before G0 changes.
- [x] **Owner: CODEX** — **Requirement / purpose:** Record the baseline commit.
  **Validation method:** Run `git log -1 --oneline` with a command-scoped safe-directory
  override. **Evidence:** `bbe64ed Initialize project development environment`.
- [x] **Owner: CODEX** — **Requirement / purpose:** Verify the installed project-local
  Orchestrate ADK package version. **Validation method:** Run
  `.\.venv\Scripts\python.exe -c "from importlib.metadata import version; print(version('ibm-watsonx-orchestrate'))"`.
  **Evidence:** `2.13.0`.
- [x] **Owner: CODEX** — **Requirement / purpose:** Verify that the project-local Orchestrate
  CLI reports its version. **Validation method:** Run
  `.\.venv\Scripts\orchestrate.exe --version`. **Evidence:** Command exited 0 and reported
  `ADK Version: 2.13.0` and `Langflow Version: 1.7.1`.

## G0 — CONTROL PLANE

**Purpose:** Freeze development rules, technical specification, and an evidence-based
execution checklist without implementing project features.

**Entry condition:** Repository exists; the supplied G0 brief is available; no feature work is
authorized.

**Checkpoints:**

- [x] **Owner: CODEX** — **Requirement / purpose:** Inspect `README.md`, `requirements.txt`,
  `.gitignore`, `tests/test_environment.py`, Git baseline, Python, ADK availability, and existing
  tests before editing. **Validation method:** Read files and run the specified safe local
  commands. **Evidence:** Completed during G0; results recorded in the foundation section.
- [x] **Owner: CODEX** — **Requirement / purpose:** Create only the concise repository rules
  file `AGENTS.md`. **Validation method:** Inspect the final diff for required rules, scope, and
  line count. **Evidence:** Full new-file diff inspected; all required operational rules are
  present; the G0 correction pass revalidated the concise file at 56 lines.
- [x] **Owner: CODEX** — **Requirement / purpose:** Create only the complete technical source
  of truth at `artifacts/development_history/PROJECT_SPEC_HISTORY.md`. **Validation method:** Audit it against every supplied
  architecture, contract, constraint, fallback, non-goal, edge case, and acceptance
  requirement. **Evidence:** Full new-file diff inspected; the G0 correction pass revalidated
  the 419-line file with A–F requirement divisions, routing/edge cases, frozen decisions,
  constraints, fallbacks, non-goals, and acceptance; no implementation code is included.
- [x] **Owner: CODEX** — **Requirement / purpose:** Create only this six-gate progress source at
  `artifacts/development_history/PROJECT_EVIDENCE_LEDGER.md`. **Validation method:** Audit all gates for purpose, entry condition,
  owned checkpoints, validation/evidence, and exit criteria. **Evidence:** Full new-file diff
  inspected; exactly G0–G5 are present with the required fields and owned evidence checkpoints.
- [x] **Owner: CODEX** — **Requirement / purpose:** Preserve the existing local environment and
  stay inside the G0 file boundary. **Validation method:** Confirm the final diff/status contain
  only the three authorized new files and no dependencies, features, secrets, staging, commits,
  or pushes. **Evidence:** File inventory and full new-file diffs show only `AGENTS.md`,
  `artifacts/development_history/PROJECT_SPEC_HISTORY.md`, and `artifacts/development_history/PROJECT_EVIDENCE_LEDGER.md`; tracked diff is empty and the
  secret-shaped assignment scan found no match.
- [x] **Owner: CODEX** — **Requirement / purpose:** Execute final G0 local validation and inspect
  its results. **Validation method:** Run `.\.venv\Scripts\python.exe -m pytest -q`,
  `git diff --check`, and `git status --short`; inspect the complete diff. **Evidence:** Project-
  local pytest passed with 2 tests; `git diff --check` passed; status contained only
  `?? AGENTS.md` and `?? docs/`.
- [x] **Owner: MANUAL** — **Requirement / purpose:** G0 supervisor audit passed; approve the
  three control files and authorize advancement. **Validation method:** Supervisor performs a
  line-by-line audit and explicitly approves G0. **Evidence:** Supervisor audit approved G0 on
  2026-08-09 02:55:52 +03:00 after direct review of `AGENTS.md`,
  `artifacts/development_history/PROJECT_SPEC_HISTORY.md`, and `artifacts/development_history/PROJECT_EVIDENCE_LEDGER.md`; project-local pytest verification;
  project-local Orchestrate ADK verification; and scope audit confirming only the three G0
  control files were introduced.

**Validation:** Document audit, full diff inspection,
`.\.venv\Scripts\python.exe -m pytest -q`, `git diff --check`, and `git status --short`; no
remote commands.

**Evidence:** G0 inspection, document, scope, command, and diff evidence is recorded in the
checked checkpoints above. The project-local environment tests, ADK package check, CLI version
check, and supervisor approval evidence pass.

**Exit criteria:** The three control files are approved, the scope audit is clean, local facts
and failures are accurately recorded, and the MANUAL “G0 supervisor audit passed” checkpoint
is checked by a supervisor. G0 is approved and closed; execution tracking has advanced to G1A.

## G1 — WATSON PLATFORM PROOF

**Purpose:** Prove real tenant capabilities early and freeze the platform-dependent decisions
before feature implementation.

**Entry condition:** G0 supervisor audit is approved and the supervisor explicitly authorizes
G1 credentials, tenant activity, and any necessary dependency changes.

**Checkpoints:**

### G1A — Connectivity

- [x] **Owner: MANUAL** — **Requirement / purpose:** Authenticate to remote watsonx
  Orchestrate. **Validation method:** Perform approved authentication and observe a successful
  tenant command/session. **Evidence:** Supervisors verified remote environment `project2` was
  created and activated successfully with IBM IAM authentication; CLI reported `project2` active
  in the Global workspace; `orchestrate env list` showed `project2` as active with local
  separately configured; and, with `project2` active, `orchestrate agents list` successfully
  queried the remote tenant and returned Agent records. No credentials were committed and no
  feature implementation occurred.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove watsonx.ai connectivity with a real
  API smoke call. **Validation method:** Send a minimal approved request and capture a
  successful non-sensitive result. **Evidence:** Supervisors verified a valid IBM Cloud IAM API
  key was exchanged for an IAM bearer token; the Frankfurt watsonx.ai endpoint was used; the
  repository `.venv` executed the installed `ibm-watsonx-ai` SDK; `APIClient` authenticated
  successfully against the actual watsonx.ai project; `client.projects.get_details(project_id)`
  returned project metadata; and the observed smoke output was `WATSONX_API_SMOKE=PASS`,
  `RESPONSE_TYPE=dict`, and `PROJECT_METADATA_RECEIVED=True`. No credentials were committed and
  no feature implementation occurred.
- [x] **Owner: MANUAL** — **Requirement / purpose:** List models actually available in the
  target Watson environment. **Validation method:** Query the tenant model catalog and preserve
  dated output. **Evidence:** Supervisors verified full remote Orchestrate model discovery with
  `orchestrate models list -a`; the command succeeded and nine Orchestrate model/provider
  entries were observed: `groq/openai/gpt-oss-120b` as default/preferred,
  `bedrock/openai.gpt-oss-120b-1:0` as preferred, `watsonx/openai/gpt-oss-120b` as preferred,
  `watsonx/ibm/granite-3-1-8b-base`, `watsonx/ibm/granite-4-h-small`,
  `watsonx/meta-llama/llama-3-3-70b-instruct`,
  `watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8`,
  `watsonx/mistralai/mistral-medium-2505`, and
  `watsonx/mistralai/mistral-small-3-1-24b-instruct-2503`. Supervisors also verified direct
  Frankfurt watsonx.ai chat-model discovery through the repository-local `ibm-watsonx-ai` SDK;
  the watsonx.ai project had the required Runtime association, discovery reported
  `WATSONX_CHAT_MODEL_DISCOVERY=PASS` and `CHAT_MODEL_COUNT=4`, and the four direct chat models
  observed were `ibm/granite-4-h-small`, `meta-llama/llama-3-3-70b-instruct`,
  `meta-llama/llama-4-maverick-17b-128e-instruct-fp8`, and
  `mistralai/mistral-small-3-1-24b-instruct-2503`. Actual model identifiers were captured; no
  model has been selected or frozen yet.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Select one suitable available model under
  the specification's decision rule. **Validation method:** Review availability and smoke-call
  evidence; benchmark only if the selected model later fails quality targets. **Evidence:**
  Supervisors selected `meta-llama/llama-4-maverick-17b-128e-instruct-fp8` from the four
  available direct watsonx.ai chat finalists under the fixed priority: safety first, then
  structured-output reliability and semantic correctness, then support-draft quality, with
  latency/token usage only as tie-breakers. Valid Round-1 smoke evidence used four finalist
  models, eight synthetic probes per model, 32/32 successful remote chat calls, temperature
  `0.0`, and max completion tokens `300`; Maverick recorded API success `8/8`, strict JSON
  `7/7`, schema valid `7/7`, expected semantic matches `5/7`, safety `4/4`, and mean latency
  approximately `0.92` seconds. A valid corrective confirmation run
  `g1a-model-selection-confirmation-v1` then completed 16/16 planned calls with all four
  finalists, no model initialization errors, no per-call infrastructure/runtime errors, and
  `model_selected=false`. In that confirmation, Maverick passed corrected C1, failed corrected
  C2 with the residual risk `unknown-urgency over-inference` by returning `urgency = medium`
  where JSON null was expected, passed corrected C3 with only
  `missing_fields = ["employee_name"]` and `side_effect_allowed = false`, and retained the
  support-drafting residual risk of an unsupported future-action/SLA promise on C4. Across the
  two valid rounds, Maverick was the only finalist with no observed safety-probe failure. The
  prior IBM infrastructure/certificate-failure execution is excluded from model-quality,
  schema, semantic, and safety evidence because it failed before usable model inference. This is
  bounded G1 selection evidence, not a formal benchmark or a claim that the selected model is
  perfect.
- [x] **Owner: CODEX** — **Requirement / purpose:** Prepare the minimal real
  `hr_onboarding_agent` artifact/configuration that will be expanded in G2, not a disposable
  Hello Agent. **Validation method:** Run all available local/static validation and inspect its
  bounded instructions/configuration before import. **Evidence:** Created
  `agents/hr_onboarding_agent.yaml` as a native watsonx Orchestrate Agent named
  `hr_onboarding_agent`, initially using `style: default`, and the Orchestrate-qualified
  Maverick model ID `watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8`. Local YAML
  parsing with the already-installed `yaml` package passed; local ADK `AgentSpec` validation
  passed; and static validation confirmed `spec_version: v1`, `kind: native`, non-empty bounded
  description and instructions, and empty `tools`, `collaborators`, and `knowledge_base`.
  Semantic inspection confirmed the artifact is the real HR onboarding Agent shell, covers only
  HR policy Q&A, IT/software/system access requests, and orientation booking, separates
  information requests from action-taking, preserves confirmation boundaries, invents no policy
  content, includes no Part B support-triage logic, and wires no tools, collaborators, Knowledge
  Base, side-effect workflows, Cloudant persistence, User Activity, Prompt Nodes, or later
  capabilities. After the real tenant reported Default style as deprecated and Agent Builder
  showed ReAct Core as recommended, a supervisor-approved corrective sub-step migrated only the
  repository artifact style to `react_intrinsic`, the ADK/YAML representation of ReAct Core.
  Local ADK 2.13.0 accepted `react_intrinsic`; YAML parsing and ADK `AgentSpec` validation passed
  after migration; and the model, name, kind, spec version, description, instructions, tools,
  collaborators, and Knowledge Base remained otherwise unchanged. No remote IBM command was
  executed by Codex for the style migration.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Import and test a minimal real
  `hr_onboarding_agent`. **Validation method:** Import it into Orchestrate and observe a minimal
  successful conversation. **Evidence:** Supervisors verified the corrected ReAct Core
  `hr_onboarding_agent` was remotely imported; Agent Builder showed ReAct Core selected; the
  selected Maverick model remained in use; the Agent identified itself as the HR onboarding
  assistant; stated the three approved domains; abstained on annual-leave policy while no
  Knowledge Base was attached; gracefully declined a flight-booking request; provided a clear
  conversational exit; and did not falsely claim the unavailable IT workflow had executed. Known
  deferred G2 hardening: for `Please request Slack and Jira access for me. I'm a new data
  analyst.`, the minimal shell requested an unnecessary company-email field. This does not prove
  the full IT capability works and is deferred to the real IT capability/final Agent
  instruction hardening.

### G1B — Capability Spikes

- [x] **Owner: CODEX** — **Requirement / purpose:** Prepare the minimal Prompt Node strict-
  structured-output spike artifact. **Validation method:** Run every available local/static/
  compile validation that does not require remote credentials. **Evidence:** Replaced the
  temporary YAML scaffold with `flows/g1b_prompt_node_spike.py`, a real ADK 2.13.0
  `@flow` Python artifact importable as a flow tool with `orchestrate tools import --kind flow
  --file`. Local Python syntax compilation passed; local ADK Flow loader serialization passed
  using a command-scoped fake local Orchestrate profile with a dummy non-secret JWT because ADK
  `Flow.__init__` requires an active environment before graph construction; the serialized graph is
  `__start__` → `classify_ticket_strict_json` Prompt Node → `__end__`. The Prompt Node uses the
  selected Maverick model ID `watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8`,
  Pydantic input schema with only `ticket_text`, and Pydantic output schema with exactly
  `category`, `urgency`, `confidence`, and `reasoning`. Static tests confirmed exact category
  taxonomy, true nullable urgency semantics with no string `"null"` label, confidence bounds
  0.0 through 1.0, concise reasoning, and no routing, threshold, human-review policy, drafting,
  full G3 dataset, production schema, or retry logic. Superseded Prompt YAML and temporary JSON
  smoke fixture were deleted.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove Prompt Node strict structured output.
  **Validation method:** Run input → Prompt Node → validated strict structured output → end in
  the tenant, including a repeatability check. **Evidence:** Supervisors verified
  `flows/g1b_prompt_node_spike.py` imported as remote Flow tool `g1b_prompt_node_spike`; the
  tenant accepted and executed the Flow; the Prompt Node used
  `watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8`; and execution produced
  schema-valid structured outputs with exactly `category`, `urgency`, `confidence`, and
  `reasoning`. Repeat execution of the same ticket text, `My invoice has a duplicate charge for
  this month.`, produced inconsistent/input-unfaithful classification evidence: one run
  classified billing/high with duplicate-charge reasoning, while a separate clean execution
  classified account/medium with account-access reasoning absent from the input. The capability
  spike therefore proves Prompt Node structural availability but fails semantic repeatability
  and input fidelity for this project. `PIPELINE_LLM_MODE = PYTHON_WATSONX_TOOL` is the selected
  fallback; this does not change the selected Maverick model and does not create a standalone
  Python pipeline.
- [x] **Owner: CODEX** — **Requirement / purpose:** Prepare the User Activity spike artifact for
  ask value → retain value → confirm → Yes/No branch. **Validation method:** Run all available
  local/static validation and inspect both branch definitions. **Evidence:** Replaced the
  temporary YAML scaffold with `flows/g1b_user_activity_spike.py`, a real ADK 2.13.0 `@flow`
  Python artifact importable as a flow tool with `orchestrate tools import --kind flow --file`.
  Local Python syntax compilation passed; local ADK Flow loader serialization passed using the
  same command-scoped fake local Orchestrate profile used only to avoid remote credentials
  during local graph construction. The serialized top-level graph is `__start__` →
  `g1b_user_activity_session` UserFlow → `__end__`; the nested UserFlow graph is `__start__` →
  `request_label` → `retained_request_label` → `confirmed` → `confirmation_decision` →
  `yes_branch` or `no_branch`. Static tests confirmed field-based value collection,
  retained-value display through a DataMap, explicit boolean Yes/No branch cases, output mapping
  for retained `request_label`, confirmation outcome, `side_effect_performed = false`, and
  `persistence_performed = false`, and no Cloudant, persistence, IT request, booking, or other
  side effect. Superseded User Activity YAML and superseded form-based scaffolds were deleted.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove User Activity multi-turn state and
  protected confirmation. **Validation method:** Run ask value → retain value → confirm → Yes/No
  branch and observe both branches. **Evidence:** Supervisors verified
  `flows/g1b_user_activity_spike.py` imported as remote Flow tool
  `g1b_user_activity_spike`. The initial form-based runtime displayed a blank retained value and
  failed with `Invalid 'confirmation_decision' node output. Value = {}`; the `.value`
  form-based correction failed the same way. The final field-based implementation succeeded in
  the tenant: the No run collected `g1b-no-probe`, displayed the retained value at confirmation,
  branched to No, and completed with `confirmation_outcome = "no"`,
  `persistence_performed = false`, `request_label = "g1b-no-probe"`, and
  `side_effect_performed = false`. A separate Yes run reached the Yes branch without the prior
  runtime error. This proves the native field-based User Activity strategy for G2 side-effect
  confirmation; no production IT, booking, Cloudant, or side-effect behavior was implemented or
  proven in this spike.
- [x] **Owner: CODEX** — **Requirement / purpose:** Prepare the one-document native Knowledge
  Base definition/configuration using one identified, approved supplied mock HR document.
  **Validation method:** Run available local/static validation and verify that no policy content
  was invented. **Evidence:** Verified the engineer-supplied mock document directory contains
  exactly `benefits-and-compensation.md`, `code-of-conduct.md`, `it-access-policy.md`,
  `leave-policy.md`, and `new-hire-orientation-guide.md`; used only the authoritative
  `mock_docs/leave-policy.md` source for this G1B spike and did not modify policy content.
  Created byte-identical ingestion representation `knowledge/sources/leave-policy.txt` because
  the tenant rejected direct Markdown ingestion as unsupported `text/markdown`. Created
  `knowledge/g1b_leave_policy_kb.yaml` as the one-document native Knowledge Base definition
  referencing exactly `sources/leave-policy.txt`, with a concise leave-policy description,
  built-in document-backed vector index defaulting to standard extraction, citation display,
  and an explicit abstention message. Local YAML parsing passed; ADK 2.13.0
  `KnowledgeBase.from_spec`, `KnowledgeBase.model_validate`, and
  `validate_documents_or_index_exists()` passed; tests confirmed only the approved leave-policy
  ingestion representation is referenced, its bytes and SHA-256 exactly match the authoritative
  Markdown source, and no custom RAG, external Milvus, Elasticsearch, AstraDB, OpenSearch,
  custom search, or vector database is configured. The source SHA-256 was
  `58010048238908492092F61022B97D1BF357BE6432F34E818174808187D29731`. Superseded blocked KB
  scaffold was deleted.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove native Knowledge Base viability with
  one document. **Validation method:** Ask grounded and unsupported questions; capture citation
  or grounding behavior and abstention quality. **Evidence:** Supervisors verified the first KB
  import failure was a relative-path issue (`knowledge\mock_docs\leave-policy.md`); the next
  failure proved the tenant rejected direct Markdown ingestion as unsupported
  `text/markdown`. After switching the KB definition to byte-identical
  `knowledge/sources/leave-policy.txt`, the remote native Knowledge Base import succeeded as
  `hr_leave_policy_g1b_kb` with ID `8c8d9340-f545-44c6-9620-d71d87ee4762`. The tenant reported
  `Ready=True`, Built In Index ready, and document `leave-policy.txt`. A grounded leave-policy
  question returned the approved annual-leave answer of 21 working days, and an unsupported pet
  insurance question abstained rather than inventing policy. No citation UI evidence was
  captured, so citation display is not claimed. Native Knowledge Base is viable; custom RAG and
  external vector databases remain inactive.

### G1C — Persistence

- [x] **Owner: MANUAL** — **Requirement / purpose:** Resolve persistence backend viability after
  Cloudant provisioning was blocked. **Validation method:** Review account/admin restriction
  evidence, original requirement allowance for a file/simple datastore, and approved alternative
  backend evidence. **Evidence:** Supervisors verified Cloudant provisioning was blocked by IBM
  Cloud account/admin approval; the original project requirement permits a file or simple
  datastore; an existing IBM Cloud Object Storage instance `cos-697001jjp6` and dedicated bucket
  `agentic-onboarding-p2-9g821` in `eu-de` were available; and COS was approved for bounded
  platform proof rather than Cloudant.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Configure least-privilege COS access and an
  Orchestrate connection without committing credentials. **Validation method:** Inspect resource
  scope, connection configuration, and repository secret posture. **Evidence:** Supervisors
  verified Service ID / credential `project2-onboarding-cos` was scoped to service instance
  `cos-697001jjp6`, resource type `bucket`, resource ID `agentic-onboarding-p2-9g821`, with
  only Object Reader and Object Writer roles. Orchestrate Draft connection `cos_onboarding` is
  configured as team `api_key_auth` with credentials set; Live is intentionally not configured.
  No credentials were committed.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove local real-network COS write/read.
  **Validation method:** Exchange IAM API key for bearer token, PUT one bounded JSON object, GET
  it back, and compare semantic JSON equality. **Evidence:** Supervisors verified IBM IAM
  API-key to bearer token passed with token type Bearer and `expires_in = 3600`; COS PUT to
  `g1c-persistence-probe.json` returned HTTP 200; COS GET returned HTTP 200; read-back fields
  `probe_id = g1c-persistence-probe`, `purpose = verify_cos_persistence`, and
  `status = written` matched the written payload exactly.
- [x] **Owner: CODEX** — **Requirement / purpose:** Prepare the smallest remote persistence probe
  for the intended COS runtime path without third-party dependencies. **Validation method:** Run
  local syntax and mocked network tests proving connection use, IAM request construction, PUT,
  GET, semantic equality, sanitized failures, and no external network calls. **Evidence:**
  Prepared evidence-only Python tool `tools/cos_persistence_probe.py` and dedicated empty import
  requirements file `tools/cos_persistence_probe_requirements.txt`; tests proved stdlib HTTP
  behavior, Orchestrate `expected_credentials` with `cos_onboarding` / `API_KEY_AUTH`,
  secret-safe returns and failures, matching JSON equality, mismatched read-back failure, and
  IAM/PUT/GET failure handling. No `requests`, `boto3`, `ibm-cos-sdk`, `httpx`, `aiohttp`, or
  other dependency was added. The local probe file was later deleted after durable evidence was
  consolidated for G1 closeout.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove real remote Orchestrate Python runtime
  COS write/read/equality. **Validation method:** Import the probe with the existing connection,
  invoke it through a temporary remote harness, and observe structured non-secret proof.
  **Evidence:** Supervisors verified remote Python tool `cos_persistence_probe` imported with
  connection `cos_onboarding`; ADK 2.13.0 required a requirements file and accepted the dedicated
  empty requirements input while packaging `ibm-watsonx-orchestrate==2.13.0`; temporary harness
  agent `cos_persistence_probe_agent` (Agent ID `b050c969-b64a-4152-a58c-3c9a0d722ac0`) invoked
  the tool in chat thread `157cb3b3-f634-4719-b59d-723543c2535a`; and the observed result was
  `backend = ibm_cloud_object_storage`, bucket `agentic-onboarding-p2-9g821`,
  object key `orchestrate-runtime-persistence-probe.json`, `iam_authenticated = true`,
  `put_status = 200`, `get_status = 200`, `data_match = true`, `probe_id =
  orchestrate-runtime-persistence`, and `status = pass`.
- [x] **Owner: CODEX** — **Requirement / purpose:** Freeze the smallest tenant-compatible
  persistence backend, transport, and dependency strategy. **Validation method:** Record proven
  backend, connection, transport, runtime, filesystem, and dependency evidence in the
  specification and canonical platform evidence. **Evidence:** Frozen backend is IBM Cloud
  Object Storage using bounded JSON objects, Orchestrate `API_KEY_AUTH` connection
  `cos_onboarding`, IBM IAM token exchange, COS REST API, Python standard-library HTTP, remote
  Python 3.12, read-only remote filesystem assumption, and no third-party COS SDK or HTTP
  dependency. Cloudant remains a historical initial candidate only.

### G1 frozen decisions

- [x] **Owner: CODEX** — **Requirement / purpose:** Record and freeze the selected model.
  **Validation method:** Update the specification only from the G1 model-list and smoke-call
  evidence. **Evidence:** `meta-llama/llama-4-maverick-17b-128e-instruct-fp8` is frozen as the
  selected Watson model with Orchestrate reference
  `watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8`, based on bounded G1 evidence and
  with residual risks documented.
- [x] **Owner: CODEX** — **Requirement / purpose:** Freeze `PIPELINE_LLM_MODE` as `PROMPT_NODE`
  or `PYTHON_WATSONX_TOOL`. **Validation method:** Apply the Prompt Node pass/fail rule exactly
  and cite spike evidence. **Evidence:** `PIPELINE_LLM_MODE = PYTHON_WATSONX_TOOL` is frozen
  because the real Prompt Node path imported, executed, and returned strict structure, but failed
  semantic repeatability/input fidelity in the tested tenant path. Flow remains the sole Part B
  orchestrator.
- [x] **Owner: CODEX** — **Requirement / purpose:** Freeze the User Activity implementation
  strategy. **Validation method:** Apply the primary/fallback rule to observed Yes/No state
  behavior. **Evidence:** Native field-based multi-turn User Activity is frozen because the
  form-based approach failed remotely, the `.value` correction also failed, and the simplified
  field-based pattern proved retained value, explicit confirmation, Yes branch, and No branch.
- [x] **Owner: CODEX** — **Requirement / purpose:** Freeze native Knowledge Base viability.
  **Validation method:** Record spike quality; allow custom RAG only after one reasonable native
  tuning attempt materially fails and supervisor approves fallback. **Evidence:** Native
  Orchestrate Knowledge Base is frozen with authoritative Markdown sources and byte-identical
  `.txt` ingestion representations. One-document remote KB import/index/grounded answer and
  unsupported abstention passed; direct `.md` ingestion failed as unsupported `text/markdown`.
- [x] **Owner: CODEX** — **Requirement / purpose:** Freeze COS persistence backend, transport,
  and dependency strategy. **Validation method:** Record the proven remote write/read path and
  compatibility result. **Evidence:** IBM Cloud Object Storage is frozen with bounded JSON
  objects, bucket `agentic-onboarding-p2-9g821`, Orchestrate connection `cos_onboarding`, IBM IAM
  token exchange, COS REST API, stdlib HTTP, and no third-party COS/HTTP dependency.

**Validation:** Real tenant evidence for every remote claim; local files/tests for recorded
decisions; no decision inferred from documentation alone.

**Evidence:** G1 evidence is consolidated in `artifacts/platform_validation_evidence.md`, with
raw model-selection JSON retained as `artifacts/model_selection_smoke.json` and
`artifacts/model_selection_confirmation.json`.

**Exit criteria:** Connectivity and all three spikes are observed, persistence is proven, all
five platform-dependent decisions are recorded/frozen, local validation passes, and a
supervisor explicitly approves G1 exit. G1 is CLOSED on 2026-08-12.

## G2 — COMPLETE PART A: HR ONBOARDING AGENT

**Purpose:** Build and prove the complete bounded HR onboarding Agent after G1 decisions are
frozen.

**Entry condition:** G1 exit is approved; model, LLM mode, User Activity strategy, native KB
viability, and COS persistence strategy are frozen.

**Checkpoints:**

- [x] **Owner: CODEX** — **Requirement / purpose:** Complete the original Milestone 1 planning
  deliverables before G2 feature implementation. **Validation method:** Verify that
  `artifacts/development_history/PROJECT_SPEC_HISTORY.md` already satisfies the written Pipeline taxonomy deliverable; verify
  `docs/AGENT_DECISION_FLOW.md` exists and matches the frozen Agent architecture; verify
  `data/support_tickets_seed.json` contains exactly 30 unique tickets with supplied T01-T10
  texts preserved verbatim, exactly 20 additional synthetic tickets, no duplicate IDs/texts, no
  secrets or real personal data, and no classifier or production implementation started.
  **Evidence:** `artifacts/development_history/PROJECT_SPEC_HISTORY.md` already represents the written Pipeline taxonomy;
  `docs/AGENT_DECISION_FLOW.md` exists as the Agent decision-flow planning artifact;
  `data/support_tickets_seed.json` exists and parses as exactly 30 unique tickets with IDs
  T01-T30, exactly 10 supplied and 20 synthetic records, supplied T01-T10 texts preserved
  verbatim, and no duplicate IDs/texts. Validation passed with full pytest, dataset structural
  assertions, AgentSpec validation, `git diff --check`, and scans finding no secrets/PII,
  classifier/evaluation implementation, or production G2 feature implementation.
- [x] **Owner: CODEX** — **Requirement / purpose:** Finalize the five authoritative HR knowledge
  sources and prepare the complete platform-compatible ingestion set. **Validation method:**
  Verify the five authoritative Markdown files remain unchanged, create/verify the missing
  byte-identical `.txt` ingestion representations under `knowledge/sources/`, confirm exact byte
  equality/hashes, and scan for secrets or real personal data. **Evidence:** Five authoritative
  Markdown files were verified, and all five platform-compatible TXT ingestion representations
  are present under `knowledge/sources/`. Deterministic pair validation passed: byte equality
  PASS for all five MD/TXT pairs, SHA-256 equality PASS for all five pairs, authoritative source
  pre/post integrity PASS, and the known G1 leave-policy SHA
  `58010048238908492092F61022B97D1BF357BE6432F34E818174808187D29731` was retained exactly for
  both `mock_docs/leave-policy.md` and `knowledge/sources/leave-policy.txt`. Scoped secret/real-
  PII inspection passed for the five Markdown sources plus five TXT ingestion representations.
  `.\.venv\Scripts\python.exe -m pytest -q` passed with `2 passed in 0.04s`, and
  `git diff --check` passed.
- [x] **Owner: CODEX** — **Requirement / purpose:** Prepare the full native HR Policy Knowledge
  Base definition/configuration from the five supplied documents. **Validation method:** Run all
  available local/static validation and verify exact document references. **Evidence:**
  Production native KB artifact `knowledge/hr_policy_knowledge_base.yaml` was created with name
  `hr_policy_knowledge_base` and exactly the five approved TXT references under `sources/`.
  Local YAML parsing passed; installed ADK 2.13.0 `KnowledgeBase.from_spec`,
  `KnowledgeBase.model_validate`, and `validate_documents_or_index_exists()` passed with
  built-in document-backed vector index configuration and standard extraction strategy.
  Document path-resolution validation passed from the real artifact location. Static audit found
  no Markdown references, no stage/probe/spike/test naming, no custom RAG or external vector DB
  backend configuration, and no invented retrieval/response confidence threshold. Five-source
  MD/TXT byte and SHA-256 integrity recheck passed. KB artifact secret-shaped text scan passed.
  `.\.venv\Scripts\python.exe -m pytest -q` passed with `2 passed in 0.03s`, and
  `git diff --check` passed.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Import and prove the full native HR Policy
  Knowledge Base from all five documents. **Validation method:** Import/index in the tenant and
  observe all sources available. **Evidence:** Supervisor supplied observed remote evidence from
  the active `project2` watsonx Orchestrate tenant: production Knowledge Base
  `hr_policy_knowledge_base` imported successfully; tenant status reported `Ready=True`, Built
  In Index Status `ready`, and Documents (5). The five observed document filenames were
  `benefits-and-compensation.txt`, `code-of-conduct.txt`, `it-access-policy.txt`,
  `leave-policy.txt`, and `new-hire-orientation-guide.txt`. The remote KB ID is not recorded
  because the supervisor output displayed it truncated. This proves only full-KB import/index
  availability; Agent-level KB invocation, grounded Q&A, abstention, retrieval metrics, and
  citation behavior are not yet claimed.
- [x] **Owner: CODEX** — **Requirement / purpose:** Wire/attach the full native HR Policy
  Knowledge Base to `hr_onboarding_agent` before grounded policy-Q&A acceptance testing.
  **Validation method:** Static Agent artifact audit verifies the Agent remains ReAct Core,
  selected Maverick remains unchanged, the native KB is attached, and no IT or booking tool is
  wired by this checkpoint. **Evidence:** Local Agent YAML parsing passed; installed ADK 2.13.0
  `Agent.from_spec` and `AgentSpec.model_validate` passed. Static assertions verified
  `hr_onboarding_agent` remains native ReAct Core / `react_intrinsic`, selected Maverick remains
  `watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8`, exactly one production Knowledge
  Base is attached as `hr_policy_knowledge_base`, `tools` remains empty, `collaborators` remains
  empty, and no IT or booking capability is wired. The production KB artifact still defines
  `hr_policy_knowledge_base` with exactly five approved TXT references, and the five MD/TXT
  source-integrity checks passed. Changed-artifact secret-shaped text scan passed.
  `.\.venv\Scripts\python.exe -m pytest -q` passed with `2 passed in 0.10s`, and
  `git diff --check` passed.
- [x] **Owner: CODEX** — **Requirement / purpose:** Correctively harden
  `hr_onboarding_agent` against unsupported negative HR-policy inference before remote
  regression. **Validation method:** Static Agent artifact audit and local tests verify the
  Agent instructions require evidence-bounded abstention when KB evidence is missing or merely
  related, while still allowing negative policy answers when the attached KB explicitly supports
  them. **Evidence:** Remote testing exposed a failing unsupported-policy behavior: for dependent
  private-school or university tuition reimbursement, related benefits evidence was generalized
  into the unsupported negative conclusion that Apex does not reimburse dependent tuition.
  Local instructions were hardened with the general rule that missing or related-but-insufficient
  KB evidence is not proof that a policy, benefit, reimbursement, eligibility rule, coverage
  rule, permission, requirement, or prohibition does not exist; a negative policy answer is
  allowed only when the attached KB explicitly supports that negative answer; and related policy
  information must not be generalized to a different subject, beneficiary, scope, entitlement, or
  condition. Added `tests/test_hr_onboarding_agent_contract.py` to assert the production Agent
  architecture remains unchanged and that the no-unsupported-negative-inference instruction is
  present without simulating LLM behavior. YAML parsing, ADK `Agent.from_spec`, and
  `AgentSpec.model_validate` passed; static assertions verified name, kind, style, selected
  Maverick model, attached KB, empty tools, and empty collaborators remain unchanged.
  `.\.venv\Scripts\python.exe -m pytest -q` passed with `5 passed in 0.49s`; changed-file
  secret-shaped text scan passed; and `git diff --check` passed. Remote regression remains
  MANUAL/PENDING: U1 unsupported pet insurance must abstain, U2 unsupported dependent tuition
  reimbursement must abstain without inferring a negative policy, and one previously supported
  HR policy question must still return the grounded answer.
- [x] **Owner: CODEX** — **Requirement / purpose:** Apply Corrective Hardening #2 to
  `hr_onboarding_agent` after remote regression showed Hardening #1 was insufficient for the
  dependent-tuition unsupported-negative case. **Validation method:** Inspect installed ADK
  2.13.0 Agent guideline support; implement only an ADK-accepted native guideline if locally
  validated; otherwise use instructions; then run static Agent contract tests, ADK validation,
  architecture invariants, secret/dependency checks, and diff checks. **Evidence:** After
  Hardening #1, supervisor remote regression showed U1 unsupported pet insurance PASS with KB
  invocation and insufficient-information abstention, but U2 dependent private-school or
  university tuition reimbursement still FAIL because the Agent concluded that Apex does not
  reimburse employees' children or other dependents without explicit approved negative evidence.
  Installed ADK 2.13.0 evidence showed native `AgentSpec` accepts `guidelines` as
  `Optional[List[AgentGuideline]]`, where `AgentGuideline` has `display_name`, `condition`,
  `action`, and optional `tool`; an actual YAML guideline representation passed
  `AgentSpec.model_validate`, `Agent.from_spec`, and post-load `AgentSpec.model_validate`.
  Path A was selected. The production Agent now contains one native guideline,
  `Evidence-state policy answers`, encoding the three states: explicit positive evidence
  permits a grounded positive answer; explicit negative evidence permits a grounded negative
  answer limited to explicit scope; and neither explicit state requires insufficient-information
  abstention, including missing, noisy, broadly related, or cross-subject/beneficiary/scope/
  entitlement/reimbursement-type/coverage-type/eligibility-condition/permission/prohibition/
  exception evidence. The guideline explicitly prohibits converting silence or
  related-but-insufficient evidence into a negative company-policy conclusion. Contract tests
  were updated to assert the structured guideline, all three evidence states, unsupported-
  negative prevention, supported-negative preservation, and no hardcoded regression prompts.
  YAML parsing, ADK `Agent.from_spec`, guideline schema validation, and `AgentSpec.model_validate`
  passed; static assertions verified name, kind, style, selected Maverick model, attached KB,
  empty tools, and empty collaborators remain unchanged. `.\.venv\Scripts\python.exe -m pytest
  -q` passed with `8 passed in 0.38s`; changed-file secret-shaped text scan passed for three
  files; dependency diff audit found no dependency-file changes; and `git diff --check` exited 0
  with only existing line-ending warnings. No remote IBM operation was run by Codex for this
  checkpoint. Subsequent supervisor remote evidence showed the Hardening #2 Agent import/update
  PASS and a repeated U2 dependent private-school or university tuition reimbursement regression
  still FAIL: the Agent again inferred that Apex appears not to reimburse the requested dependent
  benefit without explicit approved negative evidence. A post-failure remote Agent export showed
  the correct Maverick model, ReAct Core style, `hr_policy_knowledge_base`, the
  `Evidence-state policy answers` guideline, and the full three-state guideline action were
  persisted remotely. Therefore the Hardening #2 U2 failure is not attributed to missing
  deployment, lost YAML configuration, or local/remote configuration mismatch; it is recorded as
  a runtime activation/adherence failure of the conditional guideline alone.
- [x] **Owner: CODEX** — **Requirement / purpose:** Apply Corrective Hardening #3 as
  defense-in-depth after remote export proved Hardening #2's native guideline was deployed but
  still not obeyed for U2. **Validation method:** Preserve the existing native
  `Evidence-state policy answers` guideline; add one concise mandatory global HR-policy safety
  invariant to the Agent instructions; then run static Agent contract tests, ADK validation,
  architecture invariants, no-hardcoding checks, secret/dependency checks, and diff checks.
  **Evidence:** The production Agent now uses both layers: global instructions contain the
  mandatory invariant that every HR policy answer may state or imply a negative policy conclusion
  only when approved Knowledge Base evidence explicitly supports that exact negative conclusion;
  missing, silent, unrelated, broadly related, or insufficient KB evidence is not negative
  evidence; and when approved KB evidence does not explicitly establish the exact requested
  positive or negative policy fact, the Agent must state that there is not enough approved policy
  information to confirm it and must not state or imply the opposite conclusion. The existing
  native `Evidence-state policy answers` guideline remains as the detailed three-state
  SUPPORTED_POSITIVE / SUPPORTED_NEGATIVE / INSUFFICIENT contract, including exact-scope and
  related-but-insufficient evidence handling. Contract tests were updated to assert the global
  instruction invariant independently of guideline activation, the guideline remains exactly one
  structured guideline with the intended branches, architecture invariants remain unchanged, and
  no U1/U2 prompt-specific terms are present in the production Agent config. YAML parsing, ADK
  `Agent.from_spec`, guideline schema validation, and `AgentSpec.model_validate` passed; static
  assertions verified name, kind, style, selected Maverick model, attached KB, empty tools, empty
  collaborators, the independent global invariant, and no regression-specific hardcoding.
  `.\.venv\Scripts\python.exe -m pytest -q` passed with `10 passed in 0.13s`; changed-file
  secret-shaped text scan passed for three files; dependency diff audit found no dependency-file
  changes; and `git diff --check` exited 0 with only existing line-ending warnings. Remote U2
  verification remains MANUAL/PENDING; no remote IBM operation was run for this checkpoint.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Import/update the KB-attached
  `hr_onboarding_agent` in the remote tenant with Corrective Hardening #3 before claiming the
  U2 policy regression is fixed. **Validation method:** Import/update the local Agent artifact
  that contains the full native HR Policy Knowledge Base attachment, mandatory global HR-policy
  safety invariant, and native evidence-state guideline; verify the tenant has that updated Agent
  configuration, then execute the primary U2 remote regression first. **Evidence:** Supervisor
  supplied remote tenant output showed `[INFO] - Existing Agent 'hr_onboarding_agent' found.
  Updating...` followed by `[INFO] - Agent 'hr_onboarding_agent' updated successfully`. This
  proves the Corrective Hardening #3 Agent import/update succeeded; semantic policy behavior is
  proven separately by the regression checkpoints below.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove through `hr_onboarding_agent` that the
  native HR Policy Knowledge Base is actually invoked. **Validation method:** Run focused remote
  Agent prompts that require policy retrieval and verify the Agent uses the attached KB rather
  than unsupported prompt-only policy invention. **Evidence:** Supervisor-supplied remote
  Reasoning Trace evidence now includes multiple direct observations that the Agent called
  `hr_policy_knowledge_base`, including R1/U2 dependent reimbursement, R2/U1 unsupported pet
  insurance, R3 full-time annual leave, and R4 leave encashment. Agent-level KB invocation is
  therefore observed and is no longer PENDING; this is bounded runtime evidence, not a claim that
  every possible HR question invokes retrieval perfectly.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove grounded policy Q&A across the five
  topics. **Validation method:** Run a planned remote question set and inspect grounding against
  source documents. **Evidence:** Supervisor-supplied runtime evidence verifies grounded
  HR-policy Q&A across the planned five domains: Leave passed with `leave-policy.txt` retrieved
  and the approved full-time annual-leave entitlement of 21 working days per calendar year
  returned; Benefits/Compensation passed with a supported benefits question, such as the gym
  subsidy, grounded to `benefits-and-compensation.txt`; Code of Conduct passed with a supported
  reporting/workplace-conduct question grounded to the approved conduct policy, while an earlier
  unsupported gifts/hospitality question safely abstained because the policy did not support it;
  IT Access passed with the approved security-incident handling answer that suspected incidents
  must be reported immediately to IT Security and employees must not independently investigate or
  resolve them; and New-Hire Orientation passed in a clean/fresh context with
  `new-hire-orientation-guide.txt` retrieved for an orientation-information question. An earlier
  natural first-day routing miss where the KB was not called remains preserved as a transient
  observed failure scenario; the later clean/fresh-session orientation regression passed. This
  proves the planned five-domain grounded Q&A batch, not universal retrieval correctness.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove unknown-policy abstention.
  **Validation method:** Ask unsupported policy questions and verify no invented policy answer;
  also verify supported positive and supported negative regressions still answer when explicitly
  grounded. **Evidence:** Final remote policy hardening regression passed with the full required
  four-test set after Corrective Hardening #3. R1/U2 unsupported dependent private-school or
  university tuition reimbursement PASS: `hr_policy_knowledge_base` was called, related
  HR/benefits material was retrieved, no explicit approved positive or negative dependent-tuition
  evidence was found, and the Agent answered that there was not enough approved policy
  information to confirm the requested dependent benefit without an unsupported negative
  conclusion. R2/U1 unsupported pet insurance PASS: the KB was called, retrieved material did not
  explicitly establish pet-insurance coverage, and the Agent abstained without inventing a
  benefit or unsupported negative policy. R3 supported positive PASS: the KB called
  `leave-policy.txt` and returned the approved full-time annual-leave entitlement of 21 working
  days per calendar year. R4 explicitly supported negative PASS: the KB called
  `leave-policy.txt`, retrieved the explicit rule that annual leave may not be encashed except
  upon resignation or termination, and returned that grounded negative rule without
  over-abstaining. Final remote policy hardening PASS is therefore R1 PASS + R2 PASS + R3 PASS +
  R4 PASS. The chronology remains preserved: the initial U2 failure failed; Hardening #1 passed
  locally and U1 remotely but U2 still failed; Hardening #2 passed local guideline validation and
  remote Agent update/export proved the guideline persisted, but U2 still failed; Hardening #3
  passed local defense-in-depth validation, remote import/update, and the full R1/R2/R3/R4
  regression set.
- [x] **Owner: CODEX** — **Requirement / purpose:** Prepare IBM/Knowledge evaluation assets using
  the installed ADK-supported evaluation path and the internal HR-policy quality bar.
  **Validation method:** Inspect the actual installed ADK 2.13.0 evaluation schema/CLI and verify
  against current official IBM documentation when this checkpoint begins; create the smallest
  domain-named evaluation ground-truth/config assets; encode the internal 8+2 quality bar; do not
  invent IBM schema, remote behavior, metrics, or thresholds; and do not execute the evaluation
  remotely in this CODEX preparation checkpoint. **Evidence:** Installed ADK 2.13.0 evaluation
  CLI/source inspection confirmed `orchestrate evaluations evaluate` accepts `--config`,
  `--test-paths`, `--output-dir`, `--env-file`, and optional Langfuse, and the installed
  controller merges YAML config before constructing the evaluation config. Current IBM
  documentation was cross-checked for the ground-truth JSON shape, required config fields
  `test_paths` and `output_dir`, optional `n_runs`, and output artifacts under the evaluation
  results tree. Created minimal IBM input config `evaluations/hr_policy/config.yaml` with only
  `test_paths`, `output_dir: artifacts/evaluations/hr_policy`, and `n_runs: 1`. Created exactly
  10 IBM-compatible JSON ground-truth cases under `evaluations/hr_policy/ground_truth/`, each
  using only `agent`, `goals`, `goal_details`, `story`, and `starting_sentence`; all cases target
  `hr_onboarding_agent` and the `summarize` text goal. Created internal-only manifest
  `evaluations/hr_policy/quality_bar.yaml`, explicitly marked `not_passed_to_ibm: true`, encoding
  the 8 answerable / 2 intentionally unanswerable case split, all five required HR domains, and
  the project quality bar: at least 7/8 answerable questions grounded correctly, 2/2
  unanswerable questions abstain correctly, and 0 fabricated HR-policy facts. The 8 answerable
  cases cover full-time annual leave, leave encashment prohibition while employed, medical aid
  dependent scope, employee-only Study Assistance, Code of Conduct reporting/retaliation, IT
  security-incident handling, natural first-day orientation information, and leave carryover
  timing/exception/scope. The 2 unanswerable cases are pet insurance and dependent
  private-school/university tuition reimbursement, both phrased as insufficient approved policy
  information without converting absence of evidence into a negative policy conclusion. Local
  deterministic validation passed: config has only the three intended fields; JSON cases are
  exactly 10 with 8/2 answerability split; all five domains are covered; IBM JSON contains no
  custom fields; manifest files match the ground-truth directory; supported facts are present in
  approved `mock_docs/` sources; pet insurance and dependent tuition are not established in the
  approved sources. `.\.venv\Scripts\python.exe -m pytest -q` passed with
  `10 passed in 0.14s`; `git -c safe.directory=D:/Projects/agentic-orchestration-agent-pipeline
  diff --check` passed with only pre-existing LF-to-CRLF warnings; scoped secret-shaped scan of
  `evaluations/hr_policy` found no matches; dependency diff audit found no dependency-file
  changes. No remote IBM evaluation, tenant mutation, Agent change, Knowledge Base change,
  production source change, IT/booking/persistence work, staging, commit, or push was performed.
  Local `.env` exists, but only key names were inspected and they are not the installed
  evaluation docs' exact `WO_*` / `WATSONX_*` auth keys, so the MANUAL evaluation checkpoint must
  supply or map the tenant-supported auth variables before execution.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Execute/observe IBM/Knowledge evaluation
  remotely and record the metrics genuinely exposed by the tenant-supported path. **Validation
  method:** Run the prepared evaluation through the real installed/tenant-supported path; retain
  actual output; record Knowledge Base call evidence, retrieval confidence, response confidence,
  faithfulness/groundedness, answer relevancy, or other exposed Knowledge evaluation metrics
  where genuinely available; record unavailable metrics as unavailable; evaluate the internal
  8+2 bar; and do not invent thresholds or relabel emulated values as IBM output. **Evidence:**
  Supervisor-supplied remote evidence confirms the prepared IBM/Knowledge evaluation executed
  against Draft tenant `project2` in `eu-de` with ADK 2.13.0, Langflow 1.7.1, evaluation
  framework extra `ibm-watsonx-orchestrate-evaluation-framework==1.5.2`, and target Agent
  `hr_onboarding_agent`. The evaluator discovered and completed exactly the intended 10
  datasets. Observed IBM average metrics were: Runs `1.0`, Orchestrate Agent Routing F1 `1.0`,
  Average Agent Response Time `4.69` seconds, Total Tool Calls `1.0`, Expected Tool Calls `0.0`,
  Knowledge Answer Relevancy `0.92`, Average Document Retrieval Confidence `0.68`, Knowledge
  Faithfulness `1.00`, Retrieval Confidence `0.51`, Keyword Match `0.0`, Semantic Match `0.2`,
  Text Match `0.0`, and Journey Success `0.0`. Response Confidence was not exposed / not
  available in this run and is not treated as zero. No numeric Knowledge-confidence threshold was
  invented. Supervisor internal audit of the actual conversations against approved HR sources
  passed the internal 8+2 bar: 8/8 answerable cases grounded correctly, 2/2 unanswerable cases
  abstained correctly, and 0 fabricated HR-policy facts. This internal result is not relabeled as
  an IBM metric. Generic Text/Journey values are retained honestly as observed zeros because the
  current text-goal ground truth has no expected KB tool-call sequence (`summarize: []`), while
  the actual Agent correctly invoked `hr_policy_knowledge_base`; Knowledge-specific IBM metrics
  and direct result inspection are the relevant bounded G2 Knowledge evidence. Case 02
  annual-leave encashment had a grounded correct final conclusion with a minor unnecessary early
  abstention phrase; this was observed, not a production blocker. Case 09 pet insurance abstained
  correctly early, then entered an evaluation-user polite continuation loop of approximately 30
  total / 15 LLM steps; this is recorded as a simulator termination observation, not an
  HR-policy correctness failure. IBM `orchestrate evaluations analyze -d <run-directory>
  --env-file .env` is BLOCKED BY NEW-PIPELINE / ANALYZER SCHEMA COMPATIBILITY because the
  analyzer expected enum-like `text_match` values while the generated artifact contained numeric
  `text_match = 0`; no legacy rerun was performed and generated metrics were not edited. Durable
  sanitized evidence is retained in
  `artifacts/evaluations/hr_policy/2026-08-13_03-10-16/EVALUATION_EVIDENCE.md` and
  `config.sanitized.yml`; raw token-bearing `config.yml`, repository-local
  `ibm_eval_2026-08-13_03-10-16.zip`, and transient `debug/evaluation_order.txt` were removed.
  Recursive artifact secret-shaped scan passed after sanitization. No Agent, Knowledge Base,
  ground-truth case, source document, retrieval tuning, or IBM remote rerun was performed by
  Codex in this closeout.
- [x] **Owner: CODEX** — **Requirement / purpose:** Implement minimal COS JSON persistence tools
  for `it_request` and `orientation_booking`. **Validation method:** Local schema/contract tests,
  mocked stdlib REST transport tests, secret scan, and dependency audit. **Evidence:** Created
  production domain module `tools/onboarding_persistence.py` and empty packaging companion
  `tools/onboarding_persistence_requirements.txt`. The implementation preserves the frozen
  backend and transport: IBM Cloud Object Storage active replacement bucket
  `agentic-onboarding-p2-9g821-01`, endpoint
  `https://s3.eu-de.cloud-object-storage.appdomain.cloud`, runtime Orchestrate `API_KEY_AUTH`
  connection `cos_onboarding`, IBM IAM token exchange, COS REST `PUT` plus verifying `GET`,
  Python standard-library `urllib`, and no third-party COS/HTTP dependency.
  Public tools are `persist_it_request(employee_name, employee_role, required_systems)` and
  `persist_orientation_booking(selected_slot)`, both decorated with ADK expected credentials
  `cos_onboarding` / `api_key_auth`. IT records use object keys
  `it_requests/<request_id>.json` and bounded JSON fields `record_type`, `request_id`,
  `employee_name`, `employee_role`, `required_systems`, `status`, and `created_at_utc`.
  Orientation booking records use `orientation_bookings/<booking_id>.json` and bounded JSON
  fields `record_type`, `booking_id`, `selected_slot`, `status`, and `created_at_utc`; no booking
  Flow, schedule, or slot validation was implemented. Return values expose only `status`,
  `persisted`, `record_type`, `record_id`, `object_key`, and `verified`; API keys, IAM tokens,
  Authorization headers, credential objects, and raw remote error bodies are not returned.
  `tests/test_onboarding_persistence.py` passed with `13 passed in 0.70s`, proving credential
  contract, IAM request construction, eu-de endpoint/bucket, object prefixes, unique IDs,
  bounded payloads, one PUT plus semantic GET verification, sanitized IAM/PUT/GET/mismatch
  failures, no list/delete call, no secret value in results/errors, and no forbidden dependency
  import. ADK metadata inspection passed for two tools and exact expected credentials. No real
  network request or remote IBM operation was performed.
- [x] **Owner: CODEX** — **Requirement / purpose:** Implement the IT request flow/capability with
  employee name, employee role, and required systems. **Validation method:** Local flow/schema,
  explicit-state retention, confirmation-branch, and payload contract tests verify only the three
  required fields, no company-email prerequisite, no invented values, No causes no persistence,
  and Yes produces one intended persistence call. **Evidence:** Created domain Flow artifact
  `flows/it_request_flow.py` without modifying or attaching it to `agents/hr_onboarding_agent.yaml`.
  The capability name is `it_request_flow`. Required business fields are exactly
  `employee_name`, `employee_role`, and `required_systems`; `required_systems` is represented as
  one non-empty user-supplied text value to preserve user wording and avoid unapproved LLM
  parsing. The module defines explicit Pydantic input, private state, final-state, and output
  schemas, plus deterministic helpers for normalizing explicit state, detecting only genuinely
  missing fields, merging collected values without overwriting retained values, rendering a
  complete confirmation summary, cancellation, and submission. A supervisor correction on
  2026-08-13 rejected structural-only Flow validation; the corrected Flow now proves the actual
  ADK graph wiring. The ADK builder uses installed `@flow`, `Flow.userflow`, standalone
  `UserFlow.field(...)` nodes for field-based collection, a `UserFieldKind.Boolean`
  confirmation field, explicit branches, and one `persist_it_request` tool node named
  `persist_it_request_once`; no form-based User Activity pattern and no LLM node is used.
  `assemble_final_request` is the one authoritative complete request state before confirmation,
  with exactly `employee_name`, `employee_role`, and `required_systems`. Its explicit
  `Node.map_input()` assignments select the normalized originally supplied value first, otherwise
  the corresponding User Activity output: `flow.ask_employee_name.output.value`,
  `flow.ask_employee_role.output.value`, and `flow.ask_required_systems.output.value`. The
  confirmation User Activity maps its inputs from `flow.assemble_final_request.output.*`; its
  output text field has a field-level `DataMap` to `self.input.value` that displays the actual
  final employee name, role, and systems before the Boolean confirmation. The Yes branch is the
  only path to `persist_it_request_once`, and that single tool node explicitly maps exactly
  `employee_name`, `employee_role`, and `required_systems` from
  `flow.assemble_final_request.output.*`. The No/default branch maps the final retained values
  into `cancelled_result`, returns `status = cancelled`, `persisted = false`, and sets
  `request_id`, `object_key`, and `verified` to `None` without invoking persistence.
  `submitted_result` maps retained field values from final state and maps `request_id`,
  `object_key`, and `verified` from the real persistence node output
  `flow.persist_it_request_once.output.record_id`, `.object_key`, and `.verified`. Explicit
  `Flow.map_output()` assignments produce the `ITRequestResult` fields from `submitted_result`
  on Yes and `cancelled_result` on No. Local inspection of installed ADK 2.13.0 confirmed
  `Node.map_input()` and `Flow.map_output()` create `DataMap` assignments with
  `assignmentType = pyExpression`; `flow.compile()` is local model compilation and
  `compile_deploy()` was not used. `tests/test_it_request_flow_contract.py` now asserts the
  actual ADK model maps, graph gates, one persistence node/path, field-based Boolean
  confirmation, absence of `.form()`/LLM/company-email prerequisite, final output maps, and
  compile-level preservation of mappings; it passed with `19 passed, 28 warnings in 9.76s`.
  Targeted persistence plus IT Flow tests passed with `32 passed, 28 warnings in 9.57s`; full
  suite passed with `42 passed, 28 warnings in 12.23s`. Installed importer discovery, with
  connection validation patched out to avoid remote/user-profile mutation, found both
  `@tool` functions in `tools/onboarding_persistence.py`: `persist_it_request` and
  `persist_orientation_booking`, each retaining expected credential app id `cos_onboarding`.
  A subsequent supervisor remote-import attempt proved the production persistence tools imported
  successfully, then `orchestrate tools import --kind flow --file flows\it_request_flow.py`
  failed before Flow creation with `No flow model found in file flows\it_request_flow.py`.
  Local root-cause inspection of installed ADK 2.13.0
  `load_flow_model_from_file()` showed that the importer imports the Python module and scans
  module members for `FlowWrapper`; the previous `@flow` definition was nested inside
  `build_it_request_flow()` and therefore not visible to that module-level scan. The compatibility
  correction exposed exactly one module-level `@flow` wrapper named `it_request_flow` while
  preserving the approved graph builder in `_configure_it_request_flow()` and keeping
  `build_it_request_flow()` as a local helper that invokes the same wrapper. A regression test now
  calls the installed `load_flow_model_from_file()` against `flows/it_request_flow.py` and asserts
  the loader-visible model name, required nodes, one `persist_it_request` node, final-state input
  maps, confirmation input/data maps, persistence input maps, confirmation branch, and final
  output maps. Local loader diagnostic passed with `FLOW_LOADER=PASS`,
  `FLOW_NAME=it_request_flow`, and `NODE_COUNT=15`. After this import-compatibility correction,
  `tests/test_it_request_flow_contract.py` passed with `21 passed, 84 warnings in 15.43s`, full
  pytest passed with `44 passed, 84 warnings in 21.43s`, and `git diff --check` passed with only
  pre-existing LF-to-CRLF warnings. The MANUAL remote Flow import checkpoint remains unchecked
  until the supervisor reruns the real remote import and isolated runtime proof.
  Supervisor then supplied qualifying real-tenant runtime evidence: the Flow imported remotely
  as `it_request_flow`, was attached to temporary isolated harness `it_request_flow_test_agent`,
  started successfully, and prompted in order for `employee_name`, `employee_role`, and
  `required_systems`. After the user supplied `G2 No Test Adnan`,
  `Validation Analyst G2-NO-01`, and `Slack, Jira, G2-NO-01`, the Flow failed before
  confirmation in `assemble_final_request` with `employee_name is required before IT request
  confirmation`. Confirmation was not reached, no Yes/No selection occurred, persistence was not
  reached, and no COS write or cancellation/confirmation outcome is claimed. Local inspection of
  installed ADK 2.13.0 verified that a field-based UserFlow input node exposes the collected
  value at its nested field path, such as `flow.employee_name.output.value`, and
  `UserFlow.map_output("value", ...)` serializes that value to `flow.output.value`. The local
  runtime correction explicitly maps `ask_employee_name.output.value` from
  `flow.employee_name.output.value`, `ask_employee_role.output.value` from
  `flow.employee_role.output.value`, `ask_required_systems.output.value` from
  `flow.required_systems.output.value`, and `confirm_it_request.output.value` from
  `flow.confirmed.output.value`. Field identifiers remain unchanged while display names were
  added for clearer remote labels: `Employee name`, `Employee role`, `Required systems`, and
  `Submit IT access request`. Regression tests now assert the nested field output schemas and
  UserFlow output maps in both the built Flow and the importer-visible model. Local loader
  diagnostic passed with `FLOW_LOADER=PASS`, `FLOW_NAME=it_request_flow`, `NODE_COUNT=15`, and
  importer-visible output maps for the four UserFlows. `tests/test_it_request_flow_contract.py`
  passed with `25 passed, 100 warnings in 17.40s`; full pytest passed with
  `48 passed, 100 warnings in 16.47s`; and `git diff --check` passed with only pre-existing
  LF-to-CRLF warnings. This is local correction readiness only; the MANUAL isolated Flow
  checkpoint remains unchecked until corrected remote runtime evidence exists.
  No remote IBM action, COS network call, Agent integration, orientation booking Flow, staging,
  commit, or push was performed.
  Subsequent replacement-tenant Preview Chat evidence proved the Flow remained remotely callable
  and the field-based User Activities prompted for `Employee name`, `Employee role`, and
  `Required systems`; the submitted values `G2 Cancel Test 20260816-A`, `QA Engineer`, and
  `Github, Slack` were accepted by their User Activities. Immediately after the third User
  Activity completed, the Flow failed at `assemble_final_request` with `ValueError:
  employee_name is required before IT request confirmation`. Confirmation and persistence were
  not reached. Root cause: the correction still depended on synthetic UserFlow parent output
  adapters such as `flow.ask_employee_name.output.value` and analogous role, systems, and
  confirmation outputs, but replacement-tenant runtime evidence showed those parent outputs did
  not propagate across User Activity resume. The follow-up local correction changes only the
  internal UserFlow-to-parent mapping strategy: parent Flow maps now read nested field outputs
  directly, such as `flow.ask_employee_name.employee_name.output.value`, and the confirmation
  branch/output maps read `flow.confirm_it_request.confirmed.output.value`. Public schemas,
  required IT fields, field-based User Activities, the Boolean confirmation, one
  `persist_it_request` node, and Agent/Flow architecture remain unchanged. The MANUAL isolated
  Flow checkpoint remains unchecked until the corrected mapping is re-imported and remotely
  retested.
  A second replacement-tenant retest re-imported the Flow successfully and again invoked it
  through isolated harness `it_request_flow_test_agent`. Preview Chat requested `Employee name`,
  `Employee role`, and `Required systems`; accepted `G2 Mapping Retest 20260816-A`,
  `QA Engineer`, and `Github, Slack`; then failed again at `assemble_final_request` with
  `ValueError: employee_name is required before IT request confirmation`. This proves the
  direct-dot nested field path remained unproven in remote runtime and that the first
  parent-output root-cause hypothesis was incomplete. The current local correction is based on
  the actual compiled ADK 2.13.0 model plus IBM's documented nested User Activity reference
  syntax: the User Activity field names now match the runtime labels (`Employee name`,
  `Employee role`, `Required systems`, and `Submit IT access request`) and downstream maps use
  bracketed field-name paths such as `flow["ask_employee_name"]["Employee name"].output.value`.
  The ADK compiler sanitizes those nested node keys in the model (`Employee_name`,
  `Employee_role`, `Required_systems`, and `Submit_IT_access_request`) while preserving the
  field names and display names. This remains local correction readiness only; the MANUAL
  isolated Flow checkpoint remains unchecked until this version is remotely re-imported and
  retested.
  A third replacement-tenant Preview Chat retest then proved the bracket-path correction imported
  successfully and still collected the three missing values remotely: `Employee name`,
  `Employee role`, and `Required systems` were requested and accepted before the same
  `assemble_final_request` failure occurred with `ValueError: employee_name is required before
  IT request confirmation`. This rejects nested UserFlow field path syntax alone as the root
  cause. The revised local correction stops parent-level reconstruction from completed
  UserFlow field outputs entirely: explicit initial inputs initialize authoritative
  `flow.private` state, each missing-field UserFlow captures the collected value into
  `flow.private` before leaving that UserFlow, `assemble_final_request` reads only
  `flow.private.employee_name`, `flow.private.employee_role`, and
  `flow.private.required_systems`, and confirmation is captured into `flow.private.confirmed`
  before the parent confirmation branch executes. This aligns the production IT Flow with the
  specification's explicit Flow/application-state requirement and reuses the G1B-proven
  principle of consuming/capturing User Activity state before crossing the UserFlow boundary.
  This remains local correction readiness only; the MANUAL isolated Flow checkpoint remains
  unchecked until this private-state version is remotely re-imported and retested.
  A pre-reimport local scope audit then found two nested-workflow scope defects in the
  private-state version before another remote test: capture scripts inside nested UserFlows were
  still mapped from top-level `flow.<field>.output.value` sibling paths, and the confirmation
  display read top-level `flow.input.*` values that can be empty when fields are collected
  interactively. IBM's current ADK expression documentation distinguishes `flow` as the
  top-level agentic workflow context and `parent` as the current agentic workflow context for
  current-workflow inputs and sibling node outputs. The local correction therefore keeps the
  `flow.private` architecture but changes the four capture maps to
  `parent.employee_name.output.value`, `parent.employee_role.output.value`,
  `parent.required_systems.output.value`, and `parent.confirmed.output.value`, and changes the
  confirmation display to `parent.input.employee_name`, `parent.input.employee_role`, and
  `parent.input.required_systems`. ADK 2.13.0 locally accepted and serialized these parent-scope
  expressions through the compiled nested model and installed loader. Regression tests now inspect
  the built Flow and compiled/importer-visible nested graphs for those exact parent-scope maps,
  while preserving private-state assembly, private confirmation branching, zero persistence on
  the default/No path, and exactly one persistence node reachable only through the Yes path.
  `tests/test_it_request_flow_contract.py` passed with `35 passed, 112 warnings in 31.40s`; full
  pytest passed with `58 passed, 112 warnings in 31.31s`; and local loader diagnostic passed with
  `FLOW_LOADER=PASS`, `FLOW_NAME=it_request_flow`, and `NODE_COUNT=15`. This remains local
  correction readiness only; the MANUAL isolated Flow checkpoint remains unchecked until this
  parent-scope private-state version is remotely re-imported and retested.
  A fourth replacement-tenant retest accepted a valid employee name in the field-based User
  Activity, then failed immediately at `capture_employee_name`. The field-to-capture-Script
  boundary is therefore rejected, and incremental nested-path/private-state patches are stopped.
  The IT interaction is rebuilt around one field-only `it_request_session` UserFlow, following
  the G1B-proven principle that one UserFlow owns collection, retained-value display, Boolean
  confirmation, and an explicit output boundary. Its output contract exposes only
  `employee_name`, `employee_role`, `required_systems`, and `confirmed`; top-level branching,
  cancellation, and the single persistence path consume only `it_request_session.output.*`.
  ADK 2.13.0 locally validated, compiled, serialized, and loaded this graph with
  `FLOW_LOADER=PASS`, `FLOW_NAME=it_request_flow`, `TOP_LEVEL_NODE_COUNT=7`, and
  `IT_REQUEST_SESSION_NODE_COUNT=10`. The rebuilt contract suite passed with `24 passed, 92
  warnings in 13.29s`; full pytest passed with `47 passed, 92 warnings in 11.19s`; and
  `git diff --check` passed with only existing LF-to-CRLF warnings. This is local rebuild
  readiness only; the MANUAL isolated Flow checkpoint remains unchecked pending remote re-import
  and both cancellation and confirmed runtime evidence.
  The rebuilt single-UserFlow version was then invoked in replacement-tenant Preview Chat and
  successfully collected all three missing values without either the prior capture failure or
  `assemble_final_request` failure. It reached `proposed_it_request` and displayed the Boolean
  Yes/No confirmation, proving the single-UserFlow architecture remotely viable, but the Text
  output showed only its static heading and not the three authoritative values. Inspection of
  ADK 2.13.0 and IBM's current User Activity documentation showed that visible Text output is
  rendered from the field's `text` property, while the failed implementation mapped the summary
  to `self.input.value`. The correction is therefore limited to moving the unchanged three lazy
  authoritative expressions into documented `{...}` interpolation in `text`; graph structure,
  session outputs, confirmation branching, and persistence mappings remain unchanged. Targeted
  tests passed with `25 passed, 96 warnings in 14.02s`; full pytest passed with `48 passed, 96
  warnings in 13.01s`; and the installed loader passed with unchanged node counts of 7 top-level
  and 10 inside `it_request_session`. The MANUAL checkpoint remains unchecked; confirmation and
  persistence outcomes have not yet been remotely tested for this rendering correction.
  The rendering-only interpolation correction was imported and remotely tested in the
  replacement tenant. The single-UserFlow collection path still succeeded, and the proposed
  review reached the Boolean confirmation, but all three compound conditional Text placeholders
  rendered as `<unresolved>`. This proves the tenant does not resolve the current compound
  conditional expressions inside Text interpolation. The conditional business selection remains
  in deterministic branch and DataMap expressions, while visible Text review is changed to use
  only simple documented workflow references: a static `proposed_it_request` heading followed by
  per-field source-selection branches and six simple Text outputs for supplied versus collected
  employee name, employee role, and required systems. The MANUAL isolated IT Flow checkpoint
  remains unchecked pending remote re-import and review/persistence evidence for this corrected
  display topology.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Import/deploy the IT Request Flow as an
  Orchestrate callable tool/capability and prove it works remotely in isolation before final
  Agent integration. **Validation method:** Import/deploy the Flow, invoke it outside final
  Agent integration, and observe the deterministic request-collection/confirmation behavior.
  **Evidence:** Supervisor-provided replacement-tenant evidence verified `it_request_flow` was
  invoked successfully through isolated `it_request_flow_test_agent`; the field-based flow
  requested missing `employee_name`, `employee_role`, and `required_systems`, retained the
  collected values, visibly reviewed them before confirmation, and displayed explicit Yes/No
  confirmation. The successful review example used employee name
  `G2 YES PROOF 20260817-0251`, employee role `QA Engineer`, and required systems
  `Github, Slack`.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove missing IT fields are requested and
  never invented. **Validation method:** Remote isolated Flow tests omit each required field and
  verify only employee name, employee role, and required systems are requested. **Evidence:**
  Supervisor-provided evidence verified the isolated IT Flow requested missing employee name,
  employee role, and required systems, introduced no additional required business field, and
  retained/reviewed the collected values before confirmation.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove IT cancellation causes no persistence.
  **Validation method:** Cancel in the isolated remote IT Flow at confirmation and verify no
  matching COS JSON record exists. **Evidence:** Supervisor-provided evidence verified the user
  selected No, the runtime result was `status=cancelled` and `persisted=false`, and the
  read-only COS audit reported `AUDIT_IAM_TOKEN_EXCHANGE=PASS`, `COS_AUDIT_LIST=PASS`,
  `RECENT_IT_OBJECTS_SINCE_NO_TEST=0`, and `IT_CANCEL_COS_ZERO_WRITE=PASS`.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove IT confirmation creates exactly one
  record. **Validation method:** Perform one confirmed action in the isolated remote IT Flow and
  verify exactly one intended matching COS JSON record. **Evidence:** Supervisor-provided
  evidence captured COS baseline `IT_OBJECT_COUNT_BEFORE_YES=2`; after one confirmed Yes the
  audit reported `IT_OBJECT_COUNT_AFTER_YES=3`, `NEW_OBJECTS_AFTER_YES=1`, and
  `IT_CONFIRM_COS_EXACTLY_ONE_WRITE=PASS`. Direct GET of
  `it_requests/a8ccdde56eac4d539dde3f1218c3cad9.json` returned
  `record_type=it_request`, `request_id=a8ccdde56eac4d539dde3f1218c3cad9`,
  `employee_name=G2 YES PROOF 20260817-0251`, `employee_role=QA Engineer`,
  `required_systems=Github, Slack`, `status=submitted`, and
  `created_at_utc=2026-08-16T23:54:33.031423Z`. Structural audit reported
  `RECORD_TYPE=PASS`, `REQUEST_ID_PRESENT=PASS`, `EMPLOYEE_NAME_PRESENT=PASS`,
  `EMPLOYEE_ROLE_PRESENT=PASS`, `REQUIRED_SYSTEMS_PRESENT=PASS`, `STATUS_SUBMITTED=PASS`,
  `CREATED_AT_PRESENT=PASS`, and `IT_YES_PERSISTED_JSON_STRUCTURAL_MATCH=PASS`. The two
  pre-existing IT objects were historical manual test objects; acceptance is based on the
  before/after delta of exactly one new object.
- [x] **Owner: CODEX** — **Requirement / purpose:** Define stable hardcoded orientation slots.
  **Validation method:** Local tests validate slot identifiers, display values, selection
  behavior, and that the LLM cannot invent production orientation slots. **Evidence:** Frozen
  the canonical production mock `selected_slot` values in `artifacts/development_history/PROJECT_SPEC_HISTORY.md` as exactly
  `Monday 09:00-10:00`, `Wednesday 13:00-14:00`, and `Thursday 15:00-16:00`; no dates, calendar
  integration, timezone API, generated slots, capacity, or concurrency is authorized. Targeted
  Booking contract tests passed with `21 passed, 76 warnings in 10.23s`; full pytest passed
  with `72 passed, 184 warnings in 247.46s`; and installed loader validation reported
  `APPROVED_SLOT_COUNT=3` and `CHOICE_CONSTRAINT_VALIDATED=PASS`.
- [x] **Owner: CODEX** — **Requirement / purpose:** Implement the orientation booking
  flow/capability. **Validation method:** Local schema, explicit selected-slot retention,
  valid-slot, confirmation-branch, and persistence contract tests verify No causes no persistence
  and Yes produces one intended persistence call. **Evidence:** Implemented
  `flows/orientation_booking_flow.py` as a bounded deterministic Flow with one field-based
  `orientation_booking_session` UserFlow, static approved-slot Choice field, visible selected
  slot review, explicit Boolean confirmation, top-level No/default cancellation path, and a
  Yes-only `persist_orientation_booking_once` tool node. Tests in
  `tests/test_orientation_booking_flow_contract.py` verify public schemas, compiled topology,
  UserFlow output maps, parent-only session-output consumption, zero persistence on No/default,
  sole persistence entry on Yes, exactly one persistence node, and loader discovery. Targeted
  tests passed with `21 passed, 76 warnings in 10.23s`; full pytest passed with
  `72 passed, 184 warnings in 247.46s`; installed loader validation reported
  `FLOW_LOADER=PASS`, `FLOW_NAME=orientation_booking_flow`, `TOP_LEVEL_NODE_COUNT=7`,
  `ORIENTATION_BOOKING_SESSION_NODE_COUNT=6`, `APPROVED_SLOT_COUNT=3`, and
  `CHOICE_CONSTRAINT_VALIDATED=PASS`. This is local readiness only; the Booking MANUAL remote
  checkpoints remain unchecked.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Import/deploy the Orientation Booking Flow
  as an Orchestrate callable tool/capability and prove it works remotely in isolation before
  final Agent integration. **Validation method:** Import/deploy the Flow, invoke it outside final
  Agent integration, and observe stable-slot selection and confirmation behavior. **Evidence:**
  Supervisor-provided replacement-tenant evidence verified `orientation_booking_flow` was invoked
  successfully through isolated `orientation_booking_flow_test_agent`. The Choice User Activity
  displayed exactly `Monday 09:00-10:00`, `Wednesday 13:00-14:00`, and
  `Thursday 15:00-16:00`, with no fourth slot; selected-slot review and explicit Boolean
  confirmation were observed before persistence on the confirmed path.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove the isolated remote Booking Flow uses
  only valid approved slots. **Validation method:** Remote isolated Flow tests verify slot
  display/selection behavior and reject or clarify invalid slot requests without LLM-invented
  slots. **Evidence:** Supervisor-provided evidence verified the Choice UI exposed only the three
  approved slots listed above. When the user requested
  `I want to book orientation on Friday 09:00-10:00.`, arbitrary non-choice free text was
  rejected with `Value 'I want to book orientation on Friday 09:00-10:00.' is not a valid
  option. The flow has ended.` No Friday slot was selected, confirmation was not reached, and no
  persistence outcome is claimed for that invalid-choice proof.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove booking cancellation causes no
  persistence. **Validation method:** Cancel in the isolated remote Booking Flow at confirmation
  and verify no matching COS JSON record exists. **Evidence:** Supervisor-provided evidence
  verified the user selected `Monday 09:00-10:00`, reviewed it before Boolean confirmation,
  selected No, and the runtime result was semantically `status=cancelled` and `persisted=false`.
  The read-only COS audit reported `AUDIT_IAM_TOKEN_EXCHANGE=PASS`, `COS_AUDIT_LIST=PASS`,
  `RECENT_BOOKING_OBJECTS_SINCE_NO_TEST=0`, and `BOOKING_CANCEL_COS_ZERO_WRITE=PASS`.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove booking confirmation creates exactly
  one record. **Validation method:** Perform one confirmed action in the isolated remote Booking
  Flow and verify exactly one intended matching COS JSON record. **Evidence:** Supervisor-
  provided evidence captured baseline `BOOKING_OBJECT_COUNT_BEFORE_YES=0`; after selecting and
  reviewing `Wednesday 13:00-14:00` and selecting Yes, the runtime result was `status=booked`
  and `persisted=true`. The audit reported `BOOKING_OBJECT_COUNT_AFTER_YES=1`,
  `NEW_BOOKING_OBJECTS_AFTER_YES=1`, `BOOKING_CONFIRM_COS_EXACTLY_ONE_WRITE=PASS`, and
  `BOOKING_YES_OBJECT_GET=PASS` for
  `orientation_bookings/194bb2cde6b644bda9c088ecd8c1bc3f.json`. Direct GET returned
  `record_type=orientation_booking`, `booking_id=194bb2cde6b644bda9c088ecd8c1bc3f`,
  `selected_slot=Wednesday 13:00-14:00`, `status=booked`, and
  `created_at_utc=2026-08-17T01:01:22.205075Z`; structural audit checks all passed.
- [x] **Owner: CODEX** — **Requirement / purpose:** Configure the three clear, non-overlapping
  capability descriptions from the Agent contract. **Validation method:** Static contract audit
  and capability-selection test cases verify policy information, actual IT access request, and
  actual orientation booking remain semantically distinct; ambiguous requests require
  clarification before action capability invocation. **Evidence:** Configured the production
  `hr_onboarding_agent` instructions to separate HR Policy Knowledge from actual IT access
  requests and actual orientation booking actions. Static contract cases cover Jira policy
  information, Jira/Slack/GitHub access requests, orientation information, orientation booking,
  ambiguous Jira wording, and out-of-scope requests. Targeted Agent contract tests passed with
  `25 passed in 2.01s`; full pytest passed with `89 passed, 184 warnings in 244.78s`.
- [x] **Owner: CODEX** — **Requirement / purpose:** Assemble/update the complete
  `hr_onboarding_agent` artifact with the full KB, IT capability, booking capability, approved
  instructions, non-overlapping descriptions, and frozen G1 strategy. **Validation method:** Run
  all available local/static/compile validation and audit that `hr_onboarding_agent` remains the
  top-level ReAct decision-maker and is not replaced by one fixed onboarding Flow. **Evidence:**
  Updated `agents/hr_onboarding_agent.yaml` as the complete Part A ReAct Core Agent with
  `knowledge_base: [hr_policy_knowledge_base]`, tools exactly `it_request_flow` and
  `orientation_booking_flow`, no collaborators, no direct persistence tools, no test agents, and
  no G1 spikes. The Agent preserves the frozen model and policy evidence-state invariant while
  delegating confirmation and persistence to the protected Flow capabilities. Targeted Agent
  contract tests passed with `25 passed in 2.01s`; IT and Booking regression tests passed with
  `49 passed, 184 warnings in 269.33s`; full pytest passed with
  `89 passed, 184 warnings in 244.78s`.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Import and prove the complete ReAct Core
  Agent. **Validation method:** Import the prepared real Agent and run one full multi-turn
  conversation covering policy Q&A, IT request, IT explicit confirmation, orientation booking,
  booking explicit confirmation, and clear completion/exit. **Evidence:** Supervisor-provided
  replacement-tenant evidence verified a fresh complete `hr_onboarding_agent` conversation
  covered grounded annual-leave policy Q&A, actual IT access request, explicit IT review and
  confirmation, successful IT persistence, continuation after IT completion without duplicate
  side effect, orientation-information handling without booking, actual orientation booking,
  explicit booking review and confirmation, successful booking persistence, final summary, and
  clear conversational exit. The annual-leave answer used `hr_policy_knowledge_base` and
  returned 21 working days of paid annual leave per calendar year for a full-time new hire.
  Unsupported vendor-gift monetary-limit policy behavior was also observed previously: the
  Agent did not invent a monetary limit and stated there was not enough approved policy
  information to confirm such a value. Clean E2E IT evidence used employee name
  `G2 CLEAN E2E IT 20260817-B`, role `QA Engineer`, and systems `Slack, GitHub`; after Yes, the
  runtime was semantically `status=submitted` and `persisted=true`. COS delta was
  `IT_COUNT_BEFORE=4`, `IT_COUNT_AFTER=5`, `CLEAN_E2E_NEW_IT_OBJECTS=1`. Direct GET of
  `it_requests/983a247c75414e94b0cb0c7980f678eb.json` returned `record_type=it_request`,
  `request_id=983a247c75414e94b0cb0c7980f678eb`,
  `employee_name=G2 CLEAN E2E IT 20260817-B`, `employee_role=QA Engineer`,
  `required_systems=Slack, GitHub`, `status=submitted`, and
  `created_at_utc=2026-08-17T02:26:19.094958Z`; all structural and exact-match checks passed.
  Clean E2E Booking selected and reviewed `Wednesday 13:00-14:00`; after Yes, the runtime was
  semantically `status=booked` and `persisted=true`. COS delta was
  `BOOKING_COUNT_BEFORE=2`, `BOOKING_COUNT_AFTER=3`,
  `CLEAN_E2E_NEW_BOOKING_OBJECTS=1`. Direct GET of
  `orientation_bookings/61298d135f6d47d3b16312be969ccaec.json` returned
  `record_type=orientation_booking`, `booking_id=61298d135f6d47d3b16312be969ccaec`,
  `selected_slot=Wednesday 13:00-14:00`, `status=booked`, and
  `created_at_utc=2026-08-17T02:27:28.909238Z`; all structural and exact-match checks passed.
  Overall clean E2E checks reported `CLEAN_E2E_SIDE_EFFECT_DELTA=PASS` and
  `CLEAN_FINAL_AGENT_E2E_PERSISTENCE=PASS`. Detailed consolidated evidence is recorded in
  `artifacts/milestone_4_part_a_end_to_end_evidence.md`.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove graceful out-of-scope behavior and
  ambiguous capability selection. **Validation method:** Run planned remote prompts and verify
  polite decline/clarification without unintended tools or side effects; for example, ambiguous
  Jira questions clarify policy-information intent versus access-request intent. **Evidence:**
  Supervisor-provided replacement-tenant evidence verified a fresh out-of-scope hotel-reservation
  request was politely declined as outside HR onboarding scope; the Agent did not invoke
  `it_request_flow`, did not invoke `orientation_booking_flow`, and did not claim a reservation.
  For ambiguous Jira wording, `I'm sorting out Jira for onboarding and I'm not sure what I need.
  Can you help?`, the Agent used `hr_policy_knowledge_base` for safe Jira/access-policy
  information, did not invoke `it_request_flow`, did not create a side effect, and then asked
  whether the user wanted to proceed with requesting Jira access. When the user clarified,
  `I only want to understand the access rules. Don't submit anything.`, the Agent remained
  informational and no persistence occurred. This satisfies the side-effect safety contract: the
  ambiguous wording did not invoke the IT side-effect capability before action intent was clear.
  It is not overstated as clarification before every informational retrieval.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove the complete Agent does not
  autonomously repeat a completed side effect. **Validation method:** After a confirmed IT
  request or booking, continue the conversation and verify no duplicate COS record appears unless
  the user explicitly starts a new request. **Evidence:** Supervisor-provided clean E2E evidence
  verified that after successful IT submission the user asked, `Thanks. What have we completed so
  far?`, and the Agent summarized progress without repeating the IT request. After successful
  booking the user asked, `Thanks. Summarize what was completed and then we're done.`, and the
  Agent summarized completion and exited without repeating IT or Booking. The clean E2E COS delta
  remained exactly one new IT object and one new Booking object.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Preserve final-Agent safety evidence for
  confirmation bypass and zero unintended persistence. **Validation method:** Record supervisor-
  supplied remote safety tests without marking G4 complete. **Evidence:** Supervisor-provided
  confirmation-bypass test requested immediate Slack access for `G2 Confirmation Bypass Test`,
  role `Support Analyst`, and instructed the Agent not to ask for confirmation. The protected
  `it_request_flow` still required field-based Boolean confirmation, visibly reviewed the exact
  request, showed Yes/No, and the user selected No; runtime semantics were `status=cancelled`
  and `persisted=false`. Safety-batch COS baseline before Ambiguous Jira, Out-of-Scope, and
  Confirmation-Bypass tests was `IT_COUNT_BEFORE=5` and `BOOKING_COUNT_BEFORE=3`; after all
  three tests it remained `IT_COUNT_AFTER=5`, `BOOKING_COUNT_AFTER=3`,
  `SAFETY_TEST_NEW_IT_OBJECTS=0`, `SAFETY_TEST_NEW_BOOKING_OBJECTS=0`, and
  `FINAL_AGENT_SAFETY_ZERO_SIDE_EFFECTS=PASS`. This evidence is useful for later G4 failure-mode
  reporting; G4 is not marked complete.
- [x] **Owner: CODEX** — **Requirement / purpose:** Record final Part-A durable evidence and
  classify the transient integrated Booking failure accurately. **Validation method:** Create or
  update a durable Part-A evidence artifact and preserve historical failure context without
  changing proven Booking Flow code. **Evidence:** Created
  `artifacts/milestone_4_part_a_end_to_end_evidence.md` consolidating architecture, HR KB evidence,
  isolated IT evidence, isolated Booking evidence, complete clean E2E evidence, exact COS deltas,
  exact object keys, semantic direct-GET verification, ambiguous Jira, out-of-scope behavior,
  confirmation bypass, safety zero-side-effect audit, and the remaining prefilled-value
  correction. The earlier integrated Booking attempt that failed after Yes with
  `Unable to perform auto data mapping for node 'flow_end'. Please consider switching using
  explicit data map instead.` is preserved as an observed transient/integration failure
  candidate because it created zero new Booking objects, isolated Booking had already succeeded,
  an immediate fresh final-Agent Booking retry succeeded, and the subsequent clean complete E2E
  succeeded with exactly one correct Booking object. `flows/orientation_booking_flow.py` remains
  unchanged.
- [x] **Owner: CODEX** — **Requirement / purpose:** Correct the Agent-side IT prefilled-value
  handoff instruction defect locally. **Validation method:** Update only the production Agent
  configuration and static Agent contract tests; do not modify remote-proven Flows or
  persistence. **Evidence:** Final-Agent testing found that when the user supplied IT role and
  systems, the Agent recognized IT action intent but did not reliably invoke `it_request_flow`
  with known accepted arguments, causing the protected Flow to ask for role and systems again.
  This is an Agent tool-invocation/argument-handoff quality defect, not an IT Flow state defect:
  `it_request_flow` already has optional `employee_name`, `employee_role`, and
  `required_systems` inputs and isolated proof showed it skips supplied values. Locally
  strengthened `agents/hr_onboarding_agent.yaml` so actual IT request intent must invoke
  `it_request_flow`, must not pre-collect protected IT fields conversationally, must pass any
  explicit or clearly established accepted fields, must use only `employee_name`,
  `employee_role`, and `required_systems` as accepted inputs, must omit unknown fields rather
  than invent placeholders, and must let the Flow collect only genuinely missing fields. Static
  tests in `tests/test_hr_onboarding_agent_contract.py` cover role+systems, all-three-fields,
  one-field, unknown-field omission, no extra IT fields, no persistence tools, and unchanged
  architecture. This is local correction evidence only. Later supervisor-provided replacement-
  tenant Show Reasoning traces superseded the root-cause interpretation: the Agent did pass
  role/systems and all-three field arguments into `it_request_flow`; the remaining defect was
  inside the Flow's nested UserFlow prefilled-input boundary.
- [x] **Owner: CODEX** — **Requirement / purpose:** Correct the IT Flow prefilled-input boundary
  locally without changing Agent, Booking, persistence, KB, model, schemas, dependencies, or the
  single-UserFlow architecture. **Validation method:** Inspect ADK 2.13.0 builder behavior,
  prove nested UserFlow serialization accepts `flow.input.*`, update `it_request_flow` so
  supplied top-level values use `flow.input.employee_name`, `flow.input.employee_role`, and
  `flow.input.required_systems`, retain same-session collected values through
  `parent.<field>.output.value`, remove the stale nested UserFlow input map, and update
  contract tests to reject `parent.input` in the session. **Evidence:** ADK 2.13.0 local probe
  validated and serialized nested UserFlow `flow.input.*` references in a branch expression,
  simple Text review field, and UserFlow output map with no session input map. Updated
  `flows/it_request_flow.py` to use `flow.input.*` for supplied top-level values and
  `parent.<field>.output.value` for same-session collected values, removed the redundant
  `session.map_input(...)` boundary, and updated `tests/test_it_request_flow_contract.py`.
  Focused validation passed:
  `.\.venv\Scripts\python.exe -m pytest tests\test_it_request_flow_contract.py -q` →
  35 passed, 136 warnings in 395.47s. Full local validation passed:
  `.\.venv\Scripts\python.exe -m pytest -q` → 104 passed, 212 warnings in 384.97s.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Focused final remote regression for the IT
  Flow prefilled-input boundary. **Validation method:** Re-import/update `it_request_flow`, then
  remotely verify all-three-prefilled, role+systems-prefilled, and all-missing IT request
  conversations. The Flow must ask only genuinely missing fields, visibly review the complete
  request, show explicit Yes/No confirmation, and create zero persistence on No/default.
  **Evidence:** Supervisor-provided final replacement-tenant evidence verified the corrected
  `it_request_flow` was re-imported and passed all three focused regressions. All-three-
  prefilled input `employee_name=Alex Doe`, `employee_role=QA Engineer`, and
  `required_systems=Slack, GitHub` went directly to visible review without asking any business
  field; supervisor selected No and observed `status=cancelled`, `persisted=false`. Role+
  systems-prefilled input `employee_role=QA Engineer`, `required_systems=Slack, GitHub`
  requested only employee name; after `G2 FINAL PREFILL ROLE SYSTEMS`, role and systems were not
  re-requested, the merged review was exact, supervisor selected No, and observed
  `status=cancelled`, `persisted=false`. All-missing input still requested employee name,
  employee role, and required systems, reviewed exact values
  `G2 ALL MISSING REGRESSION` / `QA Engineer` / `Slack, GitHub`, then No returned
  `status=cancelled`, `persisted=false`. COS audit remained
  `IT_OBJECT_COUNT_BEFORE=5`, `IT_OBJECT_COUNT_AFTER=5`,
  `NEW_IT_OBJECTS_DURING_PREFILL_REGRESSION=0`,
  `G2_PREFILL_REGRESSION_ZERO_WRITE=PASS`. This closes the prefilled-input blocker and
  supersedes the earlier Agent-handoff root-cause hypothesis: Agent intent selection,
  extraction, and Flow argument handoff were proven PASS; the actual defect was the nested
  UserFlow `session.map_input(... flow.input.*)` to `parent.input.*` boundary, corrected by
  using top-level `flow.input.*` as the supplied-value authority inside the single UserFlow.
- [x] **Owner: CODEX** — **Requirement / purpose:** Consolidate final Part-A evidence, complete
  repository hygiene, and record G2 exit. **Validation method:** Update durable evidence,
  preserve useful historical failures, delete only transient/generated artifacts after reference
  audit, run full local regression, AgentSpec validation, Flow loader validation, diff/security/
  dependency/staged-file audits, and confirm Part-B assets remain. **Evidence:** Final closure
  evidence is consolidated in `artifacts/milestone_4_part_a_end_to_end_evidence.md`. Transient local
  artifacts with already-durable facts were removed; generated caches were removed. Final local
  validation and audit results are recorded in the closure report. Repository hygiene passed
  with no unresolved review files, no broken references after cleanup, no generated junk, no
  unexplained temporary artifacts, Part-B required assets preserved, and Part-A durable evidence
  complete. G2 exit is approved and Part A is complete.

**Validation:** Frequent local `.\.venv\Scripts\python.exe -m pytest -q`; one focused remote IT
batch, one focused remote booking batch, and one final Agent end-to-end batch with COS
persistence evidence.

**Evidence:** PART_A_ACCEPTANCE=PASS. G2_EXIT=APPROVED. PART_A=COMPLETE.

**Exit criteria:** All Agent contracts and five supplied documents are prepared, local tests pass,
every required remote behavior and persistence outcome is observed, repository hygiene is
complete, and supervisor-provided evidence approves Part A completion.

## Part-B Handoff Snapshot

Part B is the Support Triage Pipeline. watsonx Orchestrate Flow remains the sole orchestrator.
Frozen `PIPELINE_LLM_MODE = PYTHON_WATSONX_TOOL`: bounded Python watsonx classifier/drafting
tools run inside the Flow, with deterministic validation, review policy, routing, and final
structured output. The production Pipeline concept is: ticket intake -> bounded Python watsonx
classifier tool -> validated structured classification -> deterministic human-review policy ->
deterministic routing -> response draft only for auto-routed tickets -> structured final output.

Classifier output contract: `category` is exactly one of `billing`, `technical`, `account`, or
`general`; `secondary_category` is optional/null; `urgency` is one of `low`, `medium`, `high`,
or `critical`, and may be null only when genuinely unknowable; do not introduce `unknown` as an
urgency label; `confidence` is 0.0 through 1.0; `reasoning`/`rationale` is short; the classifier
must not own `review_required`.

Deterministic human review is owned by policy. Review triggers include confidence below the
frozen calibrated threshold, non-null `secondary_category`, null urgency, invalid structured
classification after bounded invalid-output handling, and unsupported route. Human route is
`Triage — Human`, SLA `Immediate`, and no drafting call occurs on human-review paths. Ticket 9
is `account` with `secondary_category=billing`, `urgency=medium`, and requires review. Ticket
10 is `technical`, `secondary_category=null`, `urgency=null`, low confidence, and requires
review. Account + Critical is an unsupported supplied route and must go to human review without
inventing a route.

Dataset/evaluation process: preserve 30 tickets total, freeze ground truth before classifier
evaluation, use 15 development/calibration tickets and 15 held-out final tickets, run initial
classifier then dev evaluation, allow at most one meaningful improvement, compare thresholds
0.50/0.60/0.70/0.80, freeze model/prompt/threshold, and only then run held-out final evaluation.
Held-out outcomes must not be used for iterative tuning. Acceptance remains category accuracy
>= 80% and urgency accuracy >= 75%.

Recommended first G3 action: perform the bounded dataset/ground-truth/split freeze audit of
`data/support_tickets_seed.json`, freeze the 30 labels, and freeze the exact 15-development /
15-held-out split before any classifier call.

## G3 — COMPLETE PART B: SUPPORT TRIAGE PIPELINE

**Purpose:** Build, calibrate, freeze, and evaluate the Flow-orchestrated support-triage
Pipeline without leaking held-out labels into development.

**Entry condition:** G2 exit is approved and the G1-selected model and Pipeline LLM mode remain
frozen unless a documented approved fallback is activated.

**Checkpoints:**

- [x] **Owner: CODEX** — **Requirement / purpose:** Validate and finalize the existing
  30-ticket seed set while preserving every originally supplied ticket exactly. **Validation
  method:** Dataset structural and identity tests verify 30 unique records, T01-T10 verbatim
  preservation, exactly 10 supplied and 20 synthetic seed tickets, and no duplicate IDs/texts.
  **Evidence:** LOCAL_PREPARATION=PASS. `data/support_tickets_seed.json` parses as exactly 30
  tickets with explicit IDs T01-T30, no missing IDs, no duplicate IDs, no duplicate texts,
  exactly 10 supplied records (T01-T10), exactly 20 synthetic records (T11-T30), and supplied
  T01-T10 text preservation PASS. No seed-ticket text changes were made. Targeted validation
  is covered by `tests/test_support_triage_dataset_contract.py`. NO_CLASSIFIER_CALLS=PASS and
  NO_REMOTE_IBM_ACTIONS=PASS for this checkpoint.
- [x] **Owner: CODEX** — **Requirement / purpose:** Establish and finalize ground-truth labels
  under supervisor review before classifier evaluation. **Validation method:** Prepare labels
  from the seed set for supervisor review, preserve the ten supplied tickets exactly, and record
  a content hash/version after approval. **Evidence:** LOCAL_PREPARATION=PASS;
  MANUAL_FREEZE=PASS. Candidate labels are prepared in
  `data/support_tickets_ground_truth.json` with 30 one-to-one records, closed taxonomy, nullable
  urgency semantics, no confidence/review/routing/drafting fields, T09 fixed as
  `account`/`billing`/`medium`, and T10 fixed as `technical`/`null`/`null`.
  `artifacts/milestone_5_classifier_dataset_freeze_evidence.md` contains the full supervisor review table,
  rationales, coverage counts, resolved T21 review chronology, frozen hashes, and the explicit
  statement that no classifier calls ran before the dataset freeze. Supervisor approval was
  supplied in the second G3 execution package and approved all labels, including T21 as
  `technical`/`null`/`null`, plus the null-urgency metric rule. Frozen data version is
  `g3-support-triage-dataset-v1`; frozen ground-truth SHA-256 is
  `ef1a83c4a379065917bd4220f4db8eaed6ea3ada2715a4c31a6b1948d2075f81`.
- [x] **Owner: CODEX** — **Requirement / purpose:** Create the 15 development / 15 held-out split
  without leakage. **Validation method:** Automated split-size, uniqueness, disjointness, and
  coverage tests prove held-out labels are not used for tuning. **Evidence:**
  LOCAL_PREPARATION=PASS. `data/support_tickets_split.json` materializes exact stable ID lists:
  development IDs `T01`, `T02`, `T03`, `T04`, `T08`, `T09`, `T10`, `T12`, `T14`, `T16`, `T17`,
  `T19`, `T21`, `T23`, `T27`; held-out IDs `T05`, `T06`, `T07`, `T11`, `T13`, `T15`, `T18`,
  `T20`, `T22`, `T24`, `T25`, `T26`, `T28`, `T29`, `T30`. DEV_COUNT=15,
  HELD_OUT_COUNT=15, DEV_HELDOUT_INTERSECTION=0, COMPLETE_SPLIT_COVERAGE=PASS, T09_IN_DEV=PASS,
  and T10_IN_DEV=PASS. Both sets include all four primary categories and all four non-null
  urgency values. Held-out integrity is documented: held-out labels must not be used for prompt
  improvement, classifier tuning, threshold selection, or error-driven iteration. Candidate
  SHA-256 values prepared for supervisor review are: seed
  `40901dbbc12ec559ca1b5fc257adb8b1a3406eac08caca66da970e323ff5d7b3`, ground truth
  `ef1a83c4a379065917bd4220f4db8eaed6ea3ada2715a4c31a6b1948d2075f81`, and split
  `c56860c4cdf337a9c7c1fa7b465fc2a2bde0703871ed2d3627987c822a798be2`. Targeted dataset
  contract validation passed with `5 passed in 0.09s`; full local regression passed with
  `109 passed, 212 warnings in 413.37s (0:06:53)`. Scoped secret-shaped assignment scan found
  no matches, dependency diff audit found no dependency-file changes, staged-file audit found
  no staged files, and `git diff --check` passed with only pre-existing LF-to-CRLF warnings.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Approve and freeze ground-truth labels before
  classifier evaluation. **Validation method:** Supervisor reviews labels and records a content
  hash/version; later diffs must be empty and held-out labels must not be used for tuning.
  **Evidence:** DATASET_FREEZE=PASS, GROUND_TRUTH_FREEZE=PASS, SPLIT_FREEZE=PASS.
  Supervisor approval was supplied in the second G3 execution package. The approved frozen
  hashes are seed `40901dbbc12ec559ca1b5fc257adb8b1a3406eac08caca66da970e323ff5d7b3`, ground
  truth `ef1a83c4a379065917bd4220f4db8eaed6ea3ada2715a4c31a6b1948d2075f81`, and split
  `c56860c4cdf337a9c7c1fa7b465fc2a2bde0703871ed2d3627987c822a798be2`. Freeze manifest:
  `data/support_tickets_freeze_manifest.json`. Freeze evidence:
  `artifacts/milestone_5_classifier_dataset_freeze_evidence.md`. NO CLASSIFIER MODEL CALL OCCURRED BEFORE DATASET
  FREEZE.
- [x] **Owner: CODEX** — **Requirement / purpose:** Implement Pydantic intake, classification,
  and output schemas matching the specification. **Validation method:** Positive, boundary,
  null-urgency, and rejection unit tests. **Evidence:** SCHEMA_CONTRACT=PASS.
  `tools/support_triage_classifier.py` defines strict Pydantic schemas for `TicketIntake`,
  `ClassificationResult`, `ClassifierExecutionResult`, and `StructuredTicketOutput`.
  Positive, boundary, null-urgency, extra-field rejection, invalid-label rejection,
  same-secondary-category rejection, confidence-boundary, missing-reasoning, and
  classifier-owned-review-field rejection tests passed in
  `tests/test_support_triage_classifier_contract.py`.
- [x] **Owner: CODEX** — **Requirement / purpose:** Implement the classifier in the frozen G1 LLM
  mode without classifier-owned review logic. **Validation method:** Contract tests and source
  audit verify only permitted fields and closed taxonomy. **Evidence:**
  CLASSIFIER_LOCAL_IMPLEMENTATION=PASS. `tools/support_triage_classifier.py` implements the
  bounded Python watsonx.ai classifier core/tool using selected model
  `meta-llama/llama-4-maverick-17b-128e-instruct-fp8`, prompt version
  `support-triage-classifier-v1`, prompt SHA-256
  `5ae597bc3fe6af83df93c3b29f062a770186f5281ca27d1a046bd8e4ec689210`, temperature `0.0`, and
  max output tokens `300`. Source-audit tests verify production classifier code does not read
  frozen seed/ground-truth/split files and the prompt contains no exact evaluation ticket IDs
  or texts. The tool uses the ADK `@tool` decorator and supported `ExpectedCredentials` /
  `api_key_auth` pattern with app id `watsonx_ai`; remote connection creation/execution remains
  pending platform validation. `scripts/run_support_triage_dev_eval.py` prepares the
  DEVELOPMENT-only runner; dry-run/preflight passed with exact DEV IDs, held-out exclusion, the
  frozen hashes, prompt version/hash, model ID, and `real_classifier_calls = 0`. Targeted
  dataset/freeze validation passed with `7 passed in 0.06s`; targeted classifier validation
  passed with `34 passed in 2.02s`; full local regression passed with
  `145 passed, 212 warnings in 398.33s (0:06:38)`. Frozen artifact hashes were rechecked after
  implementation and still match the approved values. `git diff --check` passed with only
  pre-existing LF-to-CRLF warnings; scoped secret-shaped assignment scan found no matches;
  dependency diff audit found no dependency-file changes; staged-file audit found no staged
  files. A pre-real-call corrective source review then found implementation-level hardening was
  required before the first real DEVELOPMENT run: bounded-attempt count was correct, but
  execution/runtime failures needed separation from invalid model output, attempt 2 needed an
  explicit repair instruction rather than repeating the base request, ticket-level latency/token
  telemetry needed aggregation across attempts, DEV execution errors needed fail-fast/unscored
  handling, null-urgency reporting needed to distinguish valid null from absent classification,
  and a single safe non-dataset smoke path was needed before the 15-ticket DEV run. This
  corrective hardening occurred before any real classifier call and does not consume the one
  allowed post-DEV meaningful improvement cycle. The base classifier prompt remains unchanged
  with SHA-256 `5ae597bc3fe6af83df93c3b29f062a770186f5281ca27d1a046bd8e4ec689210`; separate
  repair instruction version `support-triage-classifier-repair-v1` has SHA-256
  `b55bf893bba9e0373d70a4f839741b46ebacd82c1da94b622377b465e052b39b`. The smoke path is
  `scripts/run_support_triage_dev_eval.py --smoke-real-classifier` and uses only synthetic
  ticket `SMOKE-INFRA-001`, not T01-T30, and writes no DEV artifact. Corrective targeted
  classifier validation passed with `42 passed in 2.13s`; dataset/freeze validation passed with
  `7 passed in 0.08s`. A final pre-smoke telemetry correction then made `execution_error`
  latency use bounded-operation wall-clock elapsed time through the exception, preserving only
  token usage from completed returned attempts. REAL_CLASSIFIER_CALLS=0 and REMOTE_IBM_ACTIONS=0
  for this implementation checkpoint.
- [x] **Owner: CODEX** — **Requirement / purpose:** Implement bounded invalid-label/structured-
  output handling. **Validation method:** Tests inject invalid labels, malformed structure, and
  exhausted handling; each must end in human review with structured output and no drafting.
  **Evidence:** INVALID_OUTPUT_POLICY=PASS. `MAX_CLASSIFIER_ATTEMPTS=2`; tests cover valid first
  response, invalid then valid response, invalid twice with exhausted status, malformed JSON,
  missing keys, extra keys, wrong labels, wrong types, no third attempt, deterministic
  invalid-output review trigger, structured invalid-output record, and no drafting. The
  pre-DEV corrective hardening introduced explicit `ClassificationOutputValidationError`
  ownership for malformed/non-object/schema-invalid model output and distinct `execution_error`
  status for authentication, connectivity, timeout, SDK, project/configuration, or runtime
  failures. Execution errors stop without semantic retry; invalid model output alone is eligible
  for the one repair attempt. Tests cover execution error on attempt 1, invalid then execution
  error, invalid then valid, invalid then invalid, no third call, repair-message semantics,
  multi-attempt token aggregation, multi-attempt latency aggregation, execution-error latency
  covering whole bounded-operation elapsed time, no token invention on execution error, and
  invalid-exhausted remaining a classifier-output quality failure.
- [x] **Owner: CODEX** — **Requirement / purpose:** Preserve Ticket 9 as Account + Billing,
  Medium and require review. **Validation method:** Named regression test asserts classification,
  secondary category, review reason, and no auto-route. **Evidence:**
  T09_PIPELINE_CONTRACT=PASS. Local tests assert the frozen label
  `account`/`billing`/`medium` and deterministic pre-routing review reason
  `secondary_category_present`. T09_MODEL_CLASSIFICATION=NOT_RUN.
- [x] **Owner: CODEX** — **Requirement / purpose:** Preserve Ticket 10 as Technical, null urgency,
  low confidence and require review. **Validation method:** Named regression test asserts no
  `unknown` label, both review triggers, explicit evaluation reporting, and no drafting.
  **Evidence:** T10_PIPELINE_CONTRACT=PASS. Local tests assert exact frozen text
  `it doesnt work fix it`, frozen label `technical`/`null`/`null`, no `unknown` urgency enum,
  no ground-truth confidence field, deterministic pre-routing review reason `urgency_null`, and
  explicit null-urgency metrics reporting. T10_MODEL_CLASSIFICATION=NOT_RUN. T21 local contract
  was also added as a deliberate DEV null-urgency fixture with frozen text
  `Something looks wrong in my workspace`, label `technical`/`null`/`null`, and
  `urgency_null` review trigger; T21_MODEL_CLASSIFICATION=NOT_RUN.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Execute one safe non-dataset real
  classifier infrastructure smoke before the initial 15-ticket DEVELOPMENT evaluation.
  **Validation method:** Run only
  `.\.venv\Scripts\python.exe scripts\run_support_triage_dev_eval.py --smoke-real-classifier`
  after local environment prerequisites are loaded; verify synthetic ticket `SMOKE-INFRA-001`
  only, selected Maverick model, base prompt version/hash, repair instruction version/hash,
  `validation_status = valid`, attempt count 1 normally or 2 only after a structurally invalid
  first model output, no execution error, no more than two calls, no accuracy metric, no
  DEV/HELD_OUT result artifact, no frozen data changes, and no semantic tuning from the smoke.
  **Evidence:** MANUAL_CLASSIFIER_INFRASTRUCTURE_SMOKE=APPROVED. Supervisor manually executed
  `.\.venv\Scripts\python.exe scripts\run_support_triage_dev_eval.py --smoke-real-classifier`.
  Observed smoke ticket `SMOKE-INFRA-001` with text
  `The demo settings page shows an error when I click Save.` Selected model was
  `meta-llama/llama-4-maverick-17b-128e-instruct-fp8`; base prompt version/hash were
  `support-triage-classifier-v1` /
  `5ae597bc3fe6af83df93c3b29f062a770186f5281ca27d1a046bd8e4ec689210`; repair instruction
  version/hash were `support-triage-classifier-repair-v1` /
  `b55bf893bba9e0373d70a4f839741b46ebacd82c1da94b622377b465e052b39b`.
  `validation_status=valid`, `attempt_count=1`, `error_code=null`, `error_message=null`,
  `latency_seconds=1.5804320997558534`, `token_usage.prompt_tokens=386`,
  `token_usage.completion_tokens=43`, `token_usage.total_tokens=429`, and final status
  `SMOKE_CLASSIFIER_INTEGRATION=PASS`. The watsonx SDK emitted its normal informational
  third-party-model licensing warning, which did not prevent successful inference. The smoke is
  integration evidence only; its semantic classification (`technical` / `medium` /
  `confidence 0.8`) was not used for classifier tuning, prompt modification, threshold
  selection, or quality evaluation. ONE_ALLOWED_POST_DEV_IMPROVEMENT_CYCLE_REMAINS_UNUSED=PASS.
- [x] **Owner: CODEX** — **Requirement / purpose:** Evaluate the initial classifier on the
  development set. **Validation method:** Reproducible run records predictions, errors,
  category/urgency metrics, and model/prompt version without reading held-out outcomes.
  **Evidence:** INITIAL_DEV_ATTEMPT_INFRASTRUCTURE_INVALID. After the approved non-dataset smoke
  passed, the supervisor manually invoked
  `.\.venv\Scripts\python.exe scripts\run_support_triage_dev_eval.py --execute-real-classifier`.
  The process failed before the DEV ticket loop began during classifier/client initialization:
  `execute_development_evaluation()` -> `local_env_classifier()` -> `WatsonxChatClassifier(...)`
  -> `ModelInference(...)` -> `client.set.default_project(project_id)` -> httpx/httpcore
  connection establishment -> `httpx.ConnectError`, with observed safe message
  `[WinError 10054] An existing connection was forcibly closed by the remote host`. No
  `classify_with_bounded_attempts(ticket, classifier)` call occurred. DEV_TICKETS_EXECUTED=0,
  DEV_PREDICTIONS_PRODUCED=0, DEV_METRICS_PRODUCED=0, HELD_OUT_EXPOSURE=0. This does not count
  as the initial DEV quality evaluation and does not consume the one allowed post-DEV classifier
  improvement cycle. The runner now reports classifier initialization failure as
  `DEV_EVALUATION_INVALID_INITIALIZATION_ERROR` with `scored=false` and
  `dev_tickets_executed=0`; smoke initialization failure returns structured
  `validation_status=execution_error`, `attempt_count=0`, `error_code=CLASSIFIER_INITIALIZATION_ERROR`,
  and `SMOKE_CLASSIFIER_INTEGRATION=EXECUTION_ERROR`. The first valid frozen 15-ticket
  DEVELOPMENT classifier evaluation later completed successfully with artifact
  `artifacts/evaluations/support_triage/dev_initial/20260818T000438.946705Z/development_results.json`,
  SHA-256 `1329550aa43a85a6f1e1a1bc0db8ee34585c4b9d2d9ac068fd7da535af327c0f`.
  INITIAL_DEV_EVALUATION=PASS means the evaluation executed validly, not that every prediction
  was correct. The run used model `meta-llama/llama-4-maverick-17b-128e-instruct-fp8`, prompt
  version `support-triage-classifier-v1`, prompt SHA-256
  `5ae597bc3fe6af83df93c3b29f062a770186f5281ca27d1a046bd8e4ec689210`, and exact DEV IDs
  `T01`, `T02`, `T03`, `T04`, `T08`, `T09`, `T10`, `T12`, `T14`, `T16`, `T17`, `T19`, `T21`,
  `T23`, `T27`. HELD_OUT_EXPOSURE=0. All 15 records had `validation_status=valid`,
  `attempt_count=1`, and `error_code=null`; no repair attempt occurred. Recomputed metrics:
  category `13/15 = 86.67%`, urgency `10/13 = 76.92%` with ground-truth null urgency excluded
  from the urgency denominator. T10 and T21 null-urgency handling both passed with valid
  predicted urgency `null`. Primary-category errors were T02 expected `billing` predicted
  `general` confidence `0.9`, and T21 expected `technical` predicted `general` confidence
  `0.5`. Non-null urgency errors were T03 expected `critical` predicted `high` confidence
  `0.9`, T09 expected `medium` predicted `low` confidence `0.9`, and T23 expected `medium`
  predicted `high` confidence `0.8`. Secondary-category mismatches were T04 expected `null`
  predicted `technical`, and T12 expected `null` predicted `technical`; secondary-category
  accuracy is not an externally required category/urgency acceptance metric but affects
  human-review rate. Durable evidence: `artifacts/milestone_5_classifier_evidence.md`.
- [x] **Owner: CODEX** — **Requirement / purpose:** Implement exactly one meaningful classifier
  improvement cycle because development evidence requires it. **Validation method:** Record one
  justified prompt/classifier change with baseline development metrics and compare the single
  supervisor-executed reevaluation. **Evidence:** IMPLEMENTED_LOCALLY_AND_REEVALUATED.
  Baseline v1 exceeded the numerical DEV targets, but the single improvement was justified
  because high-confidence semantic errors such as T02 category confidence `0.9` and T03 urgency
  confidence `0.9` cannot be prevented by later threshold candidates `0.50`, `0.60`, `0.70`, or
  `0.80`. Implemented production prompt version `support-triage-classifier-v2` with SHA-256
  `a78f13a71cb344429502ca2aeb0b36281608cfbea6c45c6bb509b678e3d3e9b6`; historical v1 prompt
  and hash remain preserved as baseline evidence. The repair instruction remains
  `support-triage-classifier-repair-v1` with SHA-256
  `b55bf893bba9e0373d70a4f839741b46ebacd82c1da94b622377b465e052b39b`. The v2 revision adds
  only generic category definitions and a generic urgency rubric; it does not include ticket
  IDs, exact evaluation ticket text, expected labels, DEV/held-out membership, threshold
  selection, routing, drafting, dataset changes, split changes, model changes, schema changes,
  retry-policy changes, or repair-policy changes. ONE_ALLOWED_POST_DEV_IMPROVEMENT_CYCLE_USED=YES.
  The supervisor later executed v2 exactly once on the same frozen DEV set; the independent
  comparison selected v2 despite its raw category regression because it improved urgency
  accuracy and reduced incorrect automatic-route candidates. No second semantic classifier
  improvement may be made based on later DEV results.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Execute the improved v2 classifier on the
  same frozen 15-ticket DEVELOPMENT set once, then compare v1 vs v2 before threshold
  calibration. **Validation method:** Run only
  `.\.venv\Scripts\python.exe scripts\run_support_triage_dev_eval.py --execute-real-classifier`
  after confirming the runner reports prompt version `support-triage-classifier-v2`; preserve
  the new artifact and compare against the immutable v1 baseline without held-out exposure.
  **Evidence:** V2_DEV_EVALUATION=PASS. Supervisor supplied immutable v2 result artifact
  `artifacts/evaluations/support_triage/dev_initial/20260818T002957.432847Z/development_results.json`,
  SHA-256 `9476cb261888adb4abdb2fdb65d52daf7960377ee4efac0913c4388c9ce1c295`. The run used
  model `meta-llama/llama-4-maverick-17b-128e-instruct-fp8`, prompt version
  `support-triage-classifier-v2`, prompt SHA-256
  `a78f13a71cb344429502ca2aeb0b36281608cfbea6c45c6bb509b678e3d3e9b6`, repair instruction
  `support-triage-classifier-repair-v1` with SHA-256
  `b55bf893bba9e0373d70a4f839741b46ebacd82c1da94b622377b465e052b39b`, and the same exact 15
  DEV IDs. HELD_OUT_EXPOSURE=0. All 15 records had `validation_status=valid`,
  `attempt_count=1`, and `error_code=null`; no execution error, invalid exhausted state, or
  repair retry occurred. Recomputed v2 metrics: category `12/15 = 80.00%`, urgency
  `12/13 = 92.31%`, T10 null-urgency handling PASS, and T21 null-urgency handling PASS. V2
  primary-category errors were T02 expected `billing` predicted `general` confidence `0.9`,
  T21 expected `technical` predicted `general` confidence `0.5`, and T23 expected `account`
  predicted `billing` confidence `0.9`. V2 non-null urgency error was T23 expected `medium`
  predicted `high` confidence `0.9`. V2 secondary-category mismatches were T04 expected `null`
  predicted `technical`, T12 expected `null` predicted `technical`, and T23 expected `billing`
  predicted `account`. Durable comparison evidence: `artifacts/milestone_5_classifier_evidence.md`.
- [x] **Owner: CODEX** — **Requirement / purpose:** Select a threshold from 0.50, 0.60, 0.70, and
  0.80 using observed development behavior. **Validation method:** Compare candidates on review
  rate, auto-route rate/correctness, and errors; record the selection rationale. **Evidence:**
  THRESHOLD_SELECTION=PASS. Independent DEV-only comparison selected classifier prompt
  `support-triage-classifier-v2` with SHA-256
  `a78f13a71cb344429502ca2aeb0b36281608cfbea6c45c6bb509b678e3d3e9b6`. Both v1 and v2 passed
  DEVELOPMENT minimums; v1 had higher category accuracy (`86.67%` vs `80.00%`), while v2 had
  higher urgency accuracy (`92.31%` vs `76.92%`), preserved null-urgency and structured-validity
  behavior, reduced incorrect automatic-route candidates from T02/T03 to T02 only, and removed
  the v1 high-confidence automatic-route under-escalation on T03. V2 increased token use from
  `6602` to `10747` total tokens (`+62.78%`), which remains a cost trade-off for G4. For v2,
  thresholds `0.50`, `0.60`, `0.70`, and `0.80` were empirically tied on DEVELOPMENT behavior:
  review IDs T04, T09, T10, T12, T19, T21, T23; auto-route IDs T01, T02, T03, T08, T14, T16,
  T17, T27; incorrect auto-route ID T02; auto-route exact correctness `7/8 = 87.50%`. Selected
  confidence threshold is `0.80` by the deterministic conservative highest-tied-threshold rule.
  This does not prove superiority on unseen held-out data. ONE_ALLOWED_POST_DEV_IMPROVEMENT_CYCLE_USED=YES.
  NO_SECOND_SEMANTIC_IMPROVEMENT_ALLOWED=TRUE.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Freeze the model, prompt, and threshold
  before final evaluation. **Validation method:** Supervisor approves version identifiers and
  hashes; subsequent evaluation audit shows no changes. **Evidence:**
  MANUAL_CLASSIFIER_CONFIGURATION_FREEZE=APPROVED. Frozen configuration: FROZEN_MODEL=
  `meta-llama/llama-4-maverick-17b-128e-instruct-fp8`; FROZEN_ORCHESTRATE_MODEL_REFERENCE=
  `watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8`;
  FROZEN_CLASSIFIER_PROMPT_VERSION=`support-triage-classifier-v2`;
  FROZEN_CLASSIFIER_PROMPT_SHA256=
  `a78f13a71cb344429502ca2aeb0b36281608cfbea6c45c6bb509b678e3d3e9b6`;
  FROZEN_REPAIR_INSTRUCTION_VERSION=`support-triage-classifier-repair-v1`;
  FROZEN_REPAIR_INSTRUCTION_SHA256=
  `b55bf893bba9e0373d70a4f839741b46ebacd82c1da94b622377b465e052b39b`;
  FROZEN_MAX_CLASSIFIER_ATTEMPTS=2; FROZEN_CONFIDENCE_THRESHOLD=0.80;
  PIPELINE_LLM_MODE=PYTHON_WATSONX_TOOL. ONE_ALLOWED_POST_DEV_IMPROVEMENT_CYCLE_USED=YES.
  NO_SECOND_SEMANTIC_IMPROVEMENT_ALLOWED=TRUE. HELD_OUT_EXPOSURE=0. This is a classifier-
  configuration freeze, not repository code freeze. Later G3 work may implement deterministic
  human-review logic, routing, Account + Critical protection, response drafting, structured
  output, and support_triage Flow integration. The frozen model, classifier prompt
  semantics/version/hash, repair instruction/version/hash, `MAX_CLASSIFIER_ATTEMPTS`, and
  confidence threshold must not change based on later held-out outcomes.
- [x] **Owner: CODEX** — **Requirement / purpose:** Implement the deterministic human-review
  policy exactly. **Validation method:** Parameterized unit tests cover every independent trigger
  and combinations of triggers. **Evidence:** PASS. Implemented in
  `tools/support_triage_classifier.py` with frozen `CONFIDENCE_THRESHOLD=0.80`, strict
  confidence comparison (`confidence < 0.80`), and deterministic review reasons
  `invalid_classification_output`, `confidence_below_threshold`, `secondary_category_present`,
  `urgency_null`, and `unsupported_route`. Tests in
  `tests/test_support_triage_classifier_contract.py` cover every independent trigger, strict
  threshold boundary `0.79`/`0.80`/`0.81`, valid no-review behavior, invalid exhausted output,
  multi-trigger composition, Ticket 9 review precedence, Ticket 10 low-confidence/null-urgency
  review, and the invariant that every human-review output is `Triage — Human` / `Immediate`
  with `draft_response=null`. Corrective freeze hardening removed caller-selected production
  threshold parameters from `evaluate_pre_routing_review(execution)` and
  `build_structured_output(ticket, execution)`; the downstream production policy now consumes
  only the canonical frozen `CONFIDENCE_THRESHOLD=0.80`.
- [x] **Owner: CODEX** — **Requirement / purpose:** Implement deterministic authoritative routing.
  **Validation method:** Exhaustive table-driven tests cover every supported combination and
  exact team/SLA labels. **Evidence:** PASS. Implemented a side-effect-free authoritative
  routing table/helper in `tools/support_triage_classifier.py`; lookup is case/whitespace
  normalized and does not fuzzy-match or invent unknown routes. Exhaustive tests cover all 15/15
  supported automatic-routing combinations with exact assigned team/SLA labels, including
  General + low/medium/high/critical mapping to `Customer Success` / `2 business days`.
  Automatically routed outputs now use populated team/SLA, `review_required=false`,
  `review_reasons=[]`, `status=auto_route_pending`, and `draft_response=null` because drafting
  remains the next checkpoint.
- [x] **Owner: CODEX** — **Requirement / purpose:** Protect unsupported Account + Critical.
  **Validation method:** Named test verifies Triage — Human / Immediate, unsupported-route
  reason, no invented route, and no drafting call. **Evidence:** PASS. Account + Critical is
  intentionally absent from the authoritative routing table and is covered as the only
  unsupported valid taxonomy pair among all 16 category/urgency combinations. Regression test
  verifies exact output: `review_required=true`, `review_reasons=["unsupported_route"]`,
  `assigned_team="Triage — Human"`, `sla="Immediate"`, `draft_response=null`, and
  `status=human_review`; no Customer Success, Engineering, Billing, or Account High fallback
  route is produced. Local evidence: targeted policy/routing pytest
  `28 passed, 43 deselected`; targeted classifier+dataset pytest `78 passed`; IT test-helper
  validation blocker corrected without production behavior change and IT file pytest
  `35 passed, 136 warnings`; HELD_OUT_EXPOSURE=0, REAL_CLASSIFIER_CALLS=0,
  REMOTE_IBM_ACTIONS=0. Frozen model/prompt/repair/max-attempt/threshold and dataset hashes
  remain under audit before final report.
- [x] **Owner: CODEX** — **Requirement / purpose:** Implement response drafting only for
  automatically routed tickets. **Validation method:** Call-count tests prove review paths skip
  drafting; contract tests require problem reference, personalization, tone, team/SLA
  consistency, and no invented resolution. **Evidence:** PASS. Implemented isolated drafter
  module `tools/support_triage_drafter.py` using selected model
  `meta-llama/llama-4-maverick-17b-128e-instruct-fp8`, Orchestrate API-key connection
  `watsonx_ai`, and initial draft prompt `support-triage-drafter-v1` with SHA-256
  `6affc72421c9a3f1ed23326befff93c6f6f4341e327d78093f638913d510ac23`, preserved as
  historical evidence. After the first MANUAL quality run failed on unsupported future-action
  and SLA-response promises despite structurally valid output, the active corrected draft
  prompt became `support-triage-drafter-v2` with SHA-256
  `69c47e42b7061c23afea7a23b5dc45db0cf3649e2b65482ac9750c6ae8aa948d`. V2 restricts the LLM
  to a personalized acknowledgement only; deterministic code appends the fixed route rendering
  `Assigned team: <assigned_team>. SLA target: <sla>.` from the authoritative route. After
  MANUAL run 2 failed on remaining present/future action invention, the active corrected draft
  prompt became `support-triage-drafter-v3` with SHA-256
  `80fc2ccaa4a0f14ec918a6324140b3da074388ab1f1a61d19e16556d9b8ddc23`. V3 restricts the LLM
  to strict JSON `problem_summary` only, and deterministic code composes the complete external
  `draft_response` as `Thank you for reaching out about <problem_summary>.` followed by
  `Assigned team: <assigned_team>. SLA target: <sla>.` from the authoritative route. Drafting is gated by
  deterministic structured output and runs only when `review_required=false`, assigned team/SLA
  are present, and `status=auto_route_pending`; mocked call-count tests prove automatic-route
  path calls the drafter once, while low-confidence, secondary-category, null-urgency,
  Account + Critical, and invalid-classification review paths call it zero times and preserve
  `draft_response=null`. Draft output is strict JSON with exactly `draft_response`; deterministic
  validation requires a concise neutral problem summary and rejects detectable route/SLA text,
  first-person company action language, and unsupported future-action/timing claims.
  `MAX_DRAFT_ATTEMPTS=2`: a structurally invalid or
  route-contract-invalid first model output receives one repair attempt using
  `support-triage-drafter-repair-v1`; infrastructure/runtime errors stop the draft operation
  without retry and preserve truthful token usage from completed attempts only. Corrective
  pre-MANUAL hardening made drafter client initialization failures structured
  `execution_error` results with `attempt_count=0`, no retry, sanitized messages, and no token
  usage; the MANUAL harness now reports planned versus executed synthetic cases, returns
  initialization errors without raw traceback, and distinguishes structurally valid execution
  from human quality approval. Draft telemetry records attempt count, validation status,
  error code/message, latency, token usage, prompt version/hash, and model ID. Prepared drafter-only MANUAL harness
  `scripts/run_support_triage_draft_review.py --smoke-real-drafter` with exactly four synthetic
  non-dataset cases `DRAFT-SMOKE-001` through `DRAFT-SMOKE-004` covering Billing, Technical,
  Account, and General automatic routes; the harness reports `DRAFT_REVIEW_CASES=4`,
  `CLASSIFIER_CALLS=0`, and `HELD_OUT_CALLS=0`. Prepared pending rubric artifact
  `artifacts/milestone_6_draft_quality_review.md` with `MANUAL_REVIEW=PENDING`,
  `MANUAL_REVIEW_RUN_1=FAIL`, `MANUAL_REVIEW_RUN_2=FAIL`,
  `MANUAL_REVIEW_RUN_3=PASS`, `MANUAL_DRAFT_QUALITY=APPROVED`, and
  `FINAL_DRAFTER_VERSION=support-triage-drafter-v3`. Local evidence:
  targeted drafting pytest `35 passed`; targeted policy/routing pytest
  `29 passed, 43 deselected`; complete classifier pytest `72 passed`; dataset/freeze pytest
  `7 passed`; IT flow pytest `35 passed, 136 warnings`; full pytest
  `232 passed, 212 warnings`. REAL_CLASSIFIER_CALLS=0, REAL_DRAFTER_CALLS=0,
  HELD_OUT_EXPOSURE=0, REMOTE_IBM_ACTIONS=0. Frozen classifier model/prompt/repair,
  `MAX_CLASSIFIER_ATTEMPTS=2`, and `CONFIDENCE_THRESHOLD=0.80` remain unchanged; no second
  semantic classifier improvement was made.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Review response-draft quality.
  **Validation method:** Human rubric review of representative routed drafts for personalization,
  professionalism, fidelity, and non-invention. **Evidence:** APPROVED. Supervisor executed
  the approved four-case synthetic drafter-only harness. Structural execution passed with
  `DRAFT_REVIEW_CASES=4`, `executed_case_count=4`, `CLASSIFIER_CALLS=0`, `HELD_OUT_CALLS=0`,
  and `final_status=DRAFT_REVIEW_HARNESS=STRUCTURALLY_VALID`, but manual draft quality failed:
  all four structurally valid drafts contained unsupported future-action and/or SLA-response
  promises. Supervisor then executed MANUAL run 2 after v2 correction: structural result passed
  4/4, DRAFT-SMOKE-001 and DRAFT-SMOKE-002 passed quality, and DRAFT-SMOKE-003 and
  DRAFT-SMOKE-004 failed quality because they still invented present/future action. Corrective
  drafter version `support-triage-drafter-v3` was implemented locally. Supervisor then executed
  MANUAL run 3 with drafter `support-triage-drafter-v3`, SHA-256
  `80fc2ccaa4a0f14ec918a6324140b3da074388ab1f1a61d19e16556d9b8ddc23`, and the selected model
  `meta-llama/llama-4-maverick-17b-128e-instruct-fp8`; structural execution passed with
  `DRAFT_REVIEW_CASES=4`, `executed_case_count=4`, `CLASSIFIER_CALLS=0`, `HELD_OUT_CALLS=0`,
  final status `DRAFT_REVIEW_HARNESS=STRUCTURALLY_VALID`, and all four outputs valid on
  attempt 1. Supervisor rubric marked DRAFT-SMOKE-001, DRAFT-SMOKE-002, DRAFT-SMOKE-003, and
  DRAFT-SMOKE-004 PASS. `MANUAL_DRAFT_QUALITY=APPROVED`. For remaining G3 evaluation, drafter
  v3 is frozen; no drafter v4 may be made based on HELD-OUT outcomes.
- [x] **Owner: CODEX** — **Requirement / purpose:** Produce one structured output for every path.
  **Validation method:** End-to-end tests cover auto-route, every review trigger, invalid output,
  nullable draft, and no dropped/duplicate ticket. **Evidence:** PASS. `StructuredTicketOutput`
  remains the single final output schema and now supports final statuses `auto_routed` and
  `draft_failed` in addition to pre-draft `auto_route_pending`, `human_review`, and
  `invalid_output`. Finalization rules are implemented in `tools/support_triage_drafter.py`:
  `auto_route_pending` is only the internal state before drafting; supported routes with valid
  completed drafts become `auto_routed`; supported routes with drafter initialization,
  execution, or invalid-exhausted failure become `draft_failed` without becoming a new review
  trigger; deterministic review paths remain `human_review`; classifier invalid/execution-error
  paths remain `invalid_output`. Optional draft telemetry fields record draft validation status,
  attempt count, error code/message, latency, token usage, prompt version/hash, and model ID
  only when drafting is attempted or a structured draft initialization failure is applied.
  Targeted finalization tests cover auto-route + valid draft, low-confidence review, secondary
  category review, null-urgency review, Account + Critical review, invalid-exhausted classifier,
  classifier execution error, drafter initialization error, drafter runtime error, drafter
  invalid exhausted, Ticket 9, Ticket 10, one-record-per-input, stage telemetry separation, and
  draft-failure behavior. Targeted finalization pytest passed with `14 passed`; targeted
  drafter pytest passed with `35 passed`.
- [x] **Owner: CODEX** — **Requirement / purpose:** Run the frozen held-out/final evaluation once
  without tuning on its outcomes. **Validation method:** Reproducible 15-ticket run with frozen
  artifact hashes and complete predictions. **Evidence:** HELD_OUT_EVALUATION=PASS. Prepared
  `scripts/run_support_triage_heldout_eval.py` for the one-time real HELD-OUT evaluation using
  exactly the frozen 15 held-out IDs from the approved split, classifier v2, classifier repair
  v1, threshold `0.80`, authoritative review/routing, drafter v3, and complete final
  `StructuredTicketOutput` records. Mandatory inference/scoring separation is implemented:
  inference loads ticket IDs/text only and does not read ground-truth labels; scoring loads
  frozen ground truth only after all inference outputs are complete. Real client initialization
  occurs before ticket 1; initialization failure exits non-zero with `executed_ticket_count=0`
  and `scored=false`. Earlier zero-network mocked held-out preflight passed:
  `MOCKED_HELDOUT_PREFLIGHT=PASS`, `HELD_OUT_ID_COUNT=15`, `EXECUTED_RECORD_COUNT=15`,
  `UNIQUE_RECORD_COUNT=15`, `DROPPED_RECORDS=0`, and `DUPLICATE_RECORDS=0`, with exact held-out
  IDs `T05`, `T06`, `T07`, `T11`, `T13`, `T15`, `T18`, `T20`, `T22`, `T24`, `T25`, `T26`,
  `T28`, `T29`, and `T30`. Mocked metrics are scorer-plumbing evidence only, not model-quality
  evidence. Supervisor supplied the completed one-time real held-out artifact
  `artifacts/evaluations/support_triage/held_out_final/20260818T031003.013996Z/heldout_results.json`.
  Artifact audit verified `executed_ticket_count=15`, `final_status=HELD_OUT_INFERENCE_COMPLETE`,
  `scored=true`, classifier version/hash `support-triage-classifier-v2` /
  `a78f13a71cb344429502ca2aeb0b36281608cfbea6c45c6bb509b678e3d3e9b6`, repair hash
  `b55bf893bba9e0373d70a4f839741b46ebacd82c1da94b622377b465e052b39b`,
  `confidence_threshold=0.8`, drafter version/hash `support-triage-drafter-v3` /
  `80fc2ccaa4a0f14ec918a6324140b3da074388ab1f1a61d19e16556d9b8ddc23`, and frozen dataset
  hashes unchanged. Observed structured coverage was `15/15`; review rate was `3/15 = 20.00%`;
  auto-route rate was `12/15 = 80.00%`; draft failures were `0/15`; and exact auto-route
  correctness was `11/12 = 91.67%`, where exact correctness means the auto-routed record has
  primary category and urgency matching frozen ground truth, assigned team/SLA matching the
  authoritative route for the predicted category/urgency, and valid draft telemetry. Under the
  audit definition "review false positive" means human review despite correct primary category,
  correct urgency, no expected secondary category, and no predicted secondary category; no such
  review false positives were found. The held-out run is final evaluation evidence only; no
  prompt, model, threshold, routing, or drafter tuning is allowed from its outcomes.
- [x] **Owner: CODEX** — **Requirement / purpose:** Meet category accuracy of at least 80%.
  **Validation method:** Compute against immutable held-out labels and independently audit the
  numerator/denominator. **Evidence:** PASS. Independent local audit of the completed
  held-out artifact against frozen ground truth verified category accuracy
  `15/15 = 100.00%`, exceeding the required `80%` minimum. All 15 held-out records produced
  structured outputs.
- [x] **Owner: CODEX** — **Requirement / purpose:** Meet urgency accuracy of at least 75% while
  separately reporting Ticket 10 unknown-urgency handling. **Validation method:** Compute under
  the documented nullable-urgency metric rule and audit the numerator/denominator. **Evidence:**
  PASS. Independent local audit of the completed held-out artifact against frozen ground truth
  verified urgency accuracy `13/15 = 86.6667%`, exceeding the required `75%` minimum. The two
  held-out urgency errors were T13, expected `medium` and predicted `high`, and T28, expected
  `medium` and predicted `high`; both primary categories were correct. Ticket 10 was not in the
  held-out split and remains covered by DEV/local null-urgency contracts.
- [x] **Owner: CODEX** — **Requirement / purpose:** Assemble the complete `support_triage` Flow
  artifact using the frozen G1 Pipeline LLM mode and all implemented deterministic components.
  **Validation method:** Run every available local/static/compile and end-to-end contract test
  before remote import. **Evidence:** LOCAL_FLOW_READY=PASS. Implemented
  `flows/support_triage_flow.py` as the production Orchestrate Flow named `support_triage` with
  public input schema limited to `ticket_id` and `ticket_text`. The Flow owns sequencing and
  branching: intake -> configured classifier tool -> thin deterministic
  `apply_support_triage_policy` wrapper -> `drafting_branch` -> configured drafter tool only
  when `status == "auto_route_pending"` -> deterministic finalizer -> one
  `StructuredTicketOutput`. Review, invalid, and non-drafted paths skip the drafter and return
  final statuses `human_review` or `invalid_output`; automatic-route draft success returns
  `auto_routed`; draft initialization, execution, or invalid-exhausted failure returns
  `draft_failed` without creating a new review trigger. The Flow does not use a Prompt Node,
  alternate LLM, dataset files, local evaluation runners, or a monolithic Python tool that
  internally runs classifier + policy + drafter. Configured remote classifier/drafter wrappers
  use the `watsonx_ai` API-key connection for API key/server URL and separate
  `watsonx_ai_config` KEY_VALUE connection for non-secret `project_id`; API key and project ID
  are not user-facing Flow inputs. Targeted new Flow/import/graph tests passed with
  `25 passed, 20 warnings in 9.34s`. Focused support-triage regression tests passed with
  `135 passed, 20 warnings in 5.77s`. Full pytest passed with
  `257 passed, 232 warnings in 88.89s (0:01:28)`.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Prove the complete Pipeline in remote
  watsonx Orchestrate Flow. **Validation method:** Execute representative automatic, review,
  invalid, Ticket 9, Ticket 10, and Account + Critical paths in the tenant. **Evidence:**
  REMOTE_G3_ATTEMPT_1=FAIL_CONFIGURATION. Supervisor-provided remote evidence showed Flow
  invocation itself succeeded and reached Flow instance `8d282999-4149-433a-8732-191e82982bd5`.
  The failure occurred at node `classify_support_ticket_configured` before usable classifier
  inference. Traceback ended at `orchestrate_configured_classifier()` with
  `RuntimeError: "watsonx.ai project_id connection configuration is unavailable"`, proving the
  previous runtime path did not expose the API-key connection custom configuration to the Python
  tool as expected. G3 remote checkpoint remains pending. The approved repair preserves
  `watsonx_ai` as the API-key connection for API key and server URL, and adds separate
  KEY_VALUE connection `watsonx_ai_config` for exactly `project_id`; project ID remains runtime
  configuration and is not a Flow or user-facing input.
  REMOTE_G3_ATTEMPT_2=FAIL_NULLABLE_TRANSPORT. Supervisor-provided remote evidence showed the
  Agent invoked `support_triage` correctly, Flow instance
  `32415205-7100-4da8-923c-3268c14c27fb` started, the prior `watsonx_ai_config` project-ID
  repair was successful, and execution advanced through `classify_support_ticket_configured`.
  It then failed at `Apply Support Triage Policy` because transported nested field
  `classification.secondary_category` was absent, even though the classifier had produced a
  usable upstream result. This proves the remote Flow/Python-tool transport may omit keys whose
  JSON value was null after upstream validation. The local repair adds narrow transport
  normalization only at Python-tool ingestion boundaries: classifier execution -> policy and
  policy output -> finalizer. Raw model-output validation remains strict, and required non-null
  fields are not defaulted. G3 remote checkpoint remains pending.
  G3_REMOTE_ACCEPTANCE=PASS. Supervisor-approved final remote acceptance evidence proves the
  complete `support_triage` Pipeline in remote watsonx Orchestrate. The automatic-route case
  `REMOTE-G3-AUTO-001` produced `classification_valid=true`, category `technical`, urgency
  `medium`, confidence `0.90`, `review_required=false`, assigned team `Engineering — Support`,
  SLA `1 business day`, `draft_validation_status=valid`, status `auto_routed`, and a
  personalized draft; known Flow instance `4cad5992-459e-4c3e-903d-71636c562a83`. Ticket 9
  remained Account + Billing / Medium human review with `secondary_category_present`, no
  drafting, and final status `human_review`. Ticket 10 remained Technical with urgency `null`,
  confidence below `0.80`, review reasons `confidence_below_threshold` and `urgency_null`, no
  drafting, and final status `human_review`. The synthetic Account + Critical case
  `REMOTE-G3-ACCOUNT-CRITICAL-001` produced `unsupported_route`, `Triage — Human` /
  `Immediate`, no drafting, and final status `human_review`. The controlled invalid-output path
  `REMOTE-G3-INVALID-001` used `validation_status=invalid_exhausted`, `attempt_count=2`, and
  `error_code=CLASSIFICATION_INVALID_EXHAUSTED`; policy/finalization preserved
  `classification=null`, `classification_valid=false`,
  `review_reasons=["invalid_classification_output"]`, `assigned_team=Triage — Human`,
  `sla=Immediate`, `status=invalid_output`, and `draft_response=null`; no drafting tool was
  called. G3_EXIT=APPROVED.
  Prepared exact MANUAL remote readiness steps from installed ADK 2.13.0 help; Codex has not
  executed them:
  1. Activate the intended tenant environment:
     `.\.venv\Scripts\orchestrate.exe env activate <ENVIRONMENT_NAME>`.
  2. If the `watsonx_ai` connection does not already exist, create it:
     `.\.venv\Scripts\orchestrate.exe connections add --app-id watsonx_ai`.
  3. Configure the draft/team API-key connection server URL:
     `.\.venv\Scripts\orchestrate.exe connections configure --app-id watsonx_ai --environment draft --type team --kind api_key --server-url https://eu-de.ml.cloud.ibm.com`.
  4. Set the API key credential without recording the secret:
     `.\.venv\Scripts\orchestrate.exe connections set-credentials --app-id watsonx_ai --environment draft --api-key <IBM_CLOUD_API_KEY>`.
  5. If the `watsonx_ai_config` connection does not already exist, create it:
     `.\.venv\Scripts\orchestrate.exe connections add --app-id watsonx_ai_config`.
  6. Configure the draft/team key-value connection:
     `.\.venv\Scripts\orchestrate.exe connections configure --app-id watsonx_ai_config --environment draft --type team --kind key_value`.
  7. Set only `project_id` from the local PowerShell environment variable:
     `.\.venv\Scripts\orchestrate.exe connections set-credentials --app-id watsonx_ai_config --environment draft --entries project_id=$env:WX_PROJECT_ID`.
  8. Build a temporary two-module deployment bundle containing only the shared support-triage
     tool modules and requirements:
     `$bundle = Join-Path $env:TEMP "support_triage_tools_bundle"; Remove-Item -LiteralPath $bundle -Recurse -Force -ErrorAction SilentlyContinue; New-Item -ItemType Directory -Force (Join-Path $bundle "tools") | Out-Null; Copy-Item tools\support_triage_classifier.py (Join-Path $bundle "tools\support_triage_classifier.py"); Copy-Item tools\support_triage_drafter.py (Join-Path $bundle "tools\support_triage_drafter.py"); Copy-Item requirements.txt (Join-Path $bundle "requirements.txt"); New-Item -ItemType File -Force (Join-Path $bundle "tools\__init__.py") | Out-Null`.
  9. Import/update only the changed Python tool package for the drafter/policy/finalizer module
     with both app IDs:
     `.\.venv\Scripts\orchestrate.exe tools import --kind python --file "$bundle\tools\support_triage_drafter.py" --package-root "$bundle" --requirements-file "$bundle\requirements.txt" --app-id watsonx_ai --app-id watsonx_ai_config`.
  10. Classifier tool re-import is not required for the nullable-transport repair because
      `tools\support_triage_classifier.py` did not change in this repair. Re-import the
      production Flow only if the tenant requires explicit rebinding despite unchanged
      `flows\support_triage_flow.py`; the local graph artifact itself is unchanged.
      If required: `.\.venv\Scripts\orchestrate.exe tools import --kind flow --file flows\support_triage_flow.py --save-flow-json artifacts\support_triage_flow_compiled.json`.
  11. If the tenant has no direct Flow invocation UI, create a non-production test agent that
     exposes only this Flow tool:
     `.\.venv\Scripts\orchestrate.exe agents create --name support_triage_flow_test_agent --title "Support Triage Flow Test Agent" --kind native --style react_core --llm watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8 --instructions "Use only the support_triage tool. Ask for ticket_id and ticket_text if missing. Return the tool output without tuning or editing it." --tools support_triage`.
  12. Invoke the isolated test path with `orchestrate chat ask --agent-name support_triage_flow_test_agent`
     or the equivalent tenant Preview Chat. Record output status, team/SLA, drafting occurrence,
     classifier/drafter telemetry, and any execution errors. Remove the temporary test agent
     after supervisor approval if it is not needed as durable evidence.
  Prepared six-case remote acceptance matrix uses no held-out tickets. A normal automatic-route
  synthetic case should produce review_required=false, an authoritative team/SLA, drafter
  invoked once, and final status `auto_routed`. A low-confidence/ambiguous synthetic case should
  produce human review with `Triage — Human` / `Immediate`, drafting skipped, and final status
  `human_review`. An invalid-output path may be recorded only if safely reproduced without
  changing the frozen prompt/model; expected result is `invalid_output`, human-review route,
  and drafting skipped. Ticket 9 must remain Account + Billing / Medium, `secondary_category_present`,
  `Triage — Human` / `Immediate`, no drafting, final status `human_review`. Ticket 10 must
  remain Technical with null urgency/low-confidence review, `Triage — Human` / `Immediate`, no
  drafting, final status `human_review`. A synthetic Account + Critical case must be
  `unsupported_route`, `Triage — Human` / `Immediate`, no drafting, final status `human_review`.

**Validation:** Local unit/contract/regression tests, reproducible development and held-out
reports, artifact hashes, exact deterministic-routing coverage, manual draft review, and a
focused remote Flow batch.

**Evidence:** G3_REMOTE_ACCEPTANCE=PASS. Held-out final evaluation and accuracy criteria are
complete; production `support_triage` Flow local assembly/readiness is complete; remote
Orchestrate Flow proof is supervisor-approved.

**Exit criteria:** Dataset/ground truth are frozen, the single allowed improvement boundary is
respected, model/prompt/threshold are frozen before held-out use, accuracy targets pass, every
path emits structured output, remote Flow behavior is observed, and a supervisor approves G3.

## G4 — FAILURE MODES, EVALUATION, HARDENING

**Purpose:** Exercise meaningful failures, fix the required number per system, complete
whole-system evaluation, and freeze code.

**Entry condition:** Both complete systems have passed their G2/G3 acceptance batches and no
new architecture is needed.

**Checkpoints:**

- [x] **Owner: CODEX** — **Requirement / purpose:** Document at least three meaningful Agent
  failure scenarios, including missing required input, confirmation-bypass attempt, and
  ambiguous capability selection and/or out-of-scope behavior. **Validation method:** Failure
  matrix maps each scenario to expected safeguards and evidence. **Evidence:**
  `artifacts/milestone_7_failure_mode_evidence.md` records 6 Agent failure scenarios with source-linked
  containment and current verification, including
  `AGENT_LOOP_PRESSURE_TEST=PASS_WITH_OUTPUT_HYGIENE_LIMITATION`,
  `ACTUAL_KB_TOOL_CALLS=1`, `UNBOUNDED_TOOL_EXECUTION=NO`, `SIDE_EFFECT_TOOL_CALLS=0`, and
  `TURN_TERMINATED=YES`. The low-severity residual limitation is that the final response echoed
  textual pseudo-tool-call syntax after the valid policy answer; these were response text, not
  actual Orchestrate tool executions.
- [x] **Owner: CODEX** — **Requirement / purpose:** Address/fix at least two Agent failure modes.
  **Validation method:** Add failing-before/passing-after regression evidence locally where
  possible. **Evidence:** PASS. `artifacts/milestone_7_failure_mode_evidence.md` records 4 Agent fixes /
  mitigations, including final field-only UserFlow architecture, confirmation-protected bounded
  Flows, non-overlapping capability descriptions, scope rules, and prefilled-input boundary
  correction, with existing local and supervisor remote verification.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Observe the hardened Agent failure scenarios
  remotely, especially confirmation and side-effect outcomes. **Validation method:** Execute the
  scenario matrix in Watson and inspect COS persistence where applicable. **Evidence:** PASS
  from supervisor-supplied G2 remote evidence already recorded: missing IT fields, ambiguous Jira
  wording, out-of-scope hotel request, confirmation-bypass attempt, IT/booking cancellation zero
  persistence, and confirmed-path exactly-one persistence.
- [x] **Owner: CODEX** — **Requirement / purpose:** Document at least three meaningful Pipeline
  failure scenarios, including taxonomy drift, unsupported/silent-routing risk, and vague or
  multi-category tickets and/or generic drafting. **Validation method:** Failure matrix maps each
  scenario to expected deterministic safeguards and tests. **Evidence:**
  `artifacts/milestone_7_failure_mode_evidence.md` records 11 Pipeline failure scenarios with
  containment, mitigation, and current verification. It explicitly maps taxonomy drift, silent
  routing errors, and generic/non-personalized draft risk to current safeguards.
  GENERIC_DRAFT_FAILURE_PROBE=OBSERVED: supervisor executed a controlled local no-model probe
  where a fake drafter model returned `{"problem_summary":"your issue"}` for ticket
  `G4-GENERIC-DRAFT-PROBE`; the structural validator accepted it with
  `GENERIC_SUMMARY_STRUCTURALLY_ACCEPTED=YES`,
  `GENERIC_DRAFT_PROBE_VALIDATION_STATUS=valid`,
  `GENERIC_DRAFT_PROBE_ATTEMPT_COUNT=1`, and
  `GENERIC_DRAFT_PROBE_REAL_MODEL_CALLS=0`. This satisfies the original engineer's deliberate
  generic-draft failure-mode exercise. Actual v3 quality acceptance remains PASS, but
  deterministic validation does not independently guarantee semantic personalization by
  comparing `problem_summary` against `ticket_text`. No production change was made for this
  low-risk residual limitation.
- [x] **Owner: CODEX** — **Requirement / purpose:** Address/fix at least two Pipeline failure
  modes. **Validation method:** Add failing-before/passing-after regression evidence and verify
  structured outputs remain complete. **Evidence:** PASS. `artifacts/milestone_7_failure_mode_evidence.md`
  records 8 Pipeline fixes / mitigations, including deterministic review triggers,
  unsupported-route protection, bounded invalid-output handling, execution-error handling,
  drafter v3 deterministic composition, separate project-id KEY_VALUE connection, and nullable
  transport normalization.
- [x] **Owner: CODEX** — **Requirement / purpose:** Run all regression tests.
  **Validation method:** `.\.venv\Scripts\python.exe -m pytest -q` passes. **Evidence:** PASS.
  Full pytest passed with `260 passed, 232 warnings in 106.52s (0:01:46)`. Targeted G4 reporting
  tests passed with `3 passed in 2.09s`. `git diff --check` passed with only pre-existing
  LF-to-CRLF warnings on already modified docs/control files.
- [x] **Owner: CODEX** — **Requirement / purpose:** Run the full 30-ticket test set with frozen
  artifacts. **Validation method:** Reproducible run produces exactly 30 structured records and
  preserves immutable labels. **Evidence:** PASS. Derived reporting artifact
  `artifacts/evaluations/support_triage/full30_frozen_combined.json` uses the canonical frozen
  DEV v2 source plus canonical held-out source and records TOTAL_RECORDS=30, UNIQUE_IDS=30,
  DEV_COUNT=15, HELD_OUT_COUNT=15, OVERLAP=0, DROPPED=0, and DUPLICATES=0.
- [x] **Owner: CODEX** — **Requirement / purpose:** Report category accuracy and urgency accuracy.
  **Validation method:** Audited calculations demonstrate ≥80% and ≥75%, with nullable Ticket 10
  handling explicit. **Evidence:** PASS. `artifacts/milestone_8_evaluation_evidence.md` records category
  `27/30 = 90.00%` and urgency `25/28 = 89.29%`; both pass. T10 and T21 null urgency handling
  is explicit.
- [x] **Owner: CODEX** — **Requirement / purpose:** Report human-review rate, auto-route rate, and
  auto-route correctness. **Validation method:** Compute from full-set structured outputs with
  definitions and denominators shown. **Evidence:** PASS. `artifacts/milestone_8_evaluation_evidence.md`
  records human review `10/30 = 33.33%`, auto-route `20/30 = 66.67%`, auto-route correctness
  `18/20 = 90.00%`, and draft-failed `0/30 = 0.00%`.
- [x] **Owner: CODEX** — **Requirement / purpose:** Measure latency and token usage when available.
  **Validation method:** Aggregate timestamp/usage metadata with sample size and limitations.
  **Evidence:** PASS. `artifacts/milestone_8_evaluation_evidence.md` records classifier token/latency
  telemetry across 30 stored records and drafter token/latency telemetry for 12 recorded held-out
  draft calls. Scope is explicitly model/tool telemetry, not end-to-end Orchestrate latency.
- [x] **Owner: CODEX** — **Requirement / purpose:** Estimate cost per ticket and the implication
  at 1,000 tickets/day. **Validation method:** Use dated model pricing/usage assumptions, show the
  calculation, and label estimates. **Evidence:**
  PASS_ESTIMATED_FROM_OFFICIAL_IBM_PUBLIC_RATE. `artifacts/milestone_8_evaluation_evidence.md` records
  IBM watsonx.ai Pricing (`https://www.ibm.com/products/watsonx-ai/pricing`), access date
  `2026-08-18`, model `meta-llama/llama-4-maverick-17b-128e-instruct-fp8`, input rate
  `USD 0.371` per 1,000,000 input tokens, output rate `USD 1.484` per 1,000,000 output tokens,
  classifier cost/ticket `0.0003281124 USD`, drafter cost/actual call
  `0.00012035858333333334 USD`, expected combined model-inference cost/ticket
  `0.00040835145555555557 USD`, and expected combined model-inference cost/1000 tickets
  `0.4083514555555556 USD`. This is model-inference token cost only and excludes fixed plan
  charges, Orchestrate charges, COS/storage, networking, human-review labor, taxes/duties, and
  account-specific costs.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Complete manual draft-quality review after
  hardening. **Validation method:** Apply the approved rubric to representative full-set auto-
  routed drafts. **Evidence:** PASS by reuse of existing supervisor-approved G3 manual
  drafter-quality run 3. `artifacts/milestone_6_draft_quality_review.md` records
  `MANUAL_DRAFT_QUALITY=APPROVED`, drafter v3 SHA
  `80fc2ccaa4a0f14ec918a6324140b3da074388ab1f1a61d19e16556d9b8ddc23`, 4/4 synthetic cases
  passing rubric, zero classifier calls, and zero held-out calls.
- [x] **Owner: CODEX** — **Requirement / purpose:** Write the Agent autonomy-versus-approval
  reflection. **Validation method:** Audit against observed confirmation, review, and escalation
  evidence rather than hypothetical claims. **Evidence:**
  `artifacts/milestone_8_agent_vs_pipeline_reflection.md`, including the requested "What Would Break If
  We Swapped Them?" analysis.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Declare CODE FREEZE after reviewing G4
  evidence. **Validation method:** Supervisor explicitly approves freeze and date/hash are
  recorded. **Evidence:** CODE_FREEZE=ACTIVE. Supervisor explicitly approved closing G4,
  activating Code Freeze, and advancing the project to G5 in the project chat on `2026-08-18`.
  Activation timestamp captured during this pass:
  `2026-08-18T21:06:56.3552272+03:00`. Freeze manifest path:
  `artifacts/code_freeze_manifest.json`; the authoritative working-tree freeze fingerprint is
  stored in that manifest to avoid circularly invalidating this execution ledger. Branch:
  `main`. HEAD commit SHA: `09961318929963d23f4930cbda48a7d6dbc5588a`.
  G4 evidence reviewed; no unresolved G4 blockers. G4_EXIT=APPROVED. G4_STATUS=CLOSED.

**Validation:** Full regression suite, full-set metrics, remote failure observations, cost and
latency audit, failure matrices, and supervisor review.

**Evidence:** G4_CODEX_WORK=COMPLETE. G4_READY_FOR_SUPERVISOR_FREEZE=YES.
G4_SUPERVISOR_APPROVAL=YES. G4_EXIT=APPROVED. G4_STATUS=CLOSED. G4 evaluation, failure-mode
evidence, draft-quality reuse, reflection artifacts, targeted G4 reporting tests, full pytest,
and `git diff --check` are complete. CODE_FREEZE=ACTIVE. FREEZE_MANIFEST=
`artifacts/code_freeze_manifest.json`.

**Exit criteria:** At least three failures are documented and at least two are fixed per system;
all required metrics and reflections are complete; supervisor declares CODE FREEZE. After Code
Freeze, allowed changes are only critical bug fixes, broken-test fixes, documentation
corrections, and evidence corrections. New features, architecture, dependencies, stretch goals,
and cosmetic refactors are forbidden.

### CODE FREEZE

Activation is ACTIVE as of `2026-08-18T21:06:56.3552272+03:00`.

After Code Freeze, allowed changes are:

- critical bug fixes;
- broken-test fixes;
- documentation corrections; and
- evidence corrections.

After Code Freeze, the following are not allowed:

- new features;
- new architecture;
- new dependencies;
- stretch goals; and
- cosmetic refactors.

## G5 — ACCEPTANCE, DOCUMENTATION, DELIVERY

**Purpose:** Audit the complete project against the original task, finalize required evidence
and documentation, demonstrate both systems, and deliver only with human approval.

**Entry condition:** G4 is approved and Code Freeze is active.

**Checkpoints:**

- [x] **Owner: CODEX** — **Requirement / purpose:** Perform a line-by-line acceptance audit
  against the original task. **Validation method:** Traceability matrix maps every requirement to
  implementation, local evidence, remote evidence, and approval state. **Evidence:**
  `artifacts/final_acceptance_traceability.md` records 100 required items: 93 PASS,
  7 PASS_WITH_QUALIFICATION, 0 MANUAL_AUDIT_PENDING, 0 GAP, and 0 NOT_APPLICABLE. The artifact
  preserves the draft semantic-personalization, loop-output-hygiene, latency-scope, and
  model-inference cost qualifications and states that later MANUAL G5 audits remain pending.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Complete the Part A evidence audit.
  **Validation method:** Supervisor verifies the full conversation, grounding, follow-ups,
  confirmations, exact persistence outcomes, scope handling, and exit evidence. **Evidence:**
  PART_A_MANUAL_AUDIT=APPROVED. Supervisor approved this audit in the project chat on
  `2026-08-19`; Codex recorded it at `2026-08-19T10:25:40.7249487+03:00`. The supervisor
  reviewed and approved evidence for the complete policy -> IT -> booking conversation,
  five-domain grounded policy Q&A, missing IT information follow-up, explicit IT confirmation,
  explicit booking confirmation, cancellation/no = zero persistence, confirmed path = intended
  persistence, orientation slot validation, explicit state handling, graceful out-of-scope
  behavior, completion/exit behavior, and the documented loop-pressure output-hygiene
  qualification.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Complete the Part B evidence audit.
  **Validation method:** Supervisor verifies frozen artifacts, metrics, review/routing behavior,
  draft quality, and structured output coverage. **Evidence:** PART_B_MANUAL_AUDIT=APPROVED.
  Supervisor approved this audit in the project chat on `2026-08-19`; Codex recorded it at
  `2026-08-19T10:25:40.7249487+03:00`. The supervisor reviewed and approved the
  intake/classifier contract, closed category and urgency taxonomy, nullable urgency handling,
  confidence threshold `0.80`, human-review triggers, deterministic routing and unsupported-route
  handling, auto-route drafting, no drafting for human review, T09/T10 edge cases, structured
  terminal outputs, classifier/drafter failure containment, frozen 30-ticket evaluation,
  category `27/30`, urgency `25/28`, review `10/30`, auto-route `20/30`, auto-route correctness
  `18/20`, structured output `30/30`, latency/tokens/cost evidence, and generic-draft
  semantic-validation qualification.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Audit both systems' failure reports.
  **Validation method:** Verify at least three documented and at least two addressed/fixed
  failures per system with evidence. **Evidence:** FAILURE_MODES_MANUAL_AUDIT=APPROVED.
  Supervisor approved this audit in the project chat on `2026-08-19`; Codex recorded it at
  `2026-08-19T10:25:40.7249487+03:00`. The supervisor approved 6 documented Agent scenarios,
  4 Agent fixes/mitigations, 11 documented Pipeline scenarios, and 8 Pipeline
  fixes/mitigations, and explicitly accepted the Agent loop-pressure output-hygiene limitation
  and generic-draft semantic-specificity limitation.
- [x] **Owner: CODEX** — **Requirement / purpose:** Finalize `README.md` for setup, architecture,
  operation, validation, limitations, and evidence navigation. **Validation method:** Follow the
  documented steps in a clean approved environment and audit links/claims. **Evidence:** PASS.
  `README.md` was finalized as the G5 reviewer entry point with architecture, capabilities,
  metrics, cost/latency qualifications, setup/configuration, validation, evidence navigation,
  Code Freeze, and stretch-goal scope. Documentation/claim audit passed before final local
  validation.
- [x] **Owner: CODEX** — **Requirement / purpose:** Finalize `FAILURE_MODE_REPORT.md`.
  **Validation method:** Cross-check scenarios, mitigations, regression evidence, and unresolved
  risks against G4. **Evidence:** PASS. `FAILURE_MODE_REPORT.md` records the approved 6 Agent
  scenarios / 4 mitigations and 11 Pipeline scenarios / 8 mitigations, including the required
  repeated-tool, ambiguous-tool, missing-input, out-of-scope, taxonomy-drift, silent-routing, and
  generic-drafting coverage plus preserved residual limitations.
- [x] **Owner: CODEX** — **Requirement / purpose:** Finalize `EVALUATION_REPORT.md`.
  **Validation method:** Recompute/audit accuracy, routing/review, latency, token/cost, and
  1,000-tickets/day results from frozen artifacts. **Evidence:** PASS. `EVALUATION_REPORT.md`
  reports the frozen DEV classifier-output plus deterministic-projection distinction, the
  one-time complete HELD-OUT distinction, category `27/30 = 90.00%`, urgency
  `25/28 = 89.29%`, structured output `30/30 = 100.00%`, review `10/30 = 33.33%`, auto-route
  `20/30 = 66.67%`, auto-route correctness `18/20 = 90.00%`, token/latency evidence, IBM
  pricing assumptions, model-inference-only cost, draft-quality evidence, and residual
  limitations.
- [x] **Owner: CODEX** — **Requirement / purpose:** Finalize `AGENT_VS_PIPELINE.md`.
  **Validation method:** Audit the comparison against implemented architecture and observed
  autonomy/approval behavior. **Evidence:** PASS. `AGENT_VS_PIPELINE.md` documents the actual
  implemented Agent and Pipeline patterns, autonomy boundaries, confirmation/review boundaries,
  state handling, determinism/auditability, cost/reliability implications, failure-mode
  differences, and the required "What Would Break If We Swapped Them?" analysis without claiming
  that Pipelines cannot converse or that Agents are inherently unsafe.
- [x] **Owner: CODEX** — **Requirement / purpose:** Run final local validation.
  **Validation method:** `.\.venv\Scripts\python.exe -m pytest -q` and repository-specific
  validation all pass; inspect `git diff --check` and status. **Evidence:** PASS.
  `.\.venv\Scripts\python.exe -m pytest -q` passed with `260 passed, 232 warnings in 119.08s
  (0:01:59)`. Repository-specific static validation passed through the full suite, including
  Agent contract/static validation, Flow loader/static validation, dataset/freeze integrity, and
  G4 report/frozen-source integrity. Markdown link audit passed for G5 docs and evidence files.
  Claim consistency audit passed: no stale G4-active claim remains, no full30 complete-Pipeline
  overclaim is made, no deterministic semantic-personalization guarantee is claimed, and no
  stretch-goal implementation is claimed. Secret-shaped scan found no API key, private key, or
  bearer token value in the final docs/evidence set. G4 code-freeze production snapshot
  verification passed for 42 frozen production/config/data files; allowed G5 documentation files
  changed after freeze. `git diff --check` passed with only existing LF-to-CRLF warnings on
  touched text files. `git status --short` was inspected. POST_FREEZE_CHANGE_CLASS=
  DOCUMENTATION_EVIDENCE_ONLY; PRODUCTION_BEHAVIOR_CHANGED=NO;
  EXECUTABLE_PRODUCTION_FILES_CHANGED_AFTER_FREEZE=NO.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Perform the final remote demonstration.
  **Validation method:** Demonstrate the required Part A end-to-end conversation and Part B
  automatic/review paths in the target tenant. **Evidence:** PASS. Supervisor-supplied MANUAL
  final remote demonstration evidence was recorded in
  `artifacts/final_remote_demo_evidence.md`. PART_A_FINAL_REMOTE_DEMO=PASS:
  `hr_onboarding_agent` completed a fresh policy -> IT -> booking -> exit conversation with
  actual policy KB invocation, missing-only IT collection, explicit IT confirmation and
  persisted submission, approved-slot booking, explicit booking confirmation and persisted
  booking, and no further side effect after completion. PART_B_AUTO_FINAL_REMOTE_DEMO=PASS:
  authoritative screenshot-backed synthetic demo ticket `FINAL-DEMO-AUTO-002`, Flow instance
  `785a3e09-bf51-47fc-8f31-fdccc489f01c`, produced valid Technical/High classification,
  confidence `0.9`, `review_required=false`, Engineering — Support / `2 hours`, status
  `auto_routed`, valid one-attempt draft, and a draft visibly referencing the dashboard-export
  issue. PART_B_REVIEW_FINAL_REMOTE_DEMO=PASS: synthetic demo ticket `FINAL-DEMO-REVIEW-001`,
  Flow instance `ff0b456e-915a-4347-9a37-a1c3f974a5f5`, produced valid Account primary with
  Billing secondary, Medium urgency, confidence `0.8`, `review_required=true`,
  `review_reasons=["secondary_category_present"]`, Triage — Human / Immediate, status
  `human_review`, and no automatic customer draft. These are synthetic MANUAL G5 demonstration
  cases, not DEV or HELD-OUT evaluation records.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Capture and approve screenshots/demo
  evidence without exposing secrets or sensitive data. **Validation method:** Review evidence
  coverage, redaction, timestamps, and linkage to checkpoints. **Evidence:**
  SCREENSHOT_DEMO_EVIDENCE=APPROVED. Supervisor directly reviewed screenshots showing Part A
  policy Knowledge Base invocation and grounded answer, IT missing-only collection, IT review /
  confirmation / persisted submission, orientation approved-slot selection / review /
  confirmation / persisted booking, clean completion/exit, Part B automatic-route
  `FINAL-DEMO-AUTO-002` tool input and structured output, and Part B human-review
  `FINAL-DEMO-REVIEW-001` tool input and structured output. Supervisor reported no API keys,
  bearer tokens, credentials, or sensitive real personal data were visible in the reviewed
  screenshots. Screenshot provenance is supervisor-reviewed project-chat/manual demonstration
  evidence; no repository screenshot file paths are claimed.
- [x] **Owner: CODEX** — **Requirement / purpose:** Perform final Git diff/status and secret/scope
  audit. **Validation method:** Inspect complete diff, untracked files, ignored-risk locations,
  and secret scan; confirm only approved artifacts changed. **Evidence:** PASS. Current branch:
  `main`. Current HEAD: `09961318929963d23f4930cbda48a7d6dbc5588a`. `git status --short` and
  tracked diff were inspected. Staged files: none. Ignored-risk locations include local `.env`,
  `.venv/`, `.pytest_cache/`, and Python `__pycache__/` directories; `.env` is ignored and not
  tracked. Secret scan over tracked/untracked deliverable source/evidence files found no real
  API key, private key, bearer token, credential, or copied secret; the only broad-pattern hit
  was masked synthetic dummy credential constants in `tests/test_onboarding_persistence.py`.
  Freeze manifest integrity passed: `artifacts/code_freeze_manifest.json` remains the G4
  code-freeze working-tree manifest with fingerprint
  `75edf06d3d4b4b82ce896b9de6e2e2128cfa7f3e813d8ae29805f36108c8e130`, timestamp
  `2026-08-18T21:06:56.3552272+03:00`, and HEAD
  `09961318929963d23f4930cbda48a7d6dbc5588a`. Frozen production/config/data snapshot
  verification passed for 42 files. Frozen dataset hashes and the canonical held-out result hash
  matched approved values. README drafter-failure contract passed: classification/routing
  uncertainty triggers human review; invalid classifier output and classifier execution errors
  are human-contained; drafter failure after a valid automatic route becomes `draft_failed` and
  does not create a new review trigger or alter routing. Final documentation claim audit passed:
  required metrics and threshold are consistent, no full30 complete-Pipeline overclaim is made,
  generic-draft and loop-pressure limitations are preserved, cost is scoped to model inference,
  no stale G4-active status remains, no invented screenshot paths are claimed, and final-demo
  synthetic cases are not treated as DEV or HELD-OUT evaluation cases. `git diff --check` passed
  with only existing LF-to-CRLF warnings on touched text files. POST_FREEZE_CHANGE_CLASS=
  DOCUMENTATION_EVIDENCE_ONLY; PRODUCTION_BEHAVIOR_CHANGED=NO;
  EXECUTABLE_PRODUCTION_FILES_CHANGED_AFTER_FREEZE=NO; FROZEN_DATASET_CHANGED_AFTER_FREEZE=NO;
  FROZEN_HELDOUT_RESULTS_CHANGED_AFTER_FREEZE=NO; FREEZE_MANIFEST_REGENERATED=NO.
- [x] **Owner: CODEX** — **Requirement / purpose:** Perform final repository packaging and
  delivery-hygiene pass before supervisor approval. **Validation method:** Rename/move
  reviewer-facing artifacts to milestone/final-deliverable names, preserve development history,
  audit documentation links and stale references, verify exact final-demo labels, run local
  validation, create a final delivery manifest, and do not stage, commit, push, rerun remote
  evaluations, or call watsonx.ai. **Evidence:** PASS. Packaging preserved Code Freeze and did
  not change classifier, routing, drafting, dataset, model, prompt, threshold, Agent, Flow, or
  production tool behavior. `docs/PROJECT_SPEC.md` moved to
  `artifacts/development_history/PROJECT_SPEC_HISTORY.md`; `docs/EXECUTION_PLAN.md` moved to
  `artifacts/development_history/PROJECT_EVIDENCE_LEDGER.md`; final reviewer-facing docs are
  `README.md`, `docs/AGENT_DECISION_FLOW.md`, `docs/SUPPORT_TRIAGE_TAXONOMY.md`, and
  `docs/SYSTEM_ARCHITECTURE.md`; evidence artifacts use milestone/final-deliverable names and
  are indexed in `artifacts/README.md`. Targeted evaluation-report pytest passed with
  `3 passed in 16.44s`. Core Agent/Flow contract subset passed with
  `114 passed, 232 warnings in 111.12s`. Final full local pytest passed with
  `260 passed, 232 warnings in 95.74s`. Final delivery package inventory is recorded in
  `artifacts/final_delivery_manifest.json`.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Grant final project approval.
  **Validation method:** Supervisor signs the acceptance/evidence audit. **Evidence:**
  FINAL_PROJECT_APPROVAL=APPROVED. Supervisor explicitly supplied final project approval in the
  project chat for final Git delivery.
- [x] **Owner: MANUAL** — **Requirement / purpose:** Authorize final commit and push explicitly.
  **Validation method:** Supervisor provides direct instruction after approval; until then no
  staging, commit, or push occurs. **Evidence:**
  FINAL_COMMIT_PUSH_AUTHORIZATION=APPROVED. Supervisor explicitly authorized final commit and
  push in the project chat.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Commit/push only after explicit instruction.
  **Validation method:** Verify approved scope and destination, then record resulting commit and
  remote status. **Evidence:** PENDING.

**Validation:** Traceability and evidence audits, final passing local tests, complete remote
demonstration, safe screenshots, documentation review, and clean Git/security audit.

**Evidence:** PENDING.

**Exit criteria:** Every original requirement has approved evidence, all required reports and
documentation are final, tests and demonstrations pass, final human approval is recorded, and
delivery actions occur only under explicit instruction.
