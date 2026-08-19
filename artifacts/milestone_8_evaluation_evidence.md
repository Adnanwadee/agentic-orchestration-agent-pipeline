# Milestone 8 — Evaluation Evidence

Status: MILESTONE_8_EVALUATION_EVIDENCE=PASS

Derived artifact:
`artifacts/evaluations/support_triage/full30_frozen_combined.json`

This is a derived reporting artifact only. No DEV, HELD-OUT, drafter, classifier, watsonx.ai, or
remote Orchestrate execution was performed while creating it.

## Source Artifacts

Canonical DEV:
`artifacts/evaluations/support_triage/dev_initial/20260818T002957.432847Z/development_results.json`

DEV SHA-256:
`9476cb261888adb4abdb2fdb65d52daf7960377ee4efac0913c4388c9ce1c295`

Selection reason: it is the only stored DEV artifact matching the frozen v2 classifier prompt,
selected model, exact 15 development IDs, frozen split hashes, and zero held-out IDs.

Canonical HELD-OUT:
`artifacts/evaluations/support_triage/held_out_final/20260818T031003.013996Z/heldout_results.json`

HELD-OUT SHA-256:
`91e767b936272cd3363f46006b5f24f9862e4ae9131ce5717bdda9180a924584`

Expected HELD-OUT SHA-256 matched: PASS.

Full30 derived SHA-256:
`0b7d862555c288473a3d1fb8ef6c10fc3f5c27b8bf831ca344f6789de431a1b1`

## Integrity

- TOTAL_RECORDS=30
- UNIQUE_IDS=30
- DEV_COUNT=15
- HELD_OUT_COUNT=15
- OVERLAP=0
- DROPPED=0
- DUPLICATES=0
- Every record structured: PASS

DEV source records are classifier-only. For DEV routing metrics, G4 deterministically projects
the stored classifier outputs through the frozen review/routing policy. It does not invent DEV
draft text or drafter token usage. Auto-route correctness uses approved frozen v3 manual
draft-quality evidence for DEV auto-route candidates and recorded draft telemetry for held-out
auto-routed records.

## Metrics

- Category accuracy: `27/30 = 90.00%` => PASS against `80%`.
- Urgency accuracy: `25/28 = 89.29%` => PASS against `75%`.
- Urgency denominator excludes ground-truth null urgency.
- Null-urgency handling: T10 and T21 were both predicted with urgency `null` and sent to human review.
- Structured-output rate: `30/30 = 100.00%`.
- Human-review rate: `10/30 = 33.33%`.
- Auto-route rate: `20/30 = 66.67%`.
- Draft-failed rate: `0/30 = 0.00%`.
- Auto-route correctness: `18/20 = 90.00%`.

Auto-route correctness definition: for records with reporting status `auto_routed`, primary
category must match ground truth, urgency must match ground truth where expected urgency is
non-null, deterministic assigned team/SLA must match the authoritative route, and draft path
must be valid by recorded held-out draft telemetry or approved frozen v3 manual draft-quality
evidence for classifier-only DEV records.

## Telemetry

Classifier recorded telemetry:

- Calls with token usage: `30`
- Prompt tokens: `19784`
- Completion tokens: `1687`
- Total tokens: `21471`
- Mean latency seconds: `0.9127859199730058`
- Median latency seconds: `0.7984469500370324`
- P95 latency seconds: `1.5974319597939028`

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

## Operational Estimate

Official pricing source: IBM watsonx.ai Pricing,
`https://www.ibm.com/products/watsonx-ai/pricing`, accessed `2026-08-18`.

Model: `meta-llama/llama-4-maverick-17b-128e-instruct-fp8`.

Indicative public rates used:

- Input: `USD 0.371` per `1,000,000` input tokens.
- Output: `USD 1.484` per `1,000,000` output tokens.
- Equivalent: `USD 0.000371` per `1,000` input tokens.
- Equivalent: `USD 0.001484` per `1,000` output tokens.

At `1000` incoming tickets/day:

- Expected classifier calls/day: `1000`
- Expected drafter calls/day from observed auto-route rate: `666.67`
- Expected human-review tickets/day: `333.33`
- Estimated classifier tokens/day: `715700`
- Estimated drafter tokens/day from recorded held-out drafter average: `190944.44`
- Classifier model-inference cost/ticket: `0.0003281124 USD`
- Drafter model-inference cost/actual call: `0.00012035858333333334 USD`
- Expected combined model-inference cost/ticket: `0.00040835145555555557 USD`
- Expected combined model-inference cost/1000 tickets: `0.4083514555555556 USD`

Dollar-cost status: ESTIMATED_FROM_OFFICIAL_IBM_PUBLIC_RATE.

Formula:

`model_inference_cost = input_tokens / 1,000,000 * 0.371 + output_tokens / 1,000,000 * 1.484`

Cost limitations: this is model-inference token cost only. It excludes fixed plan charges,
Orchestrate charges, COS/storage, networking, human-review labor, taxes/duties, and
account-specific costs. Public pricing is indicative and may vary by locale, account, and
offering.

## Frozen Integrity

- Model: `meta-llama/llama-4-maverick-17b-128e-instruct-fp8`
- Classifier prompt: `support-triage-classifier-v2`
- Classifier prompt SHA-256: `a78f13a71cb344429502ca2aeb0b36281608cfbea6c45c6bb509b678e3d3e9b6`
- Classifier repair SHA-256: `b55bf893bba9e0373d70a4f839741b46ebacd82c1da94b622377b465e052b39b`
- Confidence threshold: `0.80`
- Drafter prompt: `support-triage-drafter-v3`
- Drafter prompt SHA-256: `80fc2ccaa4a0f14ec918a6324140b3da074388ab1f1a61d19e16556d9b8ddc23`
