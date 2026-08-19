# Evaluation Report


This report is generated from frozen evidence only. It does not recompute model predictions,
rerun DEV, rerun HELD-OUT, call watsonx.ai, or execute remote IBM actions.

## Evaluation Design

The support-triage evaluation measures whether the Pipeline can classify, review, route, draft
when allowed, and emit structured terminal records under frozen data and configuration.

The combined frozen 30-ticket evaluation/reporting view uses:

- DEV: stored classifier outputs plus deterministic frozen policy projection.
- HELD-OUT: stored one-time complete pipeline records.

It must not be described as "complete Pipeline executed on all 30 tickets."

## Dataset

- Total tickets: `30`
- Supplied tickets preserved: `T01` through `T10`
- Synthetic tickets: `20`
- Frozen dataset version: `g3-support-triage-dataset-v1`

Ground truth, split, and null-urgency metric rule were frozen before final held-out evaluation.

Frozen split:

- DEV: `15`
- HELD-OUT: `15`
- DEV/HELD-OUT overlap: `0`

Canonical frozen artifacts:

- `data/support_tickets_seed.json`
- `data/support_tickets_ground_truth.json`
- `data/support_tickets_split.json`
- `data/support_tickets_freeze_manifest.json`

## Source Artifacts

Canonical DEV source:

- `artifacts/evaluations/support_triage/dev_initial/20260818T002957.432847Z/development_results.json`
- SHA-256: `9476cb261888adb4abdb2fdb65d52daf7960377ee4efac0913c4388c9ce1c295`

Canonical HELD-OUT source:

- `artifacts/evaluations/support_triage/held_out_final/20260818T031003.013996Z/heldout_results.json`
- SHA-256: `91e767b936272cd3363f46006b5f24f9862e4ae9131ce5717bdda9180a924584`

Derived reporting artifact:

- `artifacts/evaluations/support_triage/full30_frozen_combined.json`
- SHA-256: `0b7d862555c288473a3d1fb8ef6c10fc3f5c27b8bf831ca344f6789de431a1b1`

## Final Metrics

| Metric | Result | Status |
|---|---:|---|
| Category accuracy | `27/30 = 90.00%` | PASS against `80%` target |
| Urgency accuracy | `25/28 = 89.29%` | PASS against `75%` target |
| Structured output | `30/30 = 100.00%` | PASS |
| Human review | `10/30 = 33.33%` | Reported |
| Auto-route | `20/30 = 66.67%` | Reported |
| Auto-route correctness | `18/20 = 90.00%` | Reported |
| Draft-failed rate | `0/30 = 0.00%` | Reported |

Urgency denominator: tickets whose frozen ground-truth urgency is `null` are excluded from
primary urgency accuracy and reported separately. T10 and T21 were both predicted with urgency
`null` and sent to human review.

Auto-route correctness requires correct primary category, correct non-null urgency, correct
deterministic team/SLA, and valid draft path evidence.

## Threshold Justification

Selected confidence threshold: `0.80`.

The threshold was selected empirically from approved candidates `0.50`, `0.60`, `0.70`, and
`0.80` before held-out evaluation. For selected classifier v2, the candidates were tied on DEV
review IDs, auto-route IDs, incorrect auto-route ID, and auto-route exact correctness. The
highest tied threshold was selected conservatively. This does not prove superiority on unseen
held-out data.

## Classifier Telemetry

Classifier recorded telemetry:

- Calls with token usage: `30`
- Prompt tokens: `19784`
- Completion tokens: `1687`
- Total tokens: `21471`
- Mean latency seconds: `0.9127859199730058`
- Median latency seconds: `0.7984469500370324`
- P95 latency seconds: `1.5974319597939028`

## Drafter Telemetry

Drafter recorded telemetry, held-out actual calls only:

- Calls with token usage: `12`
- Prompt tokens: `3285`
- Completion tokens: `152`
- Total tokens: `3437`
- Mean latency seconds: `0.4832684666228791`
- Median latency seconds: `0.46698354999534786`
- P95 latency seconds: `0.5870209448738024`

Latency is recorded classifier/drafter model-tool telemetry only. It is not full end-to-end
Orchestrate Flow latency.

## Pricing Assumption And Cost

Pricing source: IBM watsonx.ai public pricing, accessed `2026-08-18`.

Model: `meta-llama/llama-4-maverick-17b-128e-instruct-fp8`.

Rates used:

- Input: USD `0.371` / 1,000,000 tokens
- Output: USD `1.484` / 1,000,000 tokens

Cost results:

- Classifier/ticket: approximately USD `0.0003281124`
- Drafter/actual call: approximately USD `0.0001203586`
- Expected combined inference cost/incoming ticket: approximately USD `0.00040835146`
- 1000 tickets/day: approximately USD `0.40835146` per day

Cost qualification: model-inference token cost only. The estimate excludes fixed plan/platform
charges, Orchestrate charges, COS/storage, networking, human-review labor, taxes/duties, and
account-specific costs.

## Draft-Quality Evaluation

Manual draft-quality run 3 approved drafter v3 on 4/4 representative synthetic non-dataset
cases. The final drafter prompt SHA-256 is
`80fc2ccaa4a0f14ec918a6324140b3da074388ab1f1a61d19e16556d9b8ddc23`.

Draft-quality qualification: a controlled fake-model probe showed that structural validation can
accept a generic problem summary. Accepted v3 outputs were personalized, but deterministic
validation does not independently compare the summary to the ticket text.

## Failure Analysis Summary

Evaluation results are interpreted with the Milestone 7 failure-mode evidence:

- Low confidence, secondary category, null urgency, invalid classifier output, execution error,
  and unsupported routes are human-contained.
- Drafter failures do not change routing policy.
- Generic-draft and loop-pressure output-hygiene limitations remain documented.

## Residual Limitations

- DEV uses stored classifier outputs plus deterministic projection, not complete pipeline
  execution.
- HELD-OUT is one-time complete pipeline evidence and must not be used for further tuning.
- Cost is model-inference token cost only.
- Latency is model/tool telemetry only.
- Draft semantic specificity is not deterministically guaranteed by structural validation.

## Final Acceptance Result

EVALUATION_ACCEPTANCE=PASS_WITH_QUALIFICATION.

The numerical category and urgency targets are met, structured-output coverage is complete, and
review/routing/cost/telemetry evidence is recorded with the required qualifications.
