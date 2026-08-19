from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from typing import Any

from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType, ExpectedCredentials
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.run.connections import api_key_auth


COS_CONNECTION_APP_ID = "cos_onboarding"
COS_BUCKET = "agentic-onboarding-p2-9g821-01"
COS_ENDPOINT = "https://s3.eu-de.cloud-object-storage.appdomain.cloud"
IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
CONNECTION_CONTRACT = ExpectedCredentials(
    app_id=COS_CONNECTION_APP_ID,
    type=ConnectionType.API_KEY_AUTH,
)


class PersistenceError(RuntimeError):
    pass


def _clean_required(value: str, field_name: str) -> str:
    cleaned = value.strip() if isinstance(value, str) else ""
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _new_id() -> str:
    return uuid.uuid4().hex


def _get_api_key() -> str:
    credentials = api_key_auth(app_id=COS_CONNECTION_APP_ID)
    api_key = getattr(credentials, "api_key", None)
    if not api_key:
        raise PersistenceError("COS connection credentials are unavailable")
    return api_key


def _request_json(
    url: str,
    *,
    method: str,
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
) -> tuple[int, Any]:
    request = urllib.request.Request(
        url,
        data=data,
        headers=headers or {},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
            status = response.getcode()
    except urllib.error.HTTPError as exc:
        raise PersistenceError(f"{method} request failed with status {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise PersistenceError(f"{method} request failed") from exc

    if not body:
        return status, None
    try:
        return status, json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise PersistenceError(f"{method} response was not valid JSON") from exc


def _exchange_iam_token(api_key: str) -> str:
    body = urllib.parse.urlencode(
        {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key,
        }
    ).encode("utf-8")
    status, payload = _request_json(
        IAM_TOKEN_URL,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        data=body,
    )
    if status < 200 or status >= 300 or not isinstance(payload, dict):
        raise PersistenceError("IAM token exchange failed")
    token = payload.get("access_token")
    if not isinstance(token, str) or not token:
        raise PersistenceError("IAM token exchange failed")
    return token


def _cos_object_url(object_key: str) -> str:
    safe_key = "/".join(urllib.parse.quote(part, safe="") for part in object_key.split("/"))
    return f"{COS_ENDPOINT}/{COS_BUCKET}/{safe_key}"


def _persist_record(record_type: str, record_id: str, object_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    api_key = _get_api_key()
    access_token = _exchange_iam_token(api_key)
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    url = _cos_object_url(object_key)

    put_status, _ = _request_json(url, method="PUT", headers=headers, data=body)
    if put_status < 200 or put_status >= 300:
        raise PersistenceError("COS object write failed")

    get_status, read_back = _request_json(url, method="GET", headers=headers)
    if get_status < 200 or get_status >= 300:
        raise PersistenceError("COS object verification failed")
    if read_back != payload:
        raise PersistenceError("COS object verification failed")

    return {
        "status": payload["status"],
        "persisted": True,
        "record_type": record_type,
        "record_id": record_id,
        "object_key": object_key,
        "verified": True,
    }


@tool(
    name="persist_it_request",
    description="Persist one confirmed onboarding IT access request as bounded JSON in IBM Cloud Object Storage.",
    expected_credentials=[CONNECTION_CONTRACT],
)
def persist_it_request(employee_name: str, employee_role: str, required_systems: str) -> dict[str, Any]:
    employee_name = _clean_required(employee_name, "employee_name")
    employee_role = _clean_required(employee_role, "employee_role")
    required_systems = _clean_required(required_systems, "required_systems")
    request_id = _new_id()
    object_key = f"it_requests/{request_id}.json"
    payload = {
        "record_type": "it_request",
        "request_id": request_id,
        "employee_name": employee_name,
        "employee_role": employee_role,
        "required_systems": required_systems,
        "status": "submitted",
        "created_at_utc": _utc_now(),
    }
    return _persist_record("it_request", request_id, object_key, payload)


@tool(
    name="persist_orientation_booking",
    description="Persist one confirmed onboarding orientation booking as bounded JSON in IBM Cloud Object Storage.",
    expected_credentials=[CONNECTION_CONTRACT],
)
def persist_orientation_booking(selected_slot: str) -> dict[str, Any]:
    selected_slot = _clean_required(selected_slot, "selected_slot")
    booking_id = _new_id()
    object_key = f"orientation_bookings/{booking_id}.json"
    payload = {
        "record_type": "orientation_booking",
        "booking_id": booking_id,
        "selected_slot": selected_slot,
        "status": "booked",
        "created_at_utc": _utc_now(),
    }
    return _persist_record("orientation_booking", booking_id, object_key, payload)
