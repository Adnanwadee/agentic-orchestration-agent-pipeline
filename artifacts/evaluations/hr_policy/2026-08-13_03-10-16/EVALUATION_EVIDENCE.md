# HR Policy Knowledge Evaluation Evidence

Run directory: `artifacts/evaluations/hr_policy/2026-08-13_03-10-16`

Target Agent: `hr_onboarding_agent`

Environment:
- watsonx Orchestrate ADK: 2.13.0
- Langflow: 1.7.1
- Evaluation framework extra: `ibm-watsonx-orchestrate-evaluation-framework==1.5.2`
- Remote environment: `project2`
- Region: `eu-de`

## Execution

The IBM evaluator executed all 10 prepared HR policy cases from `evaluations/hr_policy/ground_truth`.

The ground truth uses text goals and does not define an expected Knowledge Base tool-call sequence:

```json
{"goals": {"summarize": []}}
```

The actual Agent invoked `hr_policy_knowledge_base` in the observed conversations. Because the reference trajectory has `Expected Tool Calls = 0.0` while actual Knowledge invocation occurred, generic tool/text/journey metrics are retained as observed values rather than rewritten or treated as the G2 Knowledge acceptance decision.

## IBM Metrics

- Runs: 1.0
- Orchestrate Agent Routing F1: 1.0
- Average Agent Response Time (s): 4.69
- Total Tool Calls: 1.0
- Expected Tool Calls: 0.0
- Knowledge Answer Relevancy: 0.92
- Average Document Retrieval Confidence: 0.68
- Knowledge Faithfulness: 1.00
- Retrieval Confidence: 0.51
- Keyword Match: 0.0
- Semantic Match: 0.2
- Text Match: 0.0
- Journey Success: 0.0
- Response Confidence: not exposed / not available in this run

No numeric Knowledge-confidence threshold is approved or inferred from these values.

## Internal 8+2 Audit

Supervisor audit of the actual conversations against the approved HR sources:

- Answerable cases grounded correctly: 8 / 8
- Unanswerable cases abstained correctly: 2 / 2
- Fabricated HR policy facts: 0

Internal bar result:

- Required grounded answerable: at least 7 / 8; observed 8 / 8
- Required unanswerable abstention: 2 / 2; observed 2 / 2
- Maximum fabricated HR policy facts: 0; observed 0

This is an internal engineering quality result, not an IBM metric.

## Observations

Case 02, annual-leave encashment: the final policy conclusion was grounded and correct: annual leave may not be encashed while employed except upon resignation or termination. The first response contained a minor unnecessary abstention phrase before the explicit supported negative rule. Factual grounding and safety passed; this is not a production blocker and no Agent change was made for it.

Case 09, pet insurance: the correct abstention occurred early. The simulated evaluation user then entered an excessive polite goodbye/continuation loop, reaching approximately 30 total steps / 15 LLM steps. This is recorded as an evaluation-user termination/simulation observation, not an HR-policy correctness failure. No Agent change was made for it.

## Analyze Limitation

`orchestrate evaluations analyze -d <run-directory> --env-file .env` failed before producing analysis output with a Pydantic schema compatibility error for `ToolCallAndRoutingMetrics.text_match`: the analyzer expected enum-like values, while the new-pipeline artifact contained numeric `text_match = 0`.

IBM analyze CLI status: BLOCKED BY NEW-PIPELINE / ANALYZER SCHEMA COMPATIBILITY.

No legacy evaluation rerun was performed, and generated metrics were not edited to satisfy the analyzer.

## Artifact Sanitization

Durable IBM evidence retained:
- `summary_metrics.csv`
- `average_metrics.json`
- 10 per-case `*.metrics.json`
- 10 per-case `*.messages.json`
- 10 per-case `*.messages.analyze.json`
- 10 per-case metadata JSON files
- Per-case Knowledge Base retrieval evidence retained in `*.messages.analyze.json`
- `config.sanitized.yml`

Removed:
- raw token-bearing `config.yml`
- repository-local `ibm_eval_2026-08-13_03-10-16.zip`
- transient `debug/evaluation_order.txt`

The sanitized config parses and removes `auth_config.token`. A recursive secret-shaped scan of this run directory passed after sanitization.

No Agent, Knowledge Base, ground-truth case, source document, or retrieval configuration change was made as a result of this evaluation.
