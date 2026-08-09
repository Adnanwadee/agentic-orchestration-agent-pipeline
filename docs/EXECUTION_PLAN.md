Current Gate: G1
Current Checkpoint: G1A - Remote Orchestrate Authentication
Code Freeze: NOT ACTIVE

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
  of truth at `docs/PROJECT_SPEC.md`. **Validation method:** Audit it against every supplied
  architecture, contract, constraint, fallback, non-goal, edge case, and acceptance
  requirement. **Evidence:** Full new-file diff inspected; the G0 correction pass revalidated
  the 419-line file with A–F requirement divisions, routing/edge cases, frozen decisions,
  constraints, fallbacks, non-goals, and acceptance; no implementation code is included.
- [x] **Owner: CODEX** — **Requirement / purpose:** Create only this six-gate progress source at
  `docs/EXECUTION_PLAN.md`. **Validation method:** Audit all gates for purpose, entry condition,
  owned checkpoints, validation/evidence, and exit criteria. **Evidence:** Full new-file diff
  inspected; exactly G0–G5 are present with the required fields and owned evidence checkpoints.
- [x] **Owner: CODEX** — **Requirement / purpose:** Preserve the existing local environment and
  stay inside the G0 file boundary. **Validation method:** Confirm the final diff/status contain
  only the three authorized new files and no dependencies, features, secrets, staging, commits,
  or pushes. **Evidence:** File inventory and full new-file diffs show only `AGENTS.md`,
  `docs/PROJECT_SPEC.md`, and `docs/EXECUTION_PLAN.md`; tracked diff is empty and the
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
  `docs/PROJECT_SPEC.md`, and `docs/EXECUTION_PLAN.md`; project-local pytest verification;
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

- [ ] **Owner: MANUAL** — **Requirement / purpose:** Authenticate to remote watsonx
  Orchestrate. **Validation method:** Perform approved authentication and observe a successful
  tenant command/session. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Prove watsonx.ai connectivity with a real
  API smoke call. **Validation method:** Send a minimal approved request and capture a
  successful non-sensitive result. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** List models actually available in the
  target Watson environment. **Validation method:** Query the tenant model catalog and preserve
  dated output. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Select one suitable available model under
  the specification's decision rule. **Validation method:** Review availability and smoke-call
  evidence; benchmark only if the selected model later fails quality targets. **Evidence:**
  PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Prepare the minimal real
  `hr_onboarding_agent` artifact/configuration that will be expanded in G2, not a disposable
  Hello Agent. **Validation method:** Run all available local/static validation and inspect its
  bounded instructions/configuration before import. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Import and test a minimal real
  `hr_onboarding_agent`. **Validation method:** Import it into Orchestrate and observe a minimal
  successful conversation. **Evidence:** PENDING.

### G1B — Capability Spikes

- [ ] **Owner: CODEX** — **Requirement / purpose:** Prepare the minimal Prompt Node strict-
  structured-output spike artifact. **Validation method:** Run every available local/static/
  compile validation that does not require remote credentials. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Prove Prompt Node strict structured output.
  **Validation method:** Run input → Prompt Node → validated strict structured output → end in
  the tenant, including a repeatability check. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Prepare the User Activity spike artifact for
  ask value → retain value → confirm → Yes/No branch. **Validation method:** Run all available
  local/static validation and inspect both branch definitions. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Prove User Activity multi-turn state and
  protected confirmation. **Validation method:** Run ask value → retain value → confirm → Yes/No
  branch and observe both branches. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Prepare the one-document native Knowledge
  Base definition/configuration using one identified, approved supplied mock HR document.
  **Validation method:** Run available local/static validation and verify that no policy content
  was invented. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Prove native Knowledge Base viability with
  one document. **Validation method:** Ask grounded and unsupported questions; capture citation
  or grounding behavior and abstention quality. **Evidence:** PENDING.

### G1C — Persistence

- [ ] **Owner: MANUAL** — **Requirement / purpose:** Provision/approve Cloudant Lite and the
  `onboarding_mock` database. **Validation method:** Observe the service and named database in
  the target account. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Configure an Orchestrate connection without
  committing credentials. **Validation method:** Inspect the runtime connection and repository
  secret scan/status. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** If a third-party Cloudant package is
  actually required, prove tenant compatibility for its exact approved pinned version before
  dependent logic is implemented; otherwise record that no third-party package is required.
  **Validation method:** Run a remote Python 3.12 import preflight for the exact version, or
  approve the dependency-free path, with evidence. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Prepare the smallest remote persistence probe/
  tool for the intended runtime path, preferring no third-party dependency and adding none
  without supervisor approval. **Validation method:** Run all local schema/static/package checks
  available for the frozen dependency strategy. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Prove a real remote Cloudant write/read.
  **Validation method:** Write a non-sensitive probe through the intended runtime path and read
  the same record back. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Freeze the smallest tenant-compatible
  Cloudant transport/dependency strategy. **Validation method:** Record the observed package,
  transport, Python 3.12, read-only-filesystem, and package-size evidence; add no dependency
  without approval. **Evidence:** PENDING.

### G1 frozen decisions

- [ ] **Owner: CODEX** — **Requirement / purpose:** Record and freeze the selected model.
  **Validation method:** Update the specification only from the G1 model-list and smoke-call
  evidence. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Freeze `PIPELINE_LLM_MODE` as `PROMPT_NODE`
  or `PYTHON_WATSONX_TOOL`. **Validation method:** Apply the Prompt Node pass/fail rule exactly
  and cite spike evidence. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Freeze the User Activity implementation
  strategy. **Validation method:** Apply the primary/fallback rule to observed Yes/No state
  behavior. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Freeze native Knowledge Base viability.
  **Validation method:** Record spike quality; allow custom RAG only after one reasonable native
  tuning attempt materially fails and supervisor approves fallback. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Freeze Cloudant transport and dependency
  strategy. **Validation method:** Record the proven remote write/read path and compatibility
  result. **Evidence:** PENDING.

**Validation:** Real tenant evidence for every remote claim; local files/tests for recorded
decisions; no decision inferred from documentation alone.

**Evidence:** PENDING.

**Exit criteria:** Connectivity and all three spikes are observed, persistence is proven, all
five platform-dependent decisions are recorded/frozen, local validation passes, and a
supervisor explicitly approves G1 exit.

## G2 — COMPLETE PART A: HR ONBOARDING AGENT

**Purpose:** Build and prove the complete bounded HR onboarding Agent after G1 decisions are
frozen.

**Entry condition:** G1 exit is approved; model, LLM mode, User Activity strategy, native KB
viability, and Cloudant strategy are frozen.

**Checkpoints:**

- [ ] **Owner: CODEX** — **Requirement / purpose:** Prepare/copy the five supplied mock HR
  documents from the approved reference source into the project while preserving their policy
  content and exact expected filenames. **Validation method:** Verify all five filenames, trace
  content to the supplied/reference documents, confirm no policy content was invented for the
  implementation, and scan for secrets or real personal data. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Prepare the full native HR Policy Knowledge
  Base definition/configuration from the five supplied documents. **Validation method:** Run all
  available local/static validation and verify exact document references. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Import and prove the full native HR Policy
  Knowledge Base from all five documents. **Validation method:** Import/index in the tenant and
  observe all sources available. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Prove grounded policy Q&A across the five
  topics. **Validation method:** Run a planned remote question set and inspect grounding against
  source documents. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Prove unknown-policy abstention.
  **Validation method:** Ask unsupported policy questions and verify no invented policy answer.
  **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Implement minimal Cloudant persistence tools
  for `it_request` and `orientation_booking`. **Validation method:** Local schema/contract tests,
  mocked transport tests, secret scan, and dependency audit. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Implement the IT request flow/capability with
  employee name, employee role, and required systems. **Validation method:** Local flow/schema
  tests and payload contract inspection. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Prove missing IT fields are requested and
  never invented. **Validation method:** Remote multi-turn tests omitting each required field.
  **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Prove IT cancellation causes no persistence.
  **Validation method:** Cancel at confirmation and verify no matching Cloudant record exists.
  **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Prove IT confirmation creates exactly one
  record. **Validation method:** Perform one confirmed action and verify exactly one matching
  Cloudant record. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Define stable hardcoded orientation slots.
  **Validation method:** Local tests validate slot identifiers, display values, and selection
  behavior. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Implement the orientation booking
  flow/capability. **Validation method:** Local schema, slot, confirmation-branch, and persistence
  contract tests. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Prove booking cancellation causes no
  persistence. **Validation method:** Cancel at confirmation and verify no matching Cloudant
  record exists. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Prove booking confirmation creates exactly
  one record. **Validation method:** Perform one confirmed action and verify exactly one matching
  Cloudant record. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Configure the three clear, non-overlapping
  capability descriptions from the Agent contract. **Validation method:** Static contract audit
  and capability-selection test cases. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Assemble/update the complete
  `hr_onboarding_agent` artifact with the full KB, IT capability, booking capability, approved
  instructions, non-overlapping descriptions, and frozen G1 strategy. **Validation method:** Run
  all available local/static/compile validation and audit the integrated artifact. **Evidence:**
  PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Import and prove the complete default-style
  Agent. **Validation method:** Import the prepared real Agent and run one full multi-turn
  conversation covering policy Q&A, IT request, orientation booking, confirmations, and clear exit.
  **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Prove graceful out-of-scope behavior and
  ambiguous capability selection. **Validation method:** Run planned remote prompts and verify
  polite decline/clarification without unintended tools or side effects. **Evidence:** PENDING.

**Validation:** Frequent local `.\.venv\Scripts\python.exe -m pytest -q`; one focused remote IT
batch, one focused remote booking batch, and one final Agent end-to-end batch with Cloudant
evidence.

**Evidence:** PENDING.

**Exit criteria:** All Agent contracts and five supplied documents are prepared, local tests pass,
every required remote behavior and persistence outcome is observed, and a supervisor approves
Part A completion.

## G3 — COMPLETE PART B: SUPPORT TRIAGE PIPELINE

**Purpose:** Build, calibrate, freeze, and evaluate the Flow-orchestrated support-triage
Pipeline without leaking held-out labels into development.

**Entry condition:** G2 exit is approved and the G1-selected model and Pipeline LLM mode remain
frozen unless a documented approved fallback is activated.

**Checkpoints:**

- [ ] **Owner: CODEX** — **Requirement / purpose:** Create the 30-ticket dataset while retaining
  every originally supplied ticket. **Validation method:** Dataset structural and identity tests
  verify 30 unique records and source-ticket representation. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Establish the 15 development / 15 held-out
  split without leakage. **Validation method:** Automated split-size, uniqueness, disjointness,
  and coverage tests. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Approve and freeze ground-truth labels before
  classifier evaluation. **Validation method:** Supervisor reviews labels and records a content
  hash/version; later diffs must be empty. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Implement Pydantic intake, classification,
  and output schemas matching the specification. **Validation method:** Positive, boundary,
  null-urgency, and rejection unit tests. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Implement the classifier in the frozen G1 LLM
  mode without classifier-owned review logic. **Validation method:** Contract tests and source
  audit verify only permitted fields and closed taxonomy. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Implement bounded invalid-label/structured-
  output handling. **Validation method:** Tests inject invalid labels, malformed structure, and
  exhausted handling; each must end in human review with structured output and no drafting.
  **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Preserve Ticket 9 as Account + Billing,
  Medium and require review. **Validation method:** Named regression test asserts classification,
  secondary category, review reason, and no auto-route. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Preserve Ticket 10 as Technical, null urgency,
  low confidence and require review. **Validation method:** Named regression test asserts no
  `unknown` label, both review triggers, explicit evaluation reporting, and no drafting.
  **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Evaluate the initial classifier on the
  development set. **Validation method:** Reproducible run records predictions, errors,
  category/urgency metrics, and model/prompt version without reading held-out outcomes.
  **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Permit at most one meaningful classifier
  improvement cycle if development evidence requires it. **Validation method:** Record either
  one justified prompt/classifier change with before/after development metrics or a documented
  no-change decision. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Select a threshold from 0.50, 0.60, 0.70, and
  0.80 using observed development behavior. **Validation method:** Compare candidates on review
  rate, auto-route rate/correctness, and errors; record the selection rationale. **Evidence:**
  PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Freeze the model, prompt, and threshold
  before final evaluation. **Validation method:** Supervisor approves version identifiers and
  hashes; subsequent evaluation audit shows no changes. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Implement the deterministic human-review
  policy exactly. **Validation method:** Parameterized unit tests cover every independent trigger
  and combinations of triggers. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Implement deterministic authoritative routing.
  **Validation method:** Exhaustive table-driven tests cover every supported combination and
  exact team/SLA labels. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Protect unsupported Account + Critical.
  **Validation method:** Named test verifies Triage — Human / Immediate, unsupported-route
  reason, no invented route, and no drafting call. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Implement response drafting only for
  automatically routed tickets. **Validation method:** Call-count tests prove review paths skip
  drafting; contract tests require problem reference, personalization, tone, team/SLA
  consistency, and no invented resolution. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Review response-draft quality.
  **Validation method:** Human rubric review of representative routed drafts for personalization,
  professionalism, fidelity, and non-invention. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Produce one structured output for every path.
  **Validation method:** End-to-end tests cover auto-route, every review trigger, invalid output,
  nullable draft, and no dropped/duplicate ticket. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Run the frozen held-out/final evaluation once
  without tuning on its outcomes. **Validation method:** Reproducible 15-ticket run with frozen
  artifact hashes and complete predictions. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Meet category accuracy of at least 80%.
  **Validation method:** Compute against immutable held-out labels and independently audit the
  numerator/denominator. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Meet urgency accuracy of at least 75% while
  separately reporting Ticket 10 unknown-urgency handling. **Validation method:** Compute under
  the documented nullable-urgency metric rule and audit the numerator/denominator. **Evidence:**
  PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Assemble the complete `support_triage` Flow
  artifact using the frozen G1 Pipeline LLM mode and all implemented deterministic components.
  **Validation method:** Run every available local/static/compile and end-to-end contract test
  before remote import. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Prove the complete Pipeline in remote
  watsonx Orchestrate Flow. **Validation method:** Execute representative automatic, review,
  invalid, Ticket 9, Ticket 10, and Account + Critical paths in the tenant. **Evidence:** PENDING.

**Validation:** Local unit/contract/regression tests, reproducible development and held-out
reports, artifact hashes, exact deterministic-routing coverage, manual draft review, and a
focused remote Flow batch.

**Evidence:** PENDING.

**Exit criteria:** Dataset/ground truth are frozen, the single allowed improvement boundary is
respected, model/prompt/threshold are frozen before held-out use, accuracy targets pass, every
path emits structured output, remote Flow behavior is observed, and a supervisor approves G3.

## G4 — FAILURE MODES, EVALUATION, HARDENING

**Purpose:** Exercise meaningful failures, fix the required number per system, complete
whole-system evaluation, and freeze code.

**Entry condition:** Both complete systems have passed their G2/G3 acceptance batches and no
new architecture is needed.

**Checkpoints:**

- [ ] **Owner: CODEX** — **Requirement / purpose:** Document at least three meaningful Agent
  failure scenarios, including missing required input, confirmation-bypass attempt, and
  ambiguous capability selection and/or out-of-scope behavior. **Validation method:** Failure
  matrix maps each scenario to expected safeguards and evidence. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Address/fix at least two Agent failure modes.
  **Validation method:** Add failing-before/passing-after regression evidence locally where
  possible. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Observe the hardened Agent failure scenarios
  remotely, especially confirmation and side-effect outcomes. **Validation method:** Execute the
  scenario matrix in Watson and inspect Cloudant where applicable. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Document at least three meaningful Pipeline
  failure scenarios, including taxonomy drift, unsupported/silent-routing risk, and vague or
  multi-category tickets and/or generic drafting. **Validation method:** Failure matrix maps each
  scenario to expected deterministic safeguards and tests. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Address/fix at least two Pipeline failure
  modes. **Validation method:** Add failing-before/passing-after regression evidence and verify
  structured outputs remain complete. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Run all regression tests.
  **Validation method:** `.\.venv\Scripts\python.exe -m pytest -q` passes. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Run the full 30-ticket test set with frozen
  artifacts. **Validation method:** Reproducible run produces exactly 30 structured records and
  preserves immutable labels. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Report category accuracy and urgency accuracy.
  **Validation method:** Audited calculations demonstrate ≥80% and ≥75%, with nullable Ticket 10
  handling explicit. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Report human-review rate, auto-route rate, and
  auto-route correctness. **Validation method:** Compute from full-set structured outputs with
  definitions and denominators shown. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Measure latency and token usage when available.
  **Validation method:** Aggregate timestamp/usage metadata with sample size and limitations.
  **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Estimate cost per ticket and the implication
  at 1,000 tickets/day. **Validation method:** Use dated model pricing/usage assumptions, show the
  calculation, and label estimates. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Complete manual draft-quality review after
  hardening. **Validation method:** Apply the approved rubric to representative full-set auto-
  routed drafts. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Write the Agent autonomy-versus-approval
  reflection. **Validation method:** Audit against observed confirmation, review, and escalation
  evidence rather than hypothetical claims. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Declare CODE FREEZE after reviewing G4
  evidence. **Validation method:** Supervisor explicitly approves freeze and date/hash are
  recorded. **Evidence:** PENDING.

**Validation:** Full regression suite, full-set metrics, remote failure observations, cost and
latency audit, failure matrices, and supervisor review.

**Evidence:** PENDING.

**Exit criteria:** At least three failures are documented and at least two are fixed per system;
all required metrics and reflections are complete; supervisor declares CODE FREEZE. After Code
Freeze, allowed changes are only critical bug fixes, broken-test fixes, documentation
corrections, and evidence corrections. New features, architecture, dependencies, stretch goals,
and cosmetic refactors are forbidden.

### CODE FREEZE

Activation is PENDING the MANUAL checkpoint above.

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

- [ ] **Owner: CODEX** — **Requirement / purpose:** Perform a line-by-line acceptance audit
  against the original task. **Validation method:** Traceability matrix maps every requirement to
  implementation, local evidence, remote evidence, and approval state. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Complete the Part A evidence audit.
  **Validation method:** Supervisor verifies the full conversation, grounding, follow-ups,
  confirmations, exact persistence outcomes, scope handling, and exit evidence. **Evidence:**
  PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Complete the Part B evidence audit.
  **Validation method:** Supervisor verifies frozen artifacts, metrics, review/routing behavior,
  draft quality, and structured output coverage. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Audit both systems' failure reports.
  **Validation method:** Verify at least three documented and at least two addressed/fixed
  failures per system with evidence. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Finalize `README.md` for setup, architecture,
  operation, validation, limitations, and evidence navigation. **Validation method:** Follow the
  documented steps in a clean approved environment and audit links/claims. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Finalize `FAILURE_MODE_REPORT.md`.
  **Validation method:** Cross-check scenarios, mitigations, regression evidence, and unresolved
  risks against G4. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Finalize `EVALUATION_REPORT.md`.
  **Validation method:** Recompute/audit accuracy, routing/review, latency, token/cost, and
  1,000-tickets/day results from frozen artifacts. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Finalize `AGENT_VS_PIPELINE.md`.
  **Validation method:** Audit the comparison against implemented architecture and observed
  autonomy/approval behavior. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Run final local validation.
  **Validation method:** `.\.venv\Scripts\python.exe -m pytest -q` and repository-specific
  validation all pass; inspect `git diff --check` and status. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Perform the final remote demonstration.
  **Validation method:** Demonstrate the required Part A end-to-end conversation and Part B
  automatic/review paths in the target tenant. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Capture and approve screenshots/demo
  evidence without exposing secrets or sensitive data. **Validation method:** Review evidence
  coverage, redaction, timestamps, and linkage to checkpoints. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Perform final Git diff/status and secret/scope
  audit. **Validation method:** Inspect complete diff, untracked files, ignored-risk locations,
  and secret scan; confirm only approved artifacts changed. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Grant final project approval.
  **Validation method:** Supervisor signs the acceptance/evidence audit. **Evidence:** PENDING.
- [ ] **Owner: MANUAL** — **Requirement / purpose:** Authorize final commit and push explicitly.
  **Validation method:** Supervisor provides direct instruction after approval; until then no
  staging, commit, or push occurs. **Evidence:** PENDING.
- [ ] **Owner: CODEX** — **Requirement / purpose:** Commit/push only after explicit instruction.
  **Validation method:** Verify approved scope and destination, then record resulting commit and
  remote status. **Evidence:** PENDING.

**Validation:** Traceability and evidence audits, final passing local tests, complete remote
demonstration, safe screenshots, documentation review, and clean Git/security audit.

**Evidence:** PENDING.

**Exit criteria:** Every original requirement has approved evidence, all required reports and
documentation are final, tests and demonstrations pass, final human approval is recorded, and
delivery actions occur only under explicit instruction.
