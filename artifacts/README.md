# Artifacts Index

This index organizes evidence by the original engineer milestones. Historical files are
preserved for provenance; final reviewer-facing documents use milestone-oriented names.

## Milestone 1

- Agent decision flow: [docs/AGENT_DECISION_FLOW.md](../docs/AGENT_DECISION_FLOW.md)
- Pipeline taxonomy: [docs/SUPPORT_TRIAGE_TAXONOMY.md](../docs/SUPPORT_TRIAGE_TAXONOMY.md)
- Sample/frozen ticket dataset: [data/support_tickets_seed.json](../data/support_tickets_seed.json)
- Frozen ground truth: [data/support_tickets_ground_truth.json](../data/support_tickets_ground_truth.json)
- Frozen DEV/HELD-OUT split: [data/support_tickets_split.json](../data/support_tickets_split.json)
- Dataset freeze manifest: [data/support_tickets_freeze_manifest.json](../data/support_tickets_freeze_manifest.json)
- Dataset size: 30 tickets total; T01-T10 preserve the engineer-supplied cases, with 20
  synthetic additions, 15 DEV tickets, and 15 HELD-OUT tickets.

## Milestone 2

- Callable HR policy Q&A evidence: [milestone_4_part_a_end_to_end_evidence.md](milestone_4_part_a_end_to_end_evidence.md)
- Platform and Knowledge Base provenance: [platform_validation_evidence.md](platform_validation_evidence.md)

## Milestone 3

- Isolated IT Request and Booking Flow evidence: [milestone_4_part_a_end_to_end_evidence.md](milestone_4_part_a_end_to_end_evidence.md)
- Production Flows: [flows/it_request_flow.py](../flows/it_request_flow.py), [flows/orientation_booking_flow.py](../flows/orientation_booking_flow.py)

## Milestone 4

- Complete Part A end-to-end Agent evidence: [milestone_4_part_a_end_to_end_evidence.md](milestone_4_part_a_end_to_end_evidence.md)

## Milestone 5

- Dataset freeze: [milestone_5_classifier_dataset_freeze_evidence.md](milestone_5_classifier_dataset_freeze_evidence.md)
- Classifier development and threshold decision: [milestone_5_classifier_evidence.md](milestone_5_classifier_evidence.md)

## Milestone 6

- Routing and Pipeline implementation: [flows/support_triage_flow.py](../flows/support_triage_flow.py)
- Draft-quality evidence: [milestone_6_draft_quality_review.md](milestone_6_draft_quality_review.md)
- Human Review and auto-route evidence: [milestone_8_evaluation_evidence.md](milestone_8_evaluation_evidence.md)

## Milestone 7

- Failure-mode evidence: [milestone_7_failure_mode_evidence.md](milestone_7_failure_mode_evidence.md)
- Final failure report: [FAILURE_MODE_REPORT.md](../FAILURE_MODE_REPORT.md)

## Milestone 8

- Final evaluation evidence: [milestone_8_evaluation_evidence.md](milestone_8_evaluation_evidence.md)
- Agent autonomy/reflection: [milestone_8_agent_vs_pipeline_reflection.md](milestone_8_agent_vs_pipeline_reflection.md)
- Final evaluation report: [EVALUATION_REPORT.md](../EVALUATION_REPORT.md)
- Agent-vs-Pipeline report: [AGENT_VS_PIPELINE.md](../AGENT_VS_PIPELINE.md)

## Final Acceptance

- Acceptance traceability: [final_acceptance_traceability.md](final_acceptance_traceability.md)
- Final remote demo evidence: [final_remote_demo_evidence.md](final_remote_demo_evidence.md)
- Historical code-freeze manifest: [code_freeze_manifest.json](code_freeze_manifest.json)
- Final delivery manifest: [final_delivery_manifest.json](final_delivery_manifest.json)

## Historical / Provenance Evidence

- Development history ledger: [development_history/PROJECT_EVIDENCE_LEDGER.md](development_history/PROJECT_EVIDENCE_LEDGER.md)
- Historical technical specification: [development_history/PROJECT_SPEC_HISTORY.md](development_history/PROJECT_SPEC_HISTORY.md)
- Raw HR policy evaluation outputs: [evaluations/hr_policy/](evaluations/hr_policy/)
- Raw support-triage evaluation outputs: [evaluations/support_triage/](evaluations/support_triage/)
- Model-selection evidence: [model_selection_smoke.json](model_selection_smoke.json), [model_selection_confirmation.json](model_selection_confirmation.json)
- DEV v1 baseline and v2 comparison provenance: [milestone_5_classifier_evidence.md](milestone_5_classifier_evidence.md)
