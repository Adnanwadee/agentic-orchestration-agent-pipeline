# Milestone 5 — Classifier Development and Threshold Evidence

## Initial DEV Baseline

Result artifact:
`artifacts/evaluations/support_triage/dev_initial/20260818T000438.946705Z/development_results.json`

Result artifact SHA-256:
`1329550aa43a85a6f1e1a1bc0db8ee34585c4b9d2d9ac068fd7da535af327c0f`

Dataset version:
`g3-support-triage-dataset-v1`

Model:
`meta-llama/llama-4-maverick-17b-128e-instruct-fp8`

Historical baseline prompt:
`support-triage-classifier-v1`

Historical baseline prompt SHA-256:
`5ae597bc3fe6af83df93c3b29f062a770186f5281ca27d1a046bd8e4ec689210`

Development IDs:
`T01`, `T02`, `T03`, `T04`, `T08`, `T09`, `T10`, `T12`, `T14`, `T16`, `T17`, `T19`, `T21`, `T23`, `T27`

Held-out exposure:
`0`

Baseline validity:

- 15 development records were produced.
- All 15 records had `validation_status=valid`.
- All 15 records had `attempt_count=1`.
- All 15 records had `error_code=null`.
- No repair attempt occurred.
- No DEV execution error occurred.

Baseline metrics recomputed from frozen DEV ground truth and predictions:

- Category: `13/15 = 86.67%`
- Urgency: `10/13 = 76.92%`
- Urgency denominator excludes ground-truth null urgency.
- T10 null urgency handling: PASS, valid classification with predicted urgency `null`.
- T21 null urgency handling: PASS, valid classification with predicted urgency `null`.

Primary-category errors:

- T02: expected `billing`, predicted `general`, confidence `0.9`.
- T21: expected `technical`, predicted `general`, confidence `0.5`.

Non-null urgency errors:

- T03: expected `critical`, predicted `high`, confidence `0.9`.
- T09: expected `medium`, predicted `low`, confidence `0.9`.
- T23: expected `medium`, predicted `high`, confidence `0.8`.

Secondary-category mismatches:

- T04: expected `null`, predicted `technical`.
- T12: expected `null`, predicted `technical`.

Secondary-category accuracy is not one of the externally required category/urgency acceptance
metrics, but it is recorded because non-null secondary category affects human-review rate.

## One Allowed Prompt Revision

The v1 baseline exceeded the minimum DEV numerical targets: category accuracy was above 80% and
urgency accuracy was above 75%. One classifier improvement is still justified because the baseline
included high-confidence semantic errors that later threshold calibration cannot prevent:

- T02 category error at confidence `0.9`.
- T03 urgency error at confidence `0.9`.

The later threshold candidates are only `0.50`, `0.60`, `0.70`, and `0.80`; threshold calibration
alone cannot catch predictions above `0.80`.

Implemented local prompt revision:
`support-triage-classifier-v2`

Prompt v2 SHA-256:
`a78f13a71cb344429502ca2aeb0b36281608cfbea6c45c6bb509b678e3d3e9b6`

Repair instruction remains unchanged:
`support-triage-classifier-repair-v1`

Repair instruction SHA-256:
`b55bf893bba9e0373d70a4f839741b46ebacd82c1da94b622377b465e052b39b`

The v2 revision adds only generic taxonomy definitions and a generic urgency rubric. It does not
include ticket IDs, exact evaluation ticket text, expected labels, DEV/held-out membership,
threshold selection, routing, drafting, dataset changes, split changes, model changes, schema
changes, retry-policy changes, or repair-policy changes.

ONE_ALLOWED_POST_DEV_IMPROVEMENT_CYCLE_USED=YES.

No second semantic classifier improvement may be made based on subsequent DEV results. If v2
performs worse, the supervisor may choose between already evaluated versions using approved
development evidence, but Codex must not create a v3 or perform another semantic tuning cycle.

Improved DEV evaluation:
COMPLETE.

## V2 Improved DEV Run

Result artifact:
`artifacts/evaluations/support_triage/dev_initial/20260818T002957.432847Z/development_results.json`

Result artifact SHA-256:
`9476cb261888adb4abdb2fdb65d52daf7960377ee4efac0913c4388c9ce1c295`

Model:
`meta-llama/llama-4-maverick-17b-128e-instruct-fp8`

Prompt:
`support-triage-classifier-v2`

Prompt SHA-256:
`a78f13a71cb344429502ca2aeb0b36281608cfbea6c45c6bb509b678e3d3e9b6`

Repair instruction:
`support-triage-classifier-repair-v1`

Repair instruction SHA-256:
`b55bf893bba9e0373d70a4f839741b46ebacd82c1da94b622377b465e052b39b`

Development IDs:
`T01`, `T02`, `T03`, `T04`, `T08`, `T09`, `T10`, `T12`, `T14`, `T16`, `T17`, `T19`, `T21`, `T23`, `T27`

Held-out exposure:
`0`

V2 validity:

- 15 development records were produced.
- All 15 records had `validation_status=valid`.
- All 15 records had `attempt_count=1`.
- All 15 records had `error_code=null`.
- No repair attempt occurred.
- No DEV execution error occurred.

V2 metrics recomputed from frozen DEV ground truth and predictions:

- Category: `12/15 = 80.00%`
- Urgency: `12/13 = 92.31%`
- Urgency denominator excludes ground-truth null urgency.
- T10 null urgency handling: PASS, valid classification with predicted urgency `null`.
- T21 null urgency handling: PASS, valid classification with predicted urgency `null`.

V2 primary-category errors:

- T02: expected `billing`, predicted `general`, confidence `0.9`.
- T21: expected `technical`, predicted `general`, confidence `0.5`.
- T23: expected `account`, predicted `billing`, confidence `0.9`.

V2 non-null urgency error:

- T23: expected `medium`, predicted `high`, confidence `0.9`.

V2 secondary-category mismatches:

- T04: expected `null`, predicted `technical`.
- T12: expected `null`, predicted `technical`.
- T23: expected `billing`, predicted `account`.

For T23, v2 identifies both account and billing domains but reverses the exact required primary
and secondary categories. That is exact structured-contract incorrectness even though both
semantic domains are present.

## V1 To V2 Prediction Changes

Changed classification fields or confidence values:

- T03: urgency changed from `high` to `critical`; frozen expected urgency is `critical`.
- T08: confidence changed from `0.8` to `0.9`; semantic labels otherwise unchanged.
- T09: urgency changed from `low` to `medium`; frozen expected urgency is `medium`.
- T23: category changed from `account` to `billing`; secondary_category changed from `billing`
  to `account`; confidence changed from `0.8` to `0.9`; urgency remained `high`; frozen expected
  is category `account`, secondary_category `billing`, urgency `medium`.

Reasoning text changed for all 15 DEV records; reasoning changes are not used as category,
urgency, threshold, routing, or drafting evidence.

## Raw V1 Versus V2 Comparison

| Measure | V1 | V2 | Delta |
|---|---:|---:|---:|
| Category accuracy | `13/15 = 86.67%` | `12/15 = 80.00%` | `-6.67 pp` |
| Urgency accuracy | `10/13 = 76.92%` | `12/13 = 92.31%` | `+15.38 pp` |
| Null-urgency handling | T10 PASS, T21 PASS | T10 PASS, T21 PASS | no change |
| Structured-validity rate | `15/15 = 100%` | `15/15 = 100%` | no change |
| Repair-attempt count | `0` | `0` | no change |
| Execution-error count | `0` | `0` | no change |

High-confidence semantic errors at confidence `>= 0.80`:

- V1: T02 category error, not review-protected at threshold `0.80`; T03 urgency under-escalation,
  not review-protected at threshold `0.80`; T09 urgency error, review-protected by non-null
  secondary_category; T23 urgency error, review-protected by non-null secondary_category.
- V2: T02 category error, not review-protected at threshold `0.80`; T23 category/urgency error,
  review-protected by non-null secondary_category.

V2 does not improve every metric. It regresses raw category accuracy to the minimum passing
boundary, but it improves raw urgency accuracy and removes the V1 high-confidence automatic-route
under-escalation on T03.

## Operational Threshold Analysis

Frozen review policy for this analysis: review when validation is invalid, confidence is below
the threshold using strict `<`, secondary_category is non-null, urgency is null, or the
category/urgency pair is the unsupported Account + Critical route. Auto-route classification
correctness is measured only as primary category and urgency matching frozen DEV ground truth.

### V1

| Threshold | Review IDs | Review Count/Rate | Auto IDs | Auto Count/Rate | Incorrect Auto IDs | Auto Exact Correctness |
|---:|---|---:|---|---:|---|---:|
| `0.50` | T04, T09, T10, T12, T19, T21, T23 | `7/15 = 46.67%` | T01, T02, T03, T08, T14, T16, T17, T27 | `8/15 = 53.33%` | T02, T03 | `6/8 = 75.00%` |
| `0.60` | T04, T09, T10, T12, T19, T21, T23 | `7/15 = 46.67%` | T01, T02, T03, T08, T14, T16, T17, T27 | `8/15 = 53.33%` | T02, T03 | `6/8 = 75.00%` |
| `0.70` | T04, T09, T10, T12, T19, T21, T23 | `7/15 = 46.67%` | T01, T02, T03, T08, T14, T16, T17, T27 | `8/15 = 53.33%` | T02, T03 | `6/8 = 75.00%` |
| `0.80` | T04, T09, T10, T12, T19, T21, T23 | `7/15 = 46.67%` | T01, T02, T03, T08, T14, T16, T17, T27 | `8/15 = 53.33%` | T02, T03 | `6/8 = 75.00%` |

### V2

| Threshold | Review IDs | Review Count/Rate | Auto IDs | Auto Count/Rate | Incorrect Auto IDs | Auto Exact Correctness |
|---:|---|---:|---|---:|---|---:|
| `0.50` | T04, T09, T10, T12, T19, T21, T23 | `7/15 = 46.67%` | T01, T02, T03, T08, T14, T16, T17, T27 | `8/15 = 53.33%` | T02 | `7/8 = 87.50%` |
| `0.60` | T04, T09, T10, T12, T19, T21, T23 | `7/15 = 46.67%` | T01, T02, T03, T08, T14, T16, T17, T27 | `8/15 = 53.33%` | T02 | `7/8 = 87.50%` |
| `0.70` | T04, T09, T10, T12, T19, T21, T23 | `7/15 = 46.67%` | T01, T02, T03, T08, T14, T16, T17, T27 | `8/15 = 53.33%` | T02 | `7/8 = 87.50%` |
| `0.80` | T04, T09, T10, T12, T19, T21, T23 | `7/15 = 46.67%` | T01, T02, T03, T08, T14, T16, T17, T27 | `8/15 = 53.33%` | T02 | `7/8 = 87.50%` |

## Telemetry Comparison

| Measure | V1 | V2 |
|---|---:|---:|
| Total tokens | `6602` | `10747` |
| Mean tokens/ticket | `440.13` | `716.47` |
| Token change | baseline | `+62.78%` |
| Total observed model-call latency | `15.2930814s` | `14.9586676s` |
| Mean observed latency/ticket | `1.0195388s` | `0.9972445s` |

The latency difference is observational and noisy. The material token increase is retained as a
cost trade-off for later G4 cost analysis.

## Final Development Selection

Selected classifier prompt:
`support-triage-classifier-v2`

Selected classifier prompt SHA-256:
`a78f13a71cb344429502ca2aeb0b36281608cfbea6c45c6bb509b678e3d3e9b6`

Selection rationale: both v1 and v2 satisfy the DEVELOPMENT minimums. V1 has better raw category
accuracy (`86.67%` vs `80.00%`), but v2 has materially better urgency accuracy (`92.31%` vs
`76.92%`), preserves structured validity and null-urgency behavior, reduces incorrect auto-route
candidates from T02/T03 to T02 only, and removes the high-confidence automatic-route
under-escalation on T03. T23 is a v2 regression, but it is review-protected by non-null
secondary_category under all candidate thresholds. T02 remains the primary residual
auto-route-eligible semantic risk. V2's higher token usage is accepted as a documented cost
trade-off because the support-triage pipeline places high weight on urgency and automatic-routing
safety.

Selected confidence threshold:
`0.80`

Threshold rationale: for selected v2, all approved thresholds `0.50`, `0.60`, `0.70`, and `0.80`
are empirically tied on the measured DEVELOPMENT behavior: same review IDs, same auto-route IDs,
same incorrect auto-route ID, and same auto-route exact correctness. The highest tied approved
threshold is selected conservatively. This does not prove superiority on unseen held-out data.

Residual DEVELOPMENT risks:

- T02 remains an auto-route-eligible primary-category error at confidence `0.9`.
- V2 category accuracy is exactly at the minimum DEVELOPMENT boundary.
- T23 remains an exact primary/secondary reversal and urgency error, although review-protected.
- V2 token usage increased by `62.78%` versus v1 and must be carried into cost analysis.
- Held-out behavior remains unknown and must not be inferred from DEV evidence.
