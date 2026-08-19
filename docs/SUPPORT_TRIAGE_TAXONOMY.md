# Support Triage Taxonomy

This document is the Milestone 1 written Pipeline taxonomy deliverable for Part B.

## Classification Schema

Categories are closed:

- `billing`
- `technical`
- `account`
- `general`

Urgency labels are closed:

- `low`
- `medium`
- `high`
- `critical`

`urgency = null` is allowed only when urgency is genuinely unknowable from the ticket text. It is
not a fifth urgency label.

Confidence is a number from `0.0` through `1.0`.

Selected threshold: `0.80`.

## Human Review Rules

Human Review is required when any of these conditions is true:

- classifier confidence is below `0.80`;
- `secondary_category` is present;
- `urgency` is null;
- classifier output is invalid after bounded attempts;
- classifier execution fails;
- category/urgency has no supported route.

Drafter failure after a valid automatic route becomes terminal status `draft_failed`. It does
not create a new Human Review trigger and does not change the routing decision.

## Routing Table

| Category | Urgency | Assigned team | SLA |
|---|---|---|---|
| billing | critical | Billing — Senior | 1 hour |
| billing | high | Billing — Standard | 4 hours |
| billing | medium | Billing — Standard | 1 business day |
| billing | low | Billing — Standard | 3 business days |
| technical | critical | Engineering — On-call | 30 minutes |
| technical | high | Engineering — Support | 2 hours |
| technical | medium | Engineering — Support | 1 business day |
| technical | low | Engineering — Backlog | 5 business days |
| account | high | Customer Success | 4 hours |
| account | medium | Customer Success | 1 business day |
| account | low | Customer Success | 3 business days |
| general | low/medium/high/critical | Customer Success | 2 business days |
| human review | N/A | Triage — Human | Immediate |

There is no Account + Critical automatic route. Account + Critical is an unsupported route and
must be human-contained as `Triage — Human` / `Immediate`.

## Required Edge Cases

- Multi-category tickets use `secondary_category` and require Human Review.
- Very short/vague tickets may use `urgency = null` and require Human Review.
- Unsupported route combinations must never silently route.
- Every terminal path must return a structured output record.

## Structured Output Summary

Terminal records include the ticket reference, normalized classification, validation status,
review requirement, review reasons, assigned team/SLA when applicable, draft status, telemetry
where available, and final status.
