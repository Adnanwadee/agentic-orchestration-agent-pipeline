# Final Remote Demonstration Evidence

Status: FINAL_REMOTE_DEMO=PASS

Date: 2026-08-19

Execution owner: MANUAL supervisor. Codex did not rerun the demo, call watsonx.ai, invoke
Orchestrate, rerun DEV, or rerun HELD-OUT.

Evidence provenance: supervisor-supplied project-chat/manual demonstration evidence. Screenshots
were directly reviewed by the supervisor; no repository screenshot image files are claimed here.

## Part A Final End-To-End Demo

Target: `hr_onboarding_agent`

One fresh conversational session covered the required sequence.

### A1. Policy Q&A

User asked: `What is the annual leave policy for a full-time employee?`

Observed:

- `hr_policy_knowledge_base` was actually invoked.
- Query targeted annual leave policy for full-time employees.
- `leave-policy.txt` was retrieved.
- Grounded answer stated 21 working days of paid annual leave per calendar year.
- Supporting policy-source UI was visible.

Result: PASS

### A2. IT Request

User asked: `I need Slack and GitHub access. My role is QA Engineer.`

Observed:

- Agent requested only Employee name.
- Agent did not re-request employee role.
- Agent did not re-request required systems.
- User supplied `Final Demo User`.
- Review displayed Employee name `Final Demo User`, Employee role `QA Engineer`, and Required
  systems `Slack, Github`.
- Explicit confirmation was `Yes`.
- Observed result: `{"status":"submitted","persisted":true}`.

Result: PASS

### A3. Orientation Booking

Same conversation.

User asked: `I also want to book my orientation session.`

Observed slots exactly:

- `Monday 09:00-10:00`
- `Wednesday 13:00-14:00`
- `Thursday 15:00-16:00`

User selected `Wednesday 13:00-14:00`. Review displayed the selected slot. Explicit confirmation
was `Yes`. Observed result: `{"status":"booked","persisted":true}`.

Result: PASS

### A4. Completion / Exit

User said: `Thanks, that's everything. I'm done.`

Observed:

- Agent clearly summarized that the IT request was submitted.
- Orientation session was booked.
- Agent provided a natural conversational exit.
- No further side effect occurred.

Result: PASS

PART_A_FINAL_REMOTE_DEMO=PASS

## Part B Automatic Route Final Demo

Target: `support_triage_flow_test_agent`

Tool: `support_triage`

Authoritative screenshot-backed run: `FINAL-DEMO-AUTO-002`

Flow instance: `785a3e09-bf51-47fc-8f31-fdccc489f01c`

Ticket text:

`Since this morning, the dashboard export returns an error every time we try to download a report. The rest of the application is working.`

Observed:

- `classification_valid=true`
- `category=technical`
- `urgency=high`
- `confidence=0.9`
- `review_required=false`
- `review_reasons=[]`
- `assigned_team="Engineering — Support"`
- `sla="2 hours"`
- `status="auto_routed"`
- `draft_validation_status="valid"`
- `draft_attempt_count=1`

Draft response:

`Thank you for reaching out about dashboard export error. Assigned team: Engineering — Support. SLA target: 2 hours.`

The draft visibly refers to the actual dashboard-export issue.

Result: PASS

PART_B_AUTO_FINAL_REMOTE_DEMO=PASS

Note: an earlier successful `FINAL-DEMO-AUTO-001` run had equivalent behavior, but the supervisor
did not retain its screenshot. `FINAL-DEMO-AUTO-002` is the authoritative screenshot-backed
final-demo evidence.

## Part B Human Review Final Demo

Target: `support_triage_flow_test_agent`

Tool: `support_triage`

Ticket ID: `FINAL-DEMO-REVIEW-001`

Flow instance: `ff0b456e-915a-4347-9a37-a1c3f974a5f5`

Ticket text:

`I cannot access my account after resetting my password, and my latest invoice also contains a duplicate charge.`

Observed:

- `classification_valid=true`
- `category=account`
- `secondary_category=billing`
- `urgency=medium`
- `confidence=0.8`
- `review_required=true`
- `review_reasons=["secondary_category_present"]`
- `assigned_team="Triage — Human"`
- `sla="Immediate"`
- `status="human_review"`
- No automatic customer draft was produced.

Result: PASS

PART_B_REVIEW_FINAL_REMOTE_DEMO=PASS

## Screenshot Evidence Approval

Supervisor directly reviewed screenshots showing:

1. Part A policy Knowledge Base invocation and grounded answer.
2. Part A IT missing-only collection.
3. Part A IT review, confirmation, and persisted submission.
4. Part A orientation approved-slot selection, review, confirmation, and persisted booking.
5. Part A clean completion/exit.
6. Part B automatic route `FINAL-DEMO-AUTO-002` with `support_triage` tool input and structured
   automatic-route output.
7. Part B human-review `FINAL-DEMO-REVIEW-001` with `support_triage` tool input and structured
   human-review output.

No API keys, bearer tokens, credentials, or sensitive real personal data were visible in the
reviewed screenshots.

SCREENSHOT_DEMO_EVIDENCE=APPROVED

## Scope Qualification

The final-demo tickets are synthetic MANUAL G5 demonstration cases. They are not DEV or
HELD-OUT evaluation cases and must not be counted as model-quality tuning or final evaluation
records.

FINAL_REMOTE_DEMO_OVERALL=PASS
