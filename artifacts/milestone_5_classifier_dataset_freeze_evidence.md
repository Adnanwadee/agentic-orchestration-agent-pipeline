# Milestone 5 — Classifier Dataset Freeze Evidence

STATUS = FROZEN_APPROVED

GROUND_TRUTH_FREEZE=APPROVED
SPLIT_FREEZE=APPROVED
NULL_URGENCY_METRIC_RULE=APPROVED

NO CLASSIFIER MODEL CALL OCCURRED BEFORE DATASET FREEZE.

## Scope Boundary

This artifact records the approved Part B support-triage dataset, ground-truth labels, and
15-development / 15-held-out split. It preserves the original candidate review table below as
proposal chronology, with the final freeze decision recorded here.

No watsonx.ai classifier call, Prompt Node execution, remote IBM action, routing implementation,
drafting implementation, threshold selection, development evaluation, or held-out evaluation was
performed before the dataset/ground-truth/split freeze.

Supervisor approval was supplied in the second G3 execution package. The supervisor approved all
30 ticket texts, all T01-T30 labels, T21 specifically as `technical` / `null` / `null`, the exact
DEV/HELD_OUT split, T09/T10 placement in DEVELOPMENT, and the null-urgency metric rule.

## Structural Audit

| Check | Result |
|---|---:|
| TOTAL_TICKETS | 30 |
| Expected ID coverage | T01-T30 |
| Missing IDs | 0 |
| Duplicate IDs | 0 |
| Duplicate ticket texts | 0 |
| Supplied tickets | 10 |
| Synthetic tickets | 20 |
| T01-T10 verbatim preservation | PASS |
| Secret/PII-like accidental test data | PASS - fictional support content only |

Seed-ticket text changes: NONE.

## Coverage Counts

### Primary Category

| Category | Count |
|---|---:|
| billing | 8 |
| technical | 10 |
| account | 8 |
| general | 4 |

### Urgency

| Urgency | Count |
|---|---:|
| low | 10 |
| medium | 10 |
| high | 5 |
| critical | 3 |
| null | 2 |

### Secondary Category

| Secondary category | Count |
|---|---:|
| null | 26 |
| billing | 2 |
| account | 2 |

No secondary `technical` or `general` labels are present in the proposed ground truth.

### Category x Urgency Matrix

| Category | low | medium | high | critical | null |
|---|---:|---:|---:|---:|---:|
| billing | 3 | 2 | 3 | 0 | 0 |
| technical | 1 | 3 | 1 | 3 | 2 |
| account | 2 | 5 | 1 | 0 | 0 |
| general | 4 | 0 | 0 | 0 | 0 |

Coverage note: the dataset has meaningful representative coverage, not a Cartesian product.
There are no `billing + critical`, `account + critical`, or higher-urgency `general` examples.
This matches the current seed design and should be reviewed, but no synthetic text rewrite was
needed for the first G3 freeze-preparation boundary.

## Proposed Split

DEVELOPMENT IDs:

`T01`, `T02`, `T03`, `T04`, `T08`, `T09`, `T10`, `T12`, `T14`, `T16`, `T17`, `T19`, `T21`,
`T23`, `T27`

HELD_OUT IDs:

`T05`, `T06`, `T07`, `T11`, `T13`, `T15`, `T18`, `T20`, `T22`, `T24`, `T25`, `T26`, `T28`,
`T29`, `T30`

| Split check | Result |
|---|---:|
| DEV_COUNT | 15 |
| HELD_OUT_COUNT | 15 |
| DEV_HELDOUT_INTERSECTION | 0 |
| COMPLETE_SPLIT_COVERAGE | PASS |
| T09 in DEV | PASS |
| T10 in DEV | PASS |

T09 and T10 are design fixtures explicitly referenced by the project specification and execution
plan. They are placed in DEVELOPMENT so future classifier prompt/design work can handle
multi-category review and null-urgency behavior before the final held-out run. They are not
treated as unseen final cases.

Split rationale: the exact stable ID lists were chosen from dataset and ground-truth coverage
only. No classifier behavior exists and no model predictions were used. Both splits contain all
four primary categories and all four non-null urgency labels where the dataset permits.

Held-out integrity rule: held-out labels exist in the repository so final evaluation can be
scored, but after supervisor freeze they must not be used for prompt improvement, classifier
tuning, threshold selection, or error-driven iteration. Held-out evaluation occurs only after
the model, classifier prompt, invalid-output policy, and threshold are frozen.

## Frozen Null-Urgency Metric Rule

STATUS = APPROVED

Primary urgency accuracy denominator: all tickets whose ground-truth `expected_urgency` is
non-null.

Tickets with `expected_urgency = null` are not treated as a fifth urgency class. Null-urgency
cases are reported separately as `NULL_URGENCY_HANDLING`, including explicit Ticket 10 reporting.

## Final Frozen SHA-256

These are the verified frozen SHA-256 values.

| Artifact | FROZEN_SHA256 |
|---|---|
| `data/support_tickets_seed.json` | `40901dbbc12ec559ca1b5fc257adb8b1a3406eac08caca66da970e323ff5d7b3` |
| `data/support_tickets_ground_truth.json` | `ef1a83c4a379065917bd4220f4db8eaed6ea3ada2715a4c31a6b1948d2075f81` |
| `data/support_tickets_split.json` | `c56860c4cdf337a9c7c1fa7b465fc2a2bde0703871ed2d3627987c822a798be2` |

Freeze manifest: `data/support_tickets_freeze_manifest.json`

Frozen data version: `g3-support-triage-dataset-v1`

## Supervisor Review Table

| ID | Origin | Exact text | Category | Secondary | Urgency | Split | Label status | Ambiguity flag | Rationale |
|---|---|---|---|---|---|---|---|---|---|
| T01 | supplied | I was charged twice for my subscription this month. I need this fixed immediately — I can't afford to have money taken from my account like this. | billing | null | high | DEV | externally supplied / approved interpretation | CLEAR | Duplicate charge and immediate financial concern. |
| T02 | supplied | Hi, just wondering if you offer student discounts? No rush. | billing | null | low | DEV | externally supplied / approved interpretation | CLEAR | Billing discount question with explicit no-rush wording. |
| T03 | supplied | The application crashes every time I try to export a report. I've tried reinstalling but the problem persists. This is blocking my entire team from closing month-end. | technical | null | critical | DEV | externally supplied / approved interpretation | CLEAR | Application crash blocks an entire team from month-end close. |
| T04 | supplied | I forgot my password and the reset email isn't arriving. I've checked spam. | account | null | medium | DEV | externally supplied / approved interpretation | CLEAR | Account access problem without critical scope or deadline. |
| T05 | supplied | Everything is down. None of our staff can log in. We have a client presentation in 2 hours. | technical | null | critical | HELD_OUT | externally supplied / approved interpretation | CLEAR | Broad login outage with near-term client presentation. |
| T06 | supplied | How do I change the email address on my account? | account | null | low | HELD_OUT | externally supplied / approved interpretation | CLEAR | Account maintenance question with no urgency signal. |
| T07 | supplied | I cancelled my subscription 3 weeks ago but I was still charged this month. I want a refund and I want to know why this happened. | billing | null | high | HELD_OUT | externally supplied / approved interpretation | CLEAR | Refund and incorrect post-cancellation charge. |
| T08 | supplied | The export feature is a bit slow sometimes. Not urgent, just flagging it. | technical | null | low | DEV | externally supplied / approved interpretation | CLEAR | Technical performance issue with explicit not-urgent wording. |
| T09 | supplied | I need to transfer my account to a different email address because I'm changing companies. I also need an invoice for the last 12 months for my accountant. | account | billing | medium | DEV | externally supplied / approved interpretation | CLEAR | Explicit account transfer plus separate invoice request; design fixture. |
| T10 | supplied | it doesnt work fix it | technical | null | null | DEV | externally supplied / approved interpretation | CLEAR | Vague technical problem with unknowable urgency; design fixture. |
| T11 | synthetic | Can you send me a copy of my latest invoice for renewal planning? | billing | null | low | HELD_OUT | proposed pending supervisor approval | CLEAR | Invoice copy request for planning, no deadline or impact. |
| T12 | synthetic | Our payment method expires tomorrow and the portal will not save the replacement card. | billing | null | high | DEV | proposed pending supervisor approval | CLEAR | Payment method issue with tomorrow deadline; portal detail supports billing context rather than a second issue. |
| T13 | synthetic | The dashboard loads, but every chart shows blank data after this morning's update. | technical | null | medium | HELD_OUT | proposed pending supervisor approval | CLEAR | Product data-display defect after update with operational impact but no deadline. |
| T14 | synthetic | None of our users can access the service and our support desk is receiving calls from every branch. | technical | null | critical | DEV | proposed pending supervisor approval | CLEAR | Broad service access outage affecting every branch. |
| T15 | synthetic | Please help me update the display name shown on my account profile. | account | null | low | HELD_OUT | proposed pending supervisor approval | CLEAR | Routine account profile maintenance. |
| T16 | synthetic | A teammate left the company and I need their admin access removed today. | account | null | high | DEV | proposed pending supervisor approval | CLEAR | Account/admin access removal with same-day security timing. |
| T17 | synthetic | Where can I find your service hours during public holidays? | general | null | low | DEV | proposed pending supervisor approval | CLEAR | General informational support-hours question. |
| T18 | synthetic | I have feedback about the new menu layout; it is confusing but not blocking my work. | general | null | low | HELD_OUT | proposed pending supervisor approval | CLEAR | General product feedback with explicit non-blocking impact. |
| T19 | synthetic | My receipt shows the wrong billing address and I cannot edit the organization profile. | billing | account | medium | DEV | proposed pending supervisor approval | CLEAR | Wrong receipt billing address plus separate profile-edit account issue. |
| T20 | synthetic | The login page says my account is locked after one failed attempt. | account | null | medium | HELD_OUT | proposed pending supervisor approval | CLEAR | Account lockout/access issue without broader outage signal. |
| T21 | synthetic | Something looks wrong in my workspace. | technical | null | null | DEV | supervisor-approved frozen label | CLEAR - SUPERVISOR_APPROVED | Supervisor approved `technical` / `null` / `null`; urgency remains intentionally unknowable. |
| T22 | synthetic | A scheduled report did not run overnight and executives need the numbers before the morning review. | technical | null | high | HELD_OUT | proposed pending supervisor approval | CLEAR | Report failure with executive deadline before morning review. |
| T23 | synthetic | I was downgraded to the free plan even though the annual subscription is active. | account | billing | medium | DEV | proposed pending supervisor approval | CLEAR | Account plan state conflicts with active paid subscription. |
| T24 | synthetic | Please explain the difference between monthly and annual billing. | billing | null | low | HELD_OUT | proposed pending supervisor approval | CLEAR | Billing information question with no urgency signal. |
| T25 | synthetic | The mobile app freezes when I attach a file larger than 10 MB. | technical | null | medium | HELD_OUT | proposed pending supervisor approval | CLEAR | Reproducible mobile defect with limited but real functionality impact. |
| T26 | synthetic | My invitation link expired before I could finish setting up the account. | account | null | medium | HELD_OUT | proposed pending supervisor approval | CLEAR | Account onboarding access issue without broad outage or deadline. |
| T27 | synthetic | Can someone call me about partnership options? | general | null | low | DEV | proposed pending supervisor approval | CLEAR | General business inquiry outside billing/technical/account support. |
| T28 | synthetic | We are being billed for seats that were removed last week, and the user list now shows duplicate inactive accounts. | billing | account | medium | HELD_OUT | proposed pending supervisor approval | CLEAR | Billing for removed seats plus separate duplicate inactive account list issue. |
| T29 | synthetic | Exported CSV files contain garbled characters for every customer name with an accent mark. | technical | null | medium | HELD_OUT | proposed pending supervisor approval | CLEAR | Data export encoding defect with recurring data-quality impact. |
| T30 | synthetic | Is there a status page where I can check incidents before opening a ticket? | general | null | low | HELD_OUT | proposed pending supervisor approval | CLEAR | General self-service/status-page question. |

Label-review flags: 0. Prior review flag `T21` was resolved by supervisor approval.

## Review Chronology

1. Initial G3 preparation created candidate labels, split, hashes, and review table.
2. Supervisor reviewed and approved all labels and the exact split in the second G3 execution
   package.
3. The three approved artifact hashes were reverified before classifier implementation work.
4. Dataset, ground truth, split, and null-urgency metric rule are now frozen as
   `g3-support-triage-dataset-v1`.
