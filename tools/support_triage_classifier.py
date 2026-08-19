from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Callable, Literal

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType, ExpectedCredentials
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.run.connections import api_key_auth, key_value
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator


Category = Literal["billing", "technical", "account", "general"]
Urgency = Literal["low", "medium", "high", "critical"]
ValidationStatus = Literal["valid", "invalid_exhausted", "execution_error"]
PipelineStatus = Literal[
    "pending_routing",
    "human_review",
    "auto_route_pending",
    "auto_routed",
    "draft_failed",
    "invalid_output",
]

MODEL_ID = "meta-llama/llama-4-maverick-17b-128e-instruct-fp8"
ORCHESTRATE_MODEL_ID = "watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8"
WATSONX_URL_DEFAULT = "https://eu-de.ml.cloud.ibm.com"
WATSONX_CONNECTION_APP_ID = "watsonx_ai"
WATSONX_CONFIG_CONNECTION_APP_ID = "watsonx_ai_config"
INITIAL_CLASSIFIER_PROMPT_VERSION = "support-triage-classifier-v1"
MAX_CLASSIFIER_ATTEMPTS = 2
CONFIDENCE_THRESHOLD = 0.80
MODEL_PARAMS = {
    "temperature": 0.0,
    "max_tokens": 300,
}
WATSONX_CONNECTION_CONTRACT = ExpectedCredentials(
    app_id=WATSONX_CONNECTION_APP_ID,
    type=ConnectionType.API_KEY_AUTH,
)
WATSONX_CONFIG_CONNECTION_CONTRACT = ExpectedCredentials(
    app_id=WATSONX_CONFIG_CONNECTION_APP_ID,
    type=ConnectionType.KEY_VALUE,
)

INITIAL_CLASSIFIER_PROMPT = """You classify customer support tickets for a deterministic support-triage pipeline.

Return ONLY a raw JSON object with exactly these keys:
category
secondary_category
urgency
confidence
reasoning

Field contract:
- category: exactly one of "billing", "technical", "account", "general".
- secondary_category: exactly one of "billing", "technical", "account", "general", or JSON null.
- urgency: exactly one of "low", "medium", "high", "critical", or JSON null.
- confidence: a numeric value from 0.0 through 1.0 inclusive.
- reasoning: a short non-empty explanation grounded only in the ticket text.

Decision rules:
- Classify only from the provided ticket text.
- Do not invent missing facts, impact, deadlines, affected-user counts, causes, fixes, or customer details.
- Choose one primary category.
- Use secondary_category only when the ticket contains a separate material issue that independently belongs to a second category.
- secondary_category must be JSON null when there is no separate material second issue.
- secondary_category must not equal category.
- A consequence of the primary issue does not by itself create a secondary category.
- Urgency is about time sensitivity, scope, affected users, blocking impact, or explicit business consequence, not just topic.
- Use urgency null when the ticket lacks enough evidence to infer urgency.
- Do not coerce vague or low-information tickets to medium urgency.
- Never output urgency labels such as "unknown", "unclear", "none", "n/a", or "normal".
- Do not decide review_required, review reasons, routing, assigned team, SLA, status, or drafting.
- Return raw JSON only. Do not use Markdown fences or prose outside JSON."""

INITIAL_CLASSIFIER_PROMPT_SHA256 = sha256(
    INITIAL_CLASSIFIER_PROMPT.encode("utf-8")
).hexdigest()

CLASSIFIER_PROMPT_VERSION = "support-triage-classifier-v2"
CLASSIFIER_PROMPT = """You classify customer support tickets for a deterministic support-triage pipeline.

Return ONLY a raw JSON object with exactly these keys:
category
secondary_category
urgency
confidence
reasoning

Field contract:
- category: exactly one of "billing", "technical", "account", "general".
- secondary_category: exactly one of "billing", "technical", "account", "general", or JSON null.
- urgency: exactly one of "low", "medium", "high", "critical", or JSON null.
- confidence: a numeric value from 0.0 through 1.0 inclusive.
- reasoning: a short non-empty explanation grounded only in the ticket text.

Category definitions:
- billing: charges, payments, refunds, invoices, subscriptions/plans, renewals, pricing, or discounts.
- technical: application or product malfunction, errors, crashes, unavailable or broken features, performance issues, exports, reports, or data-display failures.
- account: login/access, password/reset, account identity, profile/settings, user permissions, or account administration.
- general: support requests or information that do not materially belong to billing, technical, or account.

Urgency rubric:
- critical: widespread outage or unavailability, severe blocking impact affecting multiple users or a team, or an explicitly business-critical operation where work cannot proceed.
- high: clear time-sensitive, immediate, same-day/near-term, financial, security, or significant business impact that is serious but does not meet critical scope.
- medium: an active problem or requested operational/account/billing change that requires action but has no evidence of critical/high severity or explicit low-priority intent.
- low: informational/how-to/general inquiry, feedback, minor issue, or explicitly no-rush/not-urgent request without meaningful blocking impact.
- JSON null: the ticket contains too little evidence to safely infer urgency.

Decision rules:
- Classify only from the provided ticket text.
- Do not invent missing facts, impact, deadlines, affected-user counts, causes, fixes, or customer details.
- Choose one primary category.
- Use secondary_category only when the ticket contains a separate material issue that independently belongs to a second category.
- secondary_category must be JSON null when there is no separate material second issue.
- secondary_category must not equal category.
- A symptom, consequence, or implementation mechanism of the primary issue does not by itself create a secondary category.
- Urgency is about time sensitivity, scope, affected users, blocking impact, or explicit business consequence, not just topic.
- Do not infer critical merely from emotional language.
- Do not infer high solely because a customer wants an issue fixed.
- Use urgency null when the ticket lacks enough evidence to infer urgency.
- Do not default vague or low-information tickets to medium urgency.
- Never output urgency labels such as "unknown", "unclear", "none", "n/a", or "normal".
- Do not decide review_required, review reasons, routing, assigned team, SLA, status, or drafting.
- Return raw JSON only. Do not use Markdown fences or prose outside JSON."""
CLASSIFIER_PROMPT_SHA256 = sha256(CLASSIFIER_PROMPT.encode("utf-8")).hexdigest()

CLASSIFIER_REPAIR_INSTRUCTION_VERSION = "support-triage-classifier-repair-v1"
CLASSIFIER_REPAIR_INSTRUCTION = """The previous model response failed the required strict classification schema.

Return one corrected raw JSON object only.
Use exactly these keys: category, secondary_category, urgency, confidence, reasoning.
Use only the already-defined enum values and true JSON null rules from the base instructions.
Do not include Markdown fences, commentary, explanations outside JSON, or additional fields."""
CLASSIFIER_REPAIR_INSTRUCTION_SHA256 = sha256(
    CLASSIFIER_REPAIR_INSTRUCTION.encode("utf-8")
).hexdigest()


class ClassificationOutputValidationError(ValueError):
    """Raised only for model text that fails the classification output contract."""


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class TicketIntake(StrictModel):
    ticket_id: str = Field(min_length=1, max_length=64)
    ticket_text: str = Field(min_length=1, max_length=5000)

    @field_validator("ticket_id", "ticket_text")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value must not be blank")
        return value


class ClassificationResult(StrictModel):
    category: Category
    secondary_category: Category | None
    urgency: Urgency | None
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def secondary_must_differ(self) -> "ClassificationResult":
        if self.secondary_category is not None and self.secondary_category == self.category:
            raise ValueError("secondary_category must differ from category")
        return self

    @field_validator("reasoning")
    @classmethod
    def reject_blank_reasoning(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("reasoning must not be blank")
        return value


class ClassifierExecutionResult(StrictModel):
    ticket_id: str
    classification: ClassificationResult | None
    validation_status: ValidationStatus
    attempt_count: int = Field(ge=0, le=MAX_CLASSIFIER_ATTEMPTS)
    error_code: str | None = None
    error_message: str | None = None
    latency_seconds: float | None = Field(default=None, ge=0.0)
    token_usage: dict[str, int] | None = None
    prompt_version: str = CLASSIFIER_PROMPT_VERSION
    prompt_sha256: str = CLASSIFIER_PROMPT_SHA256
    model_id: str = MODEL_ID


class StructuredTicketOutput(StrictModel):
    ticket_id: str
    ticket_text: str
    classification: ClassificationResult | None
    classification_valid: bool
    validation_status: ValidationStatus
    review_required: bool
    review_reasons: list[str]
    assigned_team: str | None = None
    sla: str | None = None
    draft_response: str | None = None
    status: PipelineStatus
    error_code: str | None = None
    error_message: str | None = None
    attempt_count: int = Field(ge=0, le=MAX_CLASSIFIER_ATTEMPTS)
    latency_seconds: float | None = Field(default=None, ge=0.0)
    token_usage: dict[str, int] | None = None
    draft_validation_status: str | None = None
    draft_attempt_count: int | None = Field(default=None, ge=0)
    draft_error_code: str | None = None
    draft_error_message: str | None = None
    draft_latency_seconds: float | None = Field(default=None, ge=0.0)
    draft_token_usage: dict[str, int] | None = None
    draft_prompt_version: str | None = None
    draft_prompt_sha256: str | None = None
    draft_model_id: str | None = None


@dataclass(frozen=True)
class RouteDecision:
    assigned_team: str
    sla: str


@dataclass(frozen=True)
class ModelCallResult:
    raw_text: str
    latency_seconds: float | None = None
    token_usage: dict[str, int] | None = None


HUMAN_REVIEW_ASSIGNED_TEAM = "Triage — Human"
HUMAN_REVIEW_SLA = "Immediate"

AUTHORITATIVE_ROUTING_TABLE: dict[tuple[str, str], RouteDecision] = {
    ("billing", "critical"): RouteDecision("Billing — Senior", "1 hour"),
    ("billing", "high"): RouteDecision("Billing — Standard", "4 hours"),
    ("billing", "medium"): RouteDecision("Billing — Standard", "1 business day"),
    ("billing", "low"): RouteDecision("Billing — Standard", "3 business days"),
    ("technical", "critical"): RouteDecision("Engineering — On-call", "30 minutes"),
    ("technical", "high"): RouteDecision("Engineering — Support", "2 hours"),
    ("technical", "medium"): RouteDecision("Engineering — Support", "1 business day"),
    ("technical", "low"): RouteDecision("Engineering — Backlog", "5 business days"),
    ("account", "high"): RouteDecision("Customer Success", "4 hours"),
    ("account", "medium"): RouteDecision("Customer Success", "1 business day"),
    ("account", "low"): RouteDecision("Customer Success", "3 business days"),
    ("general", "critical"): RouteDecision("Customer Success", "2 business days"),
    ("general", "high"): RouteDecision("Customer Success", "2 business days"),
    ("general", "medium"): RouteDecision("Customer Success", "2 business days"),
    ("general", "low"): RouteDecision("Customer Success", "2 business days"),
}


def build_classifier_messages(ticket_text: str, attempt: int = 1) -> list[dict[str, str]]:
    messages = [
        {"role": "system", "content": CLASSIFIER_PROMPT},
    ]
    if attempt == 2:
        messages.append({"role": "system", "content": CLASSIFIER_REPAIR_INSTRUCTION})
    messages.append({"role": "user", "content": f"Ticket text:\n{ticket_text}"})
    return messages


def parse_classification_response(raw_text: str) -> ClassificationResult:
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ClassificationOutputValidationError("model response was not strict JSON") from exc
    if not isinstance(payload, dict):
        raise ClassificationOutputValidationError("model response JSON must be an object")
    try:
        return ClassificationResult.model_validate(payload)
    except ValidationError as exc:
        raise ClassificationOutputValidationError(
            "model response failed classification schema validation"
        ) from exc


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


def _normalize_route_value(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    return normalized or None


def lookup_authoritative_route(category: str | None, urgency: str | None) -> RouteDecision | None:
    normalized_category = _normalize_route_value(category)
    normalized_urgency = _normalize_route_value(urgency)
    if normalized_category is None or normalized_urgency is None:
        return None
    return AUTHORITATIVE_ROUTING_TABLE.get((normalized_category, normalized_urgency))


def classify_with_bounded_attempts(
    ticket: TicketIntake,
    call_model: Callable[[TicketIntake, int], ModelCallResult],
) -> ClassifierExecutionResult:
    last_validation_error: ClassificationOutputValidationError | None = None
    attempt_latencies: list[float | None] = []
    attempt_usages: list[dict[str, int] | None] = []
    started = time.perf_counter()

    for attempt in range(1, MAX_CLASSIFIER_ATTEMPTS + 1):
        try:
            model_call = call_model(ticket, attempt)
        except Exception as exc:
            return ClassifierExecutionResult(
                ticket_id=ticket.ticket_id,
                classification=None,
                validation_status="execution_error",
                attempt_count=attempt,
                error_code="CLASSIFIER_EXECUTION_ERROR",
                error_message=str(exc),
                latency_seconds=time.perf_counter() - started,
                token_usage=_aggregate_usage(attempt_usages),
            )

        attempt_latencies.append(model_call.latency_seconds)
        attempt_usages.append(model_call.token_usage)
        try:
            classification = parse_classification_response(model_call.raw_text)
        except ClassificationOutputValidationError as exc:
            last_validation_error = exc
            continue

        return ClassifierExecutionResult(
            ticket_id=ticket.ticket_id,
            classification=classification,
            validation_status="valid",
            attempt_count=attempt,
            latency_seconds=_aggregate_latency(started, attempt_latencies),
            token_usage=_aggregate_usage(attempt_usages),
        )

    return ClassifierExecutionResult(
        ticket_id=ticket.ticket_id,
        classification=None,
        validation_status="invalid_exhausted",
        attempt_count=MAX_CLASSIFIER_ATTEMPTS,
        error_code="CLASSIFICATION_INVALID_EXHAUSTED",
        error_message=str(last_validation_error) if last_validation_error else "classification failed validation",
        latency_seconds=_aggregate_latency(started, attempt_latencies),
        token_usage=_aggregate_usage(attempt_usages),
    )


def evaluate_pre_routing_review(
    execution: ClassifierExecutionResult,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if execution.validation_status != "valid" or execution.classification is None:
        reasons.append("invalid_classification_output")
        return True, reasons

    classification = execution.classification
    if classification.confidence < CONFIDENCE_THRESHOLD:
        reasons.append("confidence_below_threshold")
    if classification.secondary_category is not None:
        reasons.append("secondary_category_present")
    if classification.urgency is None:
        reasons.append("urgency_null")
    elif lookup_authoritative_route(classification.category, classification.urgency) is None:
        reasons.append("unsupported_route")
    return bool(reasons), reasons


def build_structured_output(
    ticket: TicketIntake,
    execution: ClassifierExecutionResult,
) -> StructuredTicketOutput:
    review_required, review_reasons = evaluate_pre_routing_review(execution)
    status: PipelineStatus
    assigned_team: str | None
    sla: str | None

    if execution.validation_status != "valid":
        status = "invalid_output"
        assigned_team = HUMAN_REVIEW_ASSIGNED_TEAM
        sla = HUMAN_REVIEW_SLA
    elif review_required:
        status = "human_review"
        assigned_team = HUMAN_REVIEW_ASSIGNED_TEAM
        sla = HUMAN_REVIEW_SLA
    else:
        route = lookup_authoritative_route(
            execution.classification.category if execution.classification else None,
            execution.classification.urgency if execution.classification else None,
        )
        if route is None:
            review_required = True
            review_reasons = ["unsupported_route"]
            status = "human_review"
            assigned_team = HUMAN_REVIEW_ASSIGNED_TEAM
            sla = HUMAN_REVIEW_SLA
        else:
            status = "auto_route_pending"
            assigned_team = route.assigned_team
            sla = route.sla

    return StructuredTicketOutput(
        ticket_id=ticket.ticket_id,
        ticket_text=ticket.ticket_text,
        classification=execution.classification,
        classification_valid=execution.validation_status == "valid",
        validation_status=execution.validation_status,
        review_required=review_required,
        review_reasons=review_reasons,
        assigned_team=assigned_team,
        sla=sla,
        draft_response=None,
        status=status,
        error_code=execution.error_code,
        error_message=execution.error_message,
        attempt_count=execution.attempt_count,
        latency_seconds=execution.latency_seconds,
        token_usage=execution.token_usage,
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


class WatsonxChatClassifier:
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
            params=MODEL_PARAMS,
        )

    def __call__(self, ticket: TicketIntake, attempt: int) -> ModelCallResult:
        started = time.perf_counter()
        response = self._model.chat(
            messages=build_classifier_messages(ticket.ticket_text, attempt=attempt),
            params=MODEL_PARAMS,
        )
        elapsed = time.perf_counter() - started
        return ModelCallResult(
            raw_text=_extract_chat_content(response),
            latency_seconds=elapsed,
            token_usage=_extract_usage(response),
        )


def local_env_classifier() -> WatsonxChatClassifier:
    api_key = os.environ.get("WX_API_KEY", "")
    project_id = os.environ.get("WX_PROJECT_ID", "")
    url = os.environ.get("WX_URL", WATSONX_URL_DEFAULT)
    return WatsonxChatClassifier(api_key=api_key, project_id=project_id, url=url)


def orchestrate_connection_classifier(*, project_id: str, url: str = WATSONX_URL_DEFAULT) -> WatsonxChatClassifier:
    credentials = api_key_auth(app_id=WATSONX_CONNECTION_APP_ID)
    api_key = getattr(credentials, "api_key", None)
    if not api_key:
        raise RuntimeError("watsonx.ai connection credentials are unavailable")
    return WatsonxChatClassifier(api_key=api_key, project_id=project_id, url=url)


def _connection_config_value(credentials: Any, *names: str, default: str | None = None) -> str | None:
    custom_configuration = getattr(credentials, "custom_configuration", None) or {}
    for name in names:
        value = custom_configuration.get(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


def _connection_value(credentials: Any, name: str) -> str | None:
    value = credentials.get(name) if isinstance(credentials, dict) else getattr(credentials, name, None)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def orchestrate_configured_classifier() -> WatsonxChatClassifier:
    credentials = api_key_auth(app_id=WATSONX_CONNECTION_APP_ID)
    api_key = getattr(credentials, "api_key", None)
    if not api_key:
        raise RuntimeError("watsonx.ai connection credentials are unavailable")
    config = key_value(app_id=WATSONX_CONFIG_CONNECTION_APP_ID)
    project_id = _connection_value(config, "project_id")
    if not project_id:
        raise RuntimeError("watsonx.ai project_id key-value connection configuration is unavailable")
    url = getattr(credentials, "url", None) or WATSONX_URL_DEFAULT
    return WatsonxChatClassifier(api_key=api_key, project_id=project_id, url=url or WATSONX_URL_DEFAULT)


@tool(
    name="classify_support_ticket",
    description="Classify one support ticket into the frozen Part B category/urgency contract using watsonx.ai.",
    expected_credentials=[WATSONX_CONNECTION_CONTRACT],
)
def classify_support_ticket(ticket_id: str, ticket_text: str, wx_project_id: str, wx_url: str = WATSONX_URL_DEFAULT) -> dict[str, Any]:
    ticket = TicketIntake(ticket_id=ticket_id, ticket_text=ticket_text)
    classifier = orchestrate_connection_classifier(project_id=wx_project_id, url=wx_url)
    execution = classify_with_bounded_attempts(ticket, classifier)
    return execution.model_dump()


@tool(
    name="classify_support_ticket_configured",
    description="Classify one support ticket using watsonx.ai configuration from the watsonx_ai connection.",
    expected_credentials=[WATSONX_CONNECTION_CONTRACT, WATSONX_CONFIG_CONNECTION_CONTRACT],
)
def classify_support_ticket_configured(ticket_id: str, ticket_text: str) -> dict[str, Any]:
    ticket = TicketIntake(ticket_id=ticket_id, ticket_text=ticket_text)
    classifier = orchestrate_configured_classifier()
    execution = classify_with_bounded_attempts(ticket, classifier)
    return execution.model_dump()
