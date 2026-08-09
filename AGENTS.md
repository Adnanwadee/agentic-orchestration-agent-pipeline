# Repository Operating Rules

This repository is developed gate-by-gate under human supervision.

## Sources of truth

- Read `docs/PROJECT_SPEC.md` before editing; it is the technical source of truth.
- Read `docs/EXECUTION_PLAN.md` before editing; it is the execution and progress source.
- If the two documents conflict, stop and report the conflict.

## Scope control

- Work only on the current unchecked checkpoint.
- Never implement a future gate or unapproved checkpoint.
- Keep implementations minimal and requirement-driven.
- Prefer deterministic code wherever an LLM is unnecessary.
- Never add or change dependencies without explicit supervisor approval.
- Do not add frameworks, abstractions, or stretch goals outside the specification.
- If real Watson platform behavior conflicts with the written design, stop and report it.

## Evidence and quality

- Follow the evidence chain: implementation, local validation, required remote validation,
  observed business outcome, then supervisor approval.
- Run the checkpoint's required validation before reporting completion.
- On Windows, use the repository `.venv` executables for project validation, or otherwise
  prove the active interpreter is that `.venv`; never silently use global Python, pytest, or
  Orchestrate executables.
- Never invent Watson API, tenant, model, Prompt Node, User Activity, Knowledge Base, or
  Cloudant behavior.
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

## Handoff

Report:

- changed files;
- tests and their exact results;
- unresolved issues or design conflicts;
- required MANUAL checks and missing evidence.

Gate completion always requires the exit criteria in `docs/EXECUTION_PLAN.md`; a file or
implementation alone is not proof of completion.
