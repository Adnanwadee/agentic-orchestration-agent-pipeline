from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Callable, Literal

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType, ExpectedCredentials
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.run.connections import api_key_auth, key_value
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from tools.support_triage_classifier import (
    ClassifierExecutionResult,
    MODEL_ID,
    TicketIntake,
    WATSONX_CONFIG_CONNECTION_APP_ID,
    WATSONX_CONFIG_CONNECTION_CONTRACT,
    WATSONX_CONNECTION_APP_ID,
    WATSONX_URL_DEFAULT,
    PipelineStatus,
    StructuredTicketOutput,
    build_structured_output,
    _connection_value,
)


DraftValidationStatus = Literal["valid", "invalid_exhausted", "execution_error"]
MAX_DRAFT_ATTEMPTS = 2
DRAFT_MODEL_PARAMS = {
    "temperature": 0.0,
    "max_tokens": 220,
}
DRAFT_WATSONX_CONNECTION_CONTRACT = ExpectedCredentials(
    app_id=WATSONX_CONNECTION_APP_ID,
    type=ConnectionType.API_KEY_AUTH,
)

DRAFT_PROMPT_V1_VERSION = "support-triage-drafter-v1"
DRAFT_PROMPT_V1 = """You draft concise first responses for a deterministic support-triage pipeline.

Return ONLY a raw JSON object with exactly this key:
draft_response

Draft contract:
- Write one concise, professional first response to the customer.
- Reference the customer's actual problem from the supplied ticket text.
- Be specific to the ticket rather than a generic acknowledgement.
- Include the exact assigned team value from the supplied route context.
- Include the exact SLA value from the supplied route context.
- Treat the SLA as routing metadata/target, not as a guaranteed resolution or contact time.
- Do not change, reinterpret, or add routing decisions.
- Do not invent facts, causes, fixes, refunds, account actions, investigations, or customer details.
- Do not claim a resolution or action that has not occurred.
- Do not say "we will resolve this within X", "the team will contact you within X",
  "we have started investigating", "your refund has been issued", "the issue has been fixed",
  or "an engineer is already working on it".
- Return raw JSON only. Do not use Markdown fences or prose outside JSON."""
DRAFT_PROMPT_V1_SHA256 = sha256(DRAFT_PROMPT_V1.encode("utf-8")).hexdigest()

DRAFT_PROMPT_V2_VERSION = "support-triage-drafter-v2"
DRAFT_PROMPT_V2 = """You write only the personalized acknowledgement portion of a support-triage first response.

Return ONLY a raw JSON object with exactly this key:
acknowledgement

Acknowledgement contract:
- Write one concise, professional customer-facing acknowledgement.
- Reference the customer's actual problem from the supplied ticket text.
- Be specific to the ticket rather than a generic acknowledgement.
- Do not mention, write, restate, or interpret the assigned team.
- Do not mention, write, restate, or interpret the SLA.
- Do not discuss response time, resolution time, contact timing, or service timing.
- Do not promise future review, investigation, contact, notification, response, resolution, refund, fix, or account action.
- Do not claim that any action has already happened.
- Do not invent facts, causes, fixes, refunds, account actions, investigations, or customer details.
- If route context is present in the input, treat it as internal metadata and do not verbalize it.
- Return raw JSON only. Do not use Markdown fences or prose outside JSON."""
DRAFT_PROMPT_V2_SHA256 = sha256(DRAFT_PROMPT_V2.encode("utf-8")).hexdigest()

DRAFT_PROMPT_VERSION = "support-triage-drafter-v3"
DRAFT_PROMPT = """You extract only a concise neutral problem summary for a deterministic support-triage response.

Return ONLY a raw JSON object with exactly this key:
problem_summary

Problem summary contract:
- Summarize only the actual customer issue from the supplied ticket text.
- Prefer a short neutral noun phrase or equivalent neutral issue description.
- The text must fit naturally after: "Thank you for reaching out about ..."
- Do not write a customer-service response.
- Do not mention, write, restate, or interpret the assigned team.
- Do not mention, write, restate, or interpret the SLA.
- Do not use first-person company language such as we, our, or us.
- Do not include a promise, resolution, fix, investigation, contact, notification, refund, or action claim.
- Do not claim that any action has happened or will happen.
- If route context is present in the input, treat it as internal metadata and do not verbalize it.
- Return raw JSON only. Do not use Markdown fences or prose outside JSON."""
DRAFT_PROMPT_SHA256 = sha256(DRAFT_PROMPT.encode("utf-8")).hexdigest()

DRAFT_REPAIR_INSTRUCTION_V1_VERSION = "support-triage-drafter-repair-v1"
DRAFT_REPAIR_INSTRUCTION_V1 = """The previous model response failed the required strict draft schema or route contract.

Return one corrected raw JSON object only.
Use exactly this key: draft_response.
The draft_response must contain the exact assigned team and exact SLA from the original route context.
Do not include Markdown fences, commentary, explanations outside JSON, or additional fields."""
DRAFT_REPAIR_INSTRUCTION_V1_SHA256 = sha256(
    DRAFT_REPAIR_INSTRUCTION_V1.encode("utf-8")
).hexdigest()

DRAFT_REPAIR_INSTRUCTION_V2_VERSION = "support-triage-drafter-repair-v2"
DRAFT_REPAIR_INSTRUCTION_V2 = """The previous model response failed the required strict acknowledgement schema or safety contract.

Return one corrected raw JSON object only.
Use exactly this key: acknowledgement.
The acknowledgement must reference the customer's actual issue.
Do not mention assigned team, SLA, response time, resolution time, future contact, future review, future investigation, notification, refund, fix, or completed action.
Do not include Markdown fences, commentary, explanations outside JSON, or additional fields."""
DRAFT_REPAIR_INSTRUCTION_V2_SHA256 = sha256(
    DRAFT_REPAIR_INSTRUCTION_V2.encode("utf-8")
).hexdigest()

DRAFT_REPAIR_INSTRUCTION_VERSION = "support-triage-drafter-repair-v3"
DRAFT_REPAIR_INSTRUCTION = """The previous model response failed the required strict problem_summary schema or safety contract.

Return one corrected raw JSON object only.
Use exactly this key: problem_summary.
The problem_summary must be a concise neutral description of only the customer's issue.
It must fit naturally after: "Thank you for reaching out about ..."
Do not mention assigned team, SLA, response time, resolution time, first-person company action, future action, completed action, notification, refund, or fix.
Do not include Markdown fences, commentary, explanations outside JSON, or additional fields."""
DRAFT_REPAIR_INSTRUCTION_SHA256 = sha256(
    DRAFT_REPAIR_INSTRUCTION.encode("utf-8")
).hexdigest()

PROHIBITED_PROBLEM_SUMMARY_PATTERNS = (
    r"\b(?:we|our|us)\b",
    r"\b(?:will|would|shall|going to|aim to|committed to)\b.{0,80}\b(?:review|investigate|contact|respond|resolve|fix|address|notify|refund)\b",
    r"\b(?:review|investigate|contact|respond|resolve|fix|address|notify|refund)\b.{0,80}\b(?:within|by|under|in \d+|business day|hour|minute)\b",
    r"\b(?:has|have|is|are|was|were|will be)\s+.{0,40}\b(?:assigned|assisting|notified|started|escalated|resolved|fixed|refunded|provided)\b",
)


class DraftOutputValidationError(ValueError):
    """Raised only for model text that fails the drafting output contract."""


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class DraftRequest(StrictModel):
    ticket_id: str = Field(min_length=1, max_length=64)
    ticket_text: str = Field(min_length=1, max_length=5000)
    assigned_team: str = Field(min_length=1, max_length=120)
    sla: str = Field(min_length=1, max_length=80)

    @field_validator("ticket_id", "ticket_text", "assigned_team", "sla")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value must not be blank")
        return value


class DraftProblemSummaryResult(StrictModel):
    problem_summary: str = Field(min_length=1, max_length=300)

    @field_validator("problem_summary")
    @classmethod
    def reject_blank_problem_summary(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("problem_summary must not be blank")
        return value


class DraftExecutionResult(StrictModel):
    ticket_id: str
    draft_response: str | None = None
    validation_status: DraftValidationStatus
    attempt_count: int = Field(ge=0, le=MAX_DRAFT_ATTEMPTS)
    error_code: str | None = None
    error_message: str | None = None
    latency_seconds: float | None = Field(default=None, ge=0.0)
    token_usage: dict[str, int] | None = None
    prompt_version: str = DRAFT_PROMPT_VERSION
    prompt_sha256: str = DRAFT_PROMPT_SHA256
    model_id: str = MODEL_ID


@dataclass(frozen=True)
class DraftModelCallResult:
    raw_text: str
    latency_seconds: float | None = None
    token_usage: dict[str, int] | None = None


def build_draft_messages(request: DraftRequest, attempt: int = 1) -> list[dict[str, str]]:
    messages = [{"role": "system", "content": DRAFT_PROMPT}]
    if attempt == 2:
        messages.append({"role": "system", "content": DRAFT_REPAIR_INSTRUCTION})
    messages.append(
        {
            "role": "user",
            "content": json.dumps(
                {
                    "ticket_id": request.ticket_id,
                    "ticket_text": request.ticket_text,
                    "assigned_team": request.assigned_team,
                    "sla": request.sla,
                },
                sort_keys=True,
            ),
        }
    )
    return messages


def parse_draft_response(raw_text: str, request: DraftRequest) -> DraftProblemSummaryResult:
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise DraftOutputValidationError("draft response was not strict JSON") from exc
    if not isinstance(payload, dict):
        raise DraftOutputValidationError("draft response JSON must be an object")
    try:
        result = DraftProblemSummaryResult.model_validate(payload)
    except ValidationError as exc:
        raise DraftOutputValidationError("draft response failed schema validation") from exc

    problem_summary = result.problem_summary
    if request.assigned_team in problem_summary:
        raise DraftOutputValidationError("problem summary included assigned team")
    if request.sla in problem_summary:
        raise DraftOutputValidationError("problem summary included SLA")
    for pattern in PROHIBITED_PROBLEM_SUMMARY_PATTERNS:
        if re.search(pattern, problem_summary, flags=re.IGNORECASE):
            raise DraftOutputValidationError(
                "problem summary contained unsupported company action or timing claim"
            )
    return result


def compose_draft_response(problem_summary: str, request: DraftRequest) -> str:
    return (
        f"Thank you for reaching out about {problem_summary}.\n\n"
        f"Assigned team: {request.assigned_team}. SLA target: {request.sla}."
    )


def _aggregate_usage(attempt_usages: list[dict[str, int] | None]) -> dict[str, int] | None:
    totals: dict[str, int] = {}
    for usage in attempt_usages:
        if not usage:
            continue
        for key, value in usage.items():
            if isinstance(value, int):
                totals[key] = totals.get(key, 0) + value
    return totals or None


def _aggregate_latency(started: float, attempt_latencies: list[float | None]) -> float:
    if attempt_latencies and all(latency is not None for latency in attempt_latencies):
        return sum(float(latency) for latency in attempt_latencies)
    return time.perf_counter() - started


def _sanitize_error_message(message: str) -> str:
    sanitized = re.sub(
        r"(?i)(api[_-]?key|token|secret|password|authorization)\s*[:=]\s*(?:bearer\s+)?\S+",
        r"\1=[redacted]",
        message,
    )
    sanitized = re.sub(r"(?i)bearer\s+[a-z0-9._-]+", "Bearer [redacted]", sanitized)
    return sanitized


def _initialization_error_result(ticket_id: str, started: float, exc: Exception) -> DraftExecutionResult:
    return DraftExecutionResult(
        ticket_id=ticket_id,
        draft_response=None,
        validation_status="execution_error",
        attempt_count=0,
        error_code="DRAFTER_INITIALIZATION_ERROR",
        error_message=_sanitize_error_message(str(exc)),
        latency_seconds=time.perf_counter() - started,
        token_usage=None,
    )


def draft_with_bounded_attempts(
    request: DraftRequest,
    call_model: Callable[[DraftRequest, int], DraftModelCallResult],
) -> DraftExecutionResult:
    last_validation_error: DraftOutputValidationError | None = None
    attempt_latencies: list[float | None] = []
    attempt_usages: list[dict[str, int] | None] = []
    started = time.perf_counter()

    for attempt in range(1, MAX_DRAFT_ATTEMPTS + 1):
        try:
            model_call = call_model(request, attempt)
        except Exception as exc:
            return DraftExecutionResult(
                ticket_id=request.ticket_id,
                draft_response=None,
                validation_status="execution_error",
                attempt_count=attempt,
                error_code="DRAFT_EXECUTION_ERROR",
                error_message=_sanitize_error_message(str(exc)),
                latency_seconds=time.perf_counter() - started,
                token_usage=_aggregate_usage(attempt_usages),
            )

        attempt_latencies.append(model_call.latency_seconds)
        attempt_usages.append(model_call.token_usage)
        try:
            draft = parse_draft_response(model_call.raw_text, request)
        except DraftOutputValidationError as exc:
            last_validation_error = exc
            continue

        return DraftExecutionResult(
            ticket_id=request.ticket_id,
            draft_response=compose_draft_response(draft.problem_summary, request),
            validation_status="valid",
            attempt_count=attempt,
            latency_seconds=_aggregate_latency(started, attempt_latencies),
            token_usage=_aggregate_usage(attempt_usages),
        )

    return DraftExecutionResult(
        ticket_id=request.ticket_id,
        draft_response=None,
        validation_status="invalid_exhausted",
        attempt_count=MAX_DRAFT_ATTEMPTS,
        error_code="DRAFT_INVALID_EXHAUSTED",
        error_message=str(last_validation_error) if last_validation_error else "draft failed validation",
        latency_seconds=_aggregate_latency(started, attempt_latencies),
        token_usage=_aggregate_usage(attempt_usages),
    )


def _extract_chat_content(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("watsonx chat response did not contain choices")
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("watsonx chat response did not contain text content")
    return content


def _extract_usage(response: dict[str, Any]) -> dict[str, int] | None:
    usage = response.get("usage")
    if not isinstance(usage, dict):
        return None
    clean_usage: dict[str, int] = {}
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        value = usage.get(key)
        if isinstance(value, int):
            clean_usage[key] = value
    return clean_usage or None


class WatsonxChatDrafter:
    def __init__(
        self,
        *,
        api_key: str,
        project_id: str,
        url: str = WATSONX_URL_DEFAULT,
        model_id: str = MODEL_ID,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key is required")
        if not project_id.strip():
            raise ValueError("project_id is required")
        credentials = Credentials(url=url, api_key=api_key)
        self._model = ModelInference(
            model_id=model_id,
            credentials=credentials,
            project_id=project_id,
            params=DRAFT_MODEL_PARAMS,
        )

    def __call__(self, request: DraftRequest, attempt: int) -> DraftModelCallResult:
        started = time.perf_counter()
        response = self._model.chat(
            messages=build_draft_messages(request, attempt=attempt),
            params=DRAFT_MODEL_PARAMS,
        )
        elapsed = time.perf_counter() - started
        return DraftModelCallResult(
            raw_text=_extract_chat_content(response),
            latency_seconds=elapsed,
            token_usage=_extract_usage(response),
        )


def local_env_drafter() -> WatsonxChatDrafter:
    api_key = os.environ.get("WX_API_KEY", "")
    project_id = os.environ.get("WX_PROJECT_ID", "")
    url = os.environ.get("WX_URL", WATSONX_URL_DEFAULT)
    return WatsonxChatDrafter(api_key=api_key, project_id=project_id, url=url)


def orchestrate_connection_drafter(*, project_id: str, url: str = WATSONX_URL_DEFAULT) -> WatsonxChatDrafter:
    credentials = api_key_auth(app_id=WATSONX_CONNECTION_APP_ID)
    api_key = getattr(credentials, "api_key", None)
    if not api_key:
        raise RuntimeError("watsonx.ai connection credentials are unavailable")
    return WatsonxChatDrafter(api_key=api_key, project_id=project_id, url=url)


def orchestrate_configured_drafter() -> WatsonxChatDrafter:
    credentials = api_key_auth(app_id=WATSONX_CONNECTION_APP_ID)
    api_key = getattr(credentials, "api_key", None)
    if not api_key:
        raise RuntimeError("watsonx.ai connection credentials are unavailable")
    config = key_value(app_id=WATSONX_CONFIG_CONNECTION_APP_ID)
    project_id = _connection_value(config, "project_id")
    if not project_id:
        raise RuntimeError("watsonx.ai project_id key-value connection configuration is unavailable")
    url = getattr(credentials, "url", None) or WATSONX_URL_DEFAULT
    return WatsonxChatDrafter(api_key=api_key, project_id=project_id, url=url or WATSONX_URL_DEFAULT)


def draft_auto_route_response(
    output: StructuredTicketOutput,
    call_model: Callable[[DraftRequest, int], DraftModelCallResult],
) -> tuple[StructuredTicketOutput, DraftExecutionResult | None]:
    if (
        output.review_required
        or output.status != "auto_route_pending"
        or not output.assigned_team
        or not output.sla
    ):
        return output.model_copy(update={"draft_response": None}), None

    request = DraftRequest(
        ticket_id=output.ticket_id,
        ticket_text=output.ticket_text,
        assigned_team=output.assigned_team,
        sla=output.sla,
    )
    draft = draft_with_bounded_attempts(request, call_model)
    if draft.validation_status != "valid":
        return apply_draft_execution(output, draft), draft
    return apply_draft_execution(output, draft), draft


def apply_draft_execution(
    output: StructuredTicketOutput,
    draft: DraftExecutionResult,
) -> StructuredTicketOutput:
    return output.model_copy(
        update={
            "draft_response": draft.draft_response if draft.validation_status == "valid" else None,
            "status": "auto_routed" if draft.validation_status == "valid" else "draft_failed",
            "draft_validation_status": draft.validation_status,
            "draft_attempt_count": draft.attempt_count,
            "draft_error_code": draft.error_code,
            "draft_error_message": draft.error_message,
            "draft_latency_seconds": draft.latency_seconds,
            "draft_token_usage": draft.token_usage,
            "draft_prompt_version": draft.prompt_version,
            "draft_prompt_sha256": draft.prompt_sha256,
            "draft_model_id": draft.model_id,
        }
    )


def finalize_support_triage_output(
    ticket: TicketIntake,
    classifier_execution: ClassifierExecutionResult,
    call_model: Callable[[DraftRequest, int], DraftModelCallResult],
) -> StructuredTicketOutput:
    output = build_structured_output(ticket, classifier_execution)
    final_output, _ = draft_auto_route_response(output, call_model)
    return final_output


def _normalize_classifier_execution_transport(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    classification = normalized.get("classification")
    if isinstance(classification, dict):
        normalized_classification = dict(classification)
        normalized_classification.setdefault("secondary_category", None)
        normalized_classification.setdefault("urgency", None)
        normalized["classification"] = normalized_classification
    elif "classification" not in normalized and normalized.get("validation_status") in {
        "invalid_exhausted",
        "execution_error",
    }:
        normalized["classification"] = None
    return normalized


def _normalize_structured_output_transport(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    classification = normalized.get("classification")
    if isinstance(classification, dict):
        normalized_classification = dict(classification)
        normalized_classification.setdefault("secondary_category", None)
        normalized_classification.setdefault("urgency", None)
        normalized["classification"] = normalized_classification
    elif (
        "classification" not in normalized
        and normalized.get("classification_valid") is False
        and normalized.get("validation_status") in {"invalid_exhausted", "execution_error"}
        and normalized.get("status") == "invalid_output"
    ):
        normalized["classification"] = None
    return normalized


@tool(
    name="apply_support_triage_policy",
    description="Apply deterministic support-triage review and routing policy to a classifier result.",
)
def apply_support_triage_policy(
    ticket_id: str,
    ticket_text: str,
    classifier_execution: dict[str, Any],
) -> dict[str, Any]:
    ticket = TicketIntake(ticket_id=ticket_id, ticket_text=ticket_text)
    execution = ClassifierExecutionResult.model_validate(
        _normalize_classifier_execution_transport(classifier_execution)
    )
    return build_structured_output(ticket, execution).model_dump()


@tool(
    name="finalize_support_triage_record",
    description="Finalize one support-triage output record after optional drafting.",
)
def finalize_support_triage_record(
    pre_draft_output: dict[str, Any],
    draft_execution: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output = StructuredTicketOutput.model_validate(
        _normalize_structured_output_transport(pre_draft_output)
    )
    if output.status != "auto_route_pending":
        return output.model_dump()
    if draft_execution is None:
        return output.model_copy(update={"status": "draft_failed"}).model_dump()
    draft = DraftExecutionResult.model_validate(draft_execution)
    return apply_draft_execution(output, draft).model_dump()


@tool(
    name="draft_support_response",
    description="Draft one support-triage first response only from an already approved automatic route.",
    expected_credentials=[DRAFT_WATSONX_CONNECTION_CONTRACT],
)
def draft_support_response(
    ticket_id: str,
    ticket_text: str,
    assigned_team: str,
    sla: str,
    wx_project_id: str,
    wx_url: str = WATSONX_URL_DEFAULT,
) -> dict[str, Any]:
    request = DraftRequest(
        ticket_id=ticket_id,
        ticket_text=ticket_text,
        assigned_team=assigned_team,
        sla=sla,
    )
    started = time.perf_counter()
    try:
        drafter = orchestrate_connection_drafter(project_id=wx_project_id, url=wx_url)
    except Exception as exc:
        return _initialization_error_result(ticket_id=request.ticket_id, started=started, exc=exc).model_dump()
    execution = draft_with_bounded_attempts(request, drafter)
    return execution.model_dump()


@tool(
    name="draft_support_response_configured",
    description="Draft one support-triage first response using watsonx.ai configuration from the watsonx_ai connection.",
    expected_credentials=[DRAFT_WATSONX_CONNECTION_CONTRACT, WATSONX_CONFIG_CONNECTION_CONTRACT],
)
def draft_support_response_configured(
    ticket_id: str,
    ticket_text: str,
    assigned_team: str,
    sla: str,
) -> dict[str, Any]:
    request = DraftRequest(
        ticket_id=ticket_id,
        ticket_text=ticket_text,
        assigned_team=assigned_team,
        sla=sla,
    )
    started = time.perf_counter()
    try:
        drafter = orchestrate_configured_drafter()
    except Exception as exc:
        return _initialization_error_result(ticket_id=request.ticket_id, started=started, exc=exc).model_dump()
    execution = draft_with_bounded_attempts(request, drafter)
    return execution.model_dump()
