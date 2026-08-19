# Milestone 6 — Draft Quality Review

MANUAL_REVIEW=APPROVED

MANUAL_REVIEW_RUN_1=FAIL

Structural run-1 execution evidence supplied by supervisor:

- DRAFT_REVIEW_CASES=4
- executed_case_count=4
- CLASSIFIER_CALLS=0
- HELD_OUT_CALLS=0
- final_status=DRAFT_REVIEW_HARNESS=STRUCTURALLY_VALID

Quality result: FAIL. All four cases were structurally valid but contained unsupported
future-action and/or SLA-response promises. Structural validity is not a quality pass.

## MANUAL Run 1 Failures

### DRAFT-SMOKE-001

Observed draft text:

> The Billing — Standard team will review your account and respond within 4 hours.

Failure reasons:

- Invented future review action.
- Converted SLA into guaranteed response timing.

### DRAFT-SMOKE-002

Observed draft text:

> The Engineering — Support team ... are committed to responding within 2 hours, have been notified and will review this further.

Failure reasons:

- Invented notification.
- Invented future review.
- Response-time promise.

### DRAFT-SMOKE-003

Observed draft text:

> The Customer Success team has been assigned to assistyou with this request. We will address this within our 4 hours SLA.

Failure reasons:

- SLA converted into promised future action/timing.
- Wording-quality defect `assistyou`.

### DRAFT-SMOKE-004

Observed draft text:

> The Customer Success team ... will review this request. We aim to respond within 2 business days.

Failure reasons:

- Invented future review.
- SLA converted into expected response timing.

MANUAL_REVIEW_RUN_2=FAIL

Structural run-2 execution evidence supplied by supervisor:

- Structural result: PASS 4/4

Quality result: FAIL 2/4. Structural validity is not a quality pass.

Passing cases:

- DRAFT-SMOKE-001
- DRAFT-SMOKE-002

## MANUAL Run 2 Failures

### DRAFT-SMOKE-003

Observed draft text:

> We are assisting with this request.

Failure reason:

- Invented current action not established by pipeline state.

### DRAFT-SMOKE-004

Observed draft text:

> will provide the necessary information.

Failure reason:

- Unsupported future-action/result promise.

CORRECTIVE_DRAFTER_VERSION=support-triage-drafter-v3
CORRECTIVE_DRAFTER_PROMPT_SHA256=80fc2ccaa4a0f14ec918a6324140b3da074388ab1f1a61d19e16556d9b8ddc23
MANUAL_REVIEW_RUN_3=PASS
MANUAL_DRAFT_QUALITY=APPROVED

Structural run-3 execution evidence supplied by supervisor:

- DRAFT_REVIEW_CASES=4
- executed_case_count=4
- CLASSIFIER_CALLS=0
- HELD_OUT_CALLS=0
- final_status=DRAFT_REVIEW_HARNESS=STRUCTURALLY_VALID
- model_id=meta-llama/llama-4-maverick-17b-128e-instruct-fp8
- draft_prompt_version=support-triage-drafter-v3
- draft_prompt_sha256=80fc2ccaa4a0f14ec918a6324140b3da074388ab1f1a61d19e16556d9b8ddc23
- all four outputs valid on attempt 1

Supervisor rubric:

- DRAFT-SMOKE-001=PASS
- DRAFT-SMOKE-002=PASS
- DRAFT-SMOKE-003=PASS
- DRAFT-SMOKE-004=PASS

FINAL_DRAFTER_VERSION=support-triage-drafter-v3
FINAL_DRAFTER_SHA256=80fc2ccaa4a0f14ec918a6324140b3da074388ab1f1a61d19e16556d9b8ddc23

For remaining G3 evaluation, drafter v3 is frozen. No drafter v4 will be made based on
HELD-OUT outcomes. The minor capitalization style observed in run 3 is non-blocking and was
not tuned.

Prepared harness:

`.\.venv\Scripts\python.exe scripts\run_support_triage_draft_review.py --smoke-real-drafter`

The harness is for supervisor execution only. It performs drafting calls only, uses four
synthetic non-dataset cases, performs zero classifier calls, performs zero held-out calls, and
does not judge natural-language quality automatically.

## Final Run 3 Review Rubric

Supervisor-approved final run-3 rubric status:

| Case ID | Problem specifically referenced | Personalized / non-generic | Professional tone | Assigned team consistent | SLA consistent | No invented resolution | No invented investigation/contact/refund/fix | No unsupported future-action/SLA promise | Reviewer notes |
|---|---|---|---|---|---|---|---|---|---|
| DRAFT-SMOKE-001 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | Supervisor approved. |
| DRAFT-SMOKE-002 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | Supervisor approved. |
| DRAFT-SMOKE-003 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | Supervisor approved. |
| DRAFT-SMOKE-004 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | Supervisor approved. |

## Final Run 3 Evidence

- Model ID: `meta-llama/llama-4-maverick-17b-128e-instruct-fp8`
- Draft prompt version: `support-triage-drafter-v3`
- Draft prompt SHA-256: `80fc2ccaa4a0f14ec918a6324140b3da074388ab1f1a61d19e16556d9b8ddc23`
- DRAFT_REVIEW_CASES: `4`
- CLASSIFIER_CALLS: `0`
- HELD_OUT_CALLS: `0`
- Overall manual decision: `MANUAL_DRAFT_QUALITY=APPROVED`
