from pathlib import Path
import subprocess
import sys

import pytest
import yaml


AGENT_PATH = Path("agents/hr_onboarding_agent.yaml")
EXPECTED_TOOLS = ["it_request_flow", "orientation_booking_flow"]
EXPECTED_KNOWLEDGE_BASES = ["hr_policy_knowledge_base"]
FORBIDDEN_TOOLS = {
    "persist_it_request",
    "persist_orientation_booking",
    "support_triage",
    "g1b_prompt_node_spike",
    "g1b_user_activity_spike",
    "it_request_flow_test_agent",
    "orientation_booking_flow_test_agent",
}

CAPABILITY_SELECTION_CASES = [
    {
        "prompt": "What does the IT access policy say about requesting Jira?",
        "expected_capability": "POLICY KNOWLEDGE",
        "expected_action_flow": None,
    },
    {
        "prompt": "I need Jira access.",
        "expected_capability": "IT REQUEST",
        "expected_action_flow": "it_request_flow",
    },
    {
        "prompt": "Please request Slack and GitHub access for me.",
        "expected_capability": "IT REQUEST",
        "expected_action_flow": "it_request_flow",
    },
    {
        "prompt": "What happens during new-hire orientation?",
        "expected_capability": "POLICY KNOWLEDGE",
        "expected_action_flow": None,
    },
    {
        "prompt": "I want to book my orientation.",
        "expected_capability": "ORIENTATION BOOKING",
        "expected_action_flow": "orientation_booking_flow",
    },
    {
        "prompt": "Can you help me with Jira?",
        "expected_capability": "CLARIFY",
        "expected_action_flow": None,
    },
    {
        "prompt": "Book me a flight.",
        "expected_capability": "DECLINE",
        "expected_action_flow": None,
    },
]

IT_PREFILL_HANDOFF_CASES = [
    {
        "prompt": "I need an IT access request.",
        "known_fields": {},
        "expected_missing_fields": {"employee_name", "employee_role", "required_systems"},
    },
    {
        "prompt": "I need Slack and GitHub access. My role is QA Engineer.",
        "known_fields": {
            "employee_role": "QA Engineer",
            "required_systems": "Slack, GitHub",
        },
        "expected_missing_fields": {"employee_name"},
    },
    {
        "prompt": "My name is Alex Doe, I'm a QA Engineer, and I need Slack and GitHub access.",
        "known_fields": {
            "employee_name": "Alex Doe",
            "employee_role": "QA Engineer",
            "required_systems": "Slack, GitHub",
        },
        "expected_missing_fields": set(),
    },
    {
        "prompt": "Please request Jira access for me.",
        "known_fields": {"required_systems": "Jira"},
        "expected_missing_fields": {"employee_name", "employee_role"},
    },
]


def load_agent_spec():
    return yaml.safe_load(AGENT_PATH.read_text(encoding="utf-8"))


def guideline_text():
    guideline = load_agent_spec()["guidelines"][0]
    return f"{guideline['condition']} {guideline['action']}".lower()


def instructions_text():
    return load_agent_spec()["instructions"].lower()


def serialized_agent_text():
    return AGENT_PATH.read_text(encoding="utf-8").lower()


def test_agent_architecture_contract_is_final_part_a_agent():
    spec = load_agent_spec()

    assert spec["spec_version"] == "v1"
    assert spec["name"] == "hr_onboarding_agent"
    assert spec["kind"] == "native"
    assert spec["style"] == "react_intrinsic"
    assert spec["llm"] == "watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8"
    assert spec["knowledge_base"] == EXPECTED_KNOWLEDGE_BASES
    assert spec["tools"] == EXPECTED_TOOLS
    assert spec["collaborators"] == []


def test_agent_uses_installed_adk_agentspec_schema():
    script = (
        "from pathlib import Path; import yaml; "
        "from ibm_watsonx_orchestrate.agent_builder.agents import AgentSpec; "
        "spec = yaml.safe_load(Path('agents/hr_onboarding_agent.yaml').read_text(encoding='utf-8')); "
        "validated = AgentSpec.model_validate(spec); "
        "print(validated.name); "
        "print(validated.style.value); "
        "print(validated.llm); "
        "print(','.join(validated.tools)); "
        "print(','.join(validated.knowledge_base)); "
        "print(validated.collaborators)"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()

    assert lines == [
        "hr_onboarding_agent",
        "react_intrinsic",
        "watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8",
        ",".join(EXPECTED_TOOLS),
        ",".join(EXPECTED_KNOWLEDGE_BASES),
        "[]",
    ]


def test_agent_tools_are_exact_and_do_not_expose_persistence_part_b_or_test_harnesses():
    spec = load_agent_spec()
    serialized = serialized_agent_text()

    assert set(spec["tools"]) == set(EXPECTED_TOOLS)
    assert len(spec["tools"]) == len(EXPECTED_TOOLS)
    assert not FORBIDDEN_TOOLS.intersection(spec["tools"])
    for forbidden in FORBIDDEN_TOOLS:
        assert forbidden not in serialized
    assert "collaborators: []" in AGENT_PATH.read_text(encoding="utf-8")


def test_stale_unwired_configuration_language_is_absent():
    serialized = serialized_agent_text()

    assert "no it request workflow or tool is wired" not in serialized
    assert "no orientation booking workflow or tool is wired" not in serialized
    assert "unavailable tools" not in serialized
    assert "it_request_flow is wired" in serialized
    assert "orientation_booking_flow is wired" in serialized


def test_agent_uses_structured_guideline_for_policy_evidence_contract():
    spec = load_agent_spec()

    assert spec["instructions"].count("evidence-state policy answering guideline") == 1
    assert len(spec["guidelines"]) == 1
    assert set(spec["guidelines"][0]) == {"display_name", "condition", "action"}
    assert spec["guidelines"][0]["display_name"] == "Evidence-state policy answers"


def test_agent_guideline_expresses_all_three_evidence_states():
    text = guideline_text()

    assert "explicit positive evidence" in text
    assert "grounded positive answer" in text
    assert "explicit negative evidence" in text
    assert "grounded negative answer" in text
    assert "if neither is explicit" in text
    assert "not enough approved policy information" in text


def test_agent_guideline_disallows_unsupported_negative_policy_inference():
    text = guideline_text()

    assert "exact requested policy relationship" in text
    assert "evidence is missing" in text
    assert "broadly related" in text
    assert "different subject, beneficiary, scope" in text
    assert "reimbursement type, coverage type, eligibility condition" in text
    assert "do not convert silence or related-but-insufficient evidence into a negative" in text


def test_agent_guideline_preserves_supported_negative_answers():
    text = guideline_text()

    assert "explicit negative evidence supports" in text
    assert "prohibition, exclusion, non-eligibility, non-coverage" in text
    assert "limited to that explicit scope" in text


def test_agent_instructions_contain_mandatory_global_policy_invariant():
    instructions = instructions_text()

    assert "for every hr policy answer" in instructions
    assert "negative policy conclusion unless approved knowledge base evidence explicitly supports" in instructions
    assert "that exact negative conclusion" in instructions
    assert "missing, silent, unrelated, broadly related, or insufficient" in instructions
    assert "not negative evidence" in instructions
    assert "does not explicitly establish the exact requested positive or negative policy fact" in instructions
    assert "not enough approved policy information" in instructions
    assert "do not state or imply the opposite conclusion" in instructions


def test_agent_instructions_do_not_only_delegate_policy_safety_to_guideline():
    instructions = instructions_text()

    assert "follow the evidence-state policy answering guideline" in instructions
    assert "negative policy conclusion" in instructions
    assert "not negative evidence" in instructions
    assert instructions.index("negative policy conclusion") < instructions.index(
        "follow the evidence-state policy answering guideline"
    )


def test_policy_information_is_separated_from_it_action_intent():
    instructions = instructions_text()

    assert "use the attached hr policy knowledge base only for informational questions" in instructions
    assert "do not use policy knowledge to create an it request" in instructions
    assert "what does the policy say about jira access" in instructions
    assert "information or policy question" in instructions
    assert "use it_request_flow only when the user actually wants to request or create" in instructions
    assert "do not invoke it_request_flow merely because jira, slack, software, or it policy is mentioned" in instructions


def test_orientation_information_is_separated_from_booking_action_intent():
    instructions = instructions_text()

    assert "use orientation_booking_flow only when the user actually wants to schedule or book" in instructions
    assert "what happens during orientation" in instructions
    assert "use policy knowledge for orientation information or guidance questions" in instructions
    assert "the orientation booking flow owns presentation of approved choices" in instructions
    assert "never invent, propose, or modify orientation slots yourself" in instructions


def test_ambiguous_intent_requires_clarification_before_side_effect_capability():
    instructions = instructions_text()

    assert "when wording is ambiguous, ask a clarifying question before invoking" in instructions
    assert "can you help me with jira" in instructions
    assert "clarify whether the user wants information" in instructions
    assert "actual jira access request" in instructions
    assert "tell me about orientation" in instructions
    assert "book my orientation" in instructions


def test_it_action_contract_does_not_add_company_email_or_invention():
    instructions = instructions_text()

    assert "required fields are exactly employee name, employee role, and required systems" in instructions
    assert "do not require company email" in instructions
    assert "never invent employee_name, employee_role, or required_systems" in instructions
    assert "pass those values faithfully to it_request_flow" in instructions
    assert "allow missing it values to be collected by the protected it request flow" in instructions
    assert "company_email" not in serialized_agent_text()


def test_it_action_contract_forbids_agent_side_prefield_collection():
    instructions = instructions_text()

    assert "do not pre-collect it request fields conversationally outside it_request_flow" in instructions
    assert "invoke it_request_flow rather than asking for employee name, employee role, or required systems yourself" in instructions
    assert "once it action intent is clear, invoke it_request_flow" in instructions
    assert "the it request flow owns collection of missing values" in instructions


def test_it_action_contract_accepts_only_three_prefill_arguments_and_omits_unknowns():
    instructions = instructions_text()

    assert "accepted it_request_flow inputs are only employee_name, employee_role, and required_systems" in instructions
    assert "extract and faithfully pass any accepted it request fields" in instructions
    assert "current request or clearly established conversation context" in instructions
    assert "omit any unknown accepted it input instead of inventing a placeholder" in instructions
    assert "never invent employee_name, employee_role, or required_systems" in instructions
    assert "company_email" not in serialized_agent_text()
    for forbidden_field in ["employee_id", "department", "manager"]:
        assert forbidden_field not in serialized_agent_text()


def test_it_prefill_role_and_systems_leave_only_employee_name_conceptually_missing():
    instructions = instructions_text()

    assert "if role and systems are explicit but employee name is unknown" in instructions
    assert "with employee_role and required_systems only" in instructions
    assert "let the flow ask only for employee name" in instructions


def test_it_prefill_all_three_values_should_not_recollect_fields():
    instructions = instructions_text()

    assert "if all three accepted it values are explicit" in instructions
    assert "call it_request_flow with all three" in instructions
    assert "proceed directly to review and confirmation" in instructions


@pytest.mark.parametrize("case", IT_PREFILL_HANDOFF_CASES)
def test_static_it_prefill_handoff_cases_document_expected_conceptual_missing_fields(case):
    accepted_fields = {"employee_name", "employee_role", "required_systems"}

    assert set(case) == {"prompt", "known_fields", "expected_missing_fields"}
    assert set(case["known_fields"]).issubset(accepted_fields)
    assert case["expected_missing_fields"] == accepted_fields - set(case["known_fields"])


def test_side_effect_safety_contract_is_preserved():
    instructions = instructions_text()

    assert "never bypass explicit confirmation" in instructions
    assert "protected workflows own confirmation and persistence" in instructions
    assert "do not directly call persistence tools" in instructions
    assert "accurately distinguish cancelled workflow results from completed workflow results" in instructions
    assert "do not fabricate tool results, object ids, request ids, booking ids, or persistence outcomes" in instructions
    assert "do not autonomously repeat a completed side effect" in instructions
    assert "explicitly initiates a new request" in instructions


def test_out_of_scope_and_completion_exit_behavior_remain():
    instructions = instructions_text()

    assert "never treat an out-of-scope request" in instructions
    assert "politely explain when a request is outside hr onboarding scope" in instructions
    assert "clearly communicate completion" in instructions
    assert "support a clear conversational exit" in instructions


@pytest.mark.parametrize("case", CAPABILITY_SELECTION_CASES)
def test_static_capability_selection_contract_cases(case):
    assert set(case) == {"prompt", "expected_capability", "expected_action_flow"}
    if case["expected_capability"] == "POLICY KNOWLEDGE":
        assert case["expected_action_flow"] is None
    if case["expected_capability"] == "IT REQUEST":
        assert case["expected_action_flow"] == "it_request_flow"
    if case["expected_capability"] == "ORIENTATION BOOKING":
        assert case["expected_action_flow"] == "orientation_booking_flow"
    if case["expected_capability"] in {"CLARIFY", "DECLINE"}:
        assert case["expected_action_flow"] is None


def test_static_capability_cases_are_represented_in_agent_contract_text():
    instructions = instructions_text()

    assert "what does the policy say about jira access" in instructions
    assert "i need jira access" in instructions
    assert "request slack and github access for me" in instructions
    assert "what happens during orientation" in instructions
    assert "i want to book orientation" in instructions
    assert "can you help me with jira" in instructions
    assert "out-of-scope" in instructions


def test_agent_policy_contract_does_not_hardcode_historical_regression_prompts():
    serialized_spec = serialized_agent_text()

    assert "pet insurance" not in serialized_spec
    assert "tuition" not in serialized_spec
    assert "school tuition" not in serialized_spec
    assert "university tuition" not in serialized_spec
    assert "private-school" not in serialized_spec
    assert "children" not in serialized_spec
    assert "dependents" not in serialized_spec
