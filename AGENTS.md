# Repository Operating Rules

This repository is developed gate-by-gate under human supervision.

## Sources of truth

- Read `docs/SYSTEM_ARCHITECTURE.md` before editing; it is the final reviewer-facing
  technical architecture source.
- Read `artifacts/development_history/PROJECT_SPEC_HISTORY.md` when historical technical
  decisions or gate chronology matter.
- Read `artifacts/development_history/PROJECT_EVIDENCE_LEDGER.md` before editing; it is the
  execution and progress source.
- If the sources conflict, stop and report the conflict.

## Scope control

- Work only on the current unchecked checkpoint.
- Never implement a future gate or unapproved checkpoint.
- Keep implementations minimal and requirement-driven.
- Prefer deterministic code wherever an LLM is unnecessary.
- Never add or change dependencies without explicit supervisor approval.
- Do not add frameworks, abstractions, or stretch goals outside the specification.
- If real Watson platform behavior conflicts with the written design, stop and report it.
- Do not let stage, probe, or spike implementation silently become production code.

## Evidence and quality

- Follow the evidence chain: implementation, local validation, required remote validation,
  observed business outcome, then supervisor approval.
- Run the checkpoint's required validation before reporting completion.
- On Windows, use the repository `.venv` executables for project validation, or otherwise
  prove the active interpreter is that `.venv`; never silently use global Python, pytest, or
  Orchestrate executables.
- Never invent Watson API, tenant, model, Prompt Node, User Activity, Knowledge Base,
  persistence, or storage behavior.
- Never claim remote behavior without observed evidence.
- Never modify frozen ground truth to improve evaluation results.
- Never weaken expected tests to match incorrect implementation.
- Record failures and uncertainty accurately; stop rather than guess.
- Mark a CODEX checkpoint `[x]` only after its stated validation succeeds.
- Never mark a MANUAL checkpoint complete without supervisor-supplied evidence.

## Security and repository hygiene

- Never commit secrets, credentials, tokens, connection values, or customer data.
- Use runtime Watson/Orchestrate connections for remote credentials.
- Never stage, commit, or push unless explicitly instructed.
- Preserve unrelated and pre-existing user work.
- Keep remote Python/tool filenames to safe alphanumeric characters and underscores.
- Before gate exit, classify temporary assets as DELETE, DURABLE EVIDENCE, or PROMOTE.
- Promoted production assets must use domain-oriented names.
- Delete obsolete spikes after durable evidence is recorded.
- Manual remote cleanup remains supervisor-owned when credentials or tenant mutation are
  involved.
- Do not convert Part A into one fixed onboarding Flow; `hr_onboarding_agent` remains the
  top-level ReAct decision-maker, while IT and booking may use bounded deterministic Flows that
  receive isolated evidence before final Agent integration.

## Handoff

Report:

- changed files;
- tests and their exact results;
- unresolved issues or design conflicts;
- required MANUAL checks and missing evidence.

Gate completion always requires the exit criteria in
`artifacts/development_history/PROJECT_EVIDENCE_LEDGER.md`; a file or implementation alone is
not proof of completion.
