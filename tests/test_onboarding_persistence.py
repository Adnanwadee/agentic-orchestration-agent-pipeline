import importlib
import ast
import json
from urllib.parse import parse_qs

import pytest


DUMMY_API_KEY = "local-test-api-key"
DUMMY_IAM_TOKEN = "local-test-token"


class FakeResponse:
    def __init__(self, status, payload):
        self.status = status
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8") if self.payload is not None else b""

    def getcode(self):
        return self.status


class HttpRecorder:
    def __init__(self, *, fail_iam=False, fail_put=False, fail_get=False, mismatch=False):
        self.requests = []
        self.fail_iam = fail_iam
        self.fail_put = fail_put
        self.fail_get = fail_get
        self.mismatch = mismatch
        self.last_payload = None

    def urlopen(self, request, timeout):
        self.requests.append(request)
        method = request.get_method()
        url = request.full_url
        if method == "POST":
            if self.fail_iam:
                return FakeResponse(401, {"error": "unauthorized"})
            body = request.data.decode("utf-8")
            assert parse_qs(body)["grant_type"] == ["urn:ibm:params:oauth:grant-type:apikey"]
            assert parse_qs(body)["apikey"] == [DUMMY_API_KEY]
            return FakeResponse(200, {"access_token": DUMMY_IAM_TOKEN})
        if method == "PUT":
            if self.fail_put:
                return FakeResponse(500, {"error": "write failed"})
            self.last_payload = json.loads(request.data.decode("utf-8"))
            return FakeResponse(200, {})
        if method == "GET":
            if self.fail_get:
                return FakeResponse(500, {"error": "read failed"})
            payload = dict(self.last_payload)
            if self.mismatch:
                payload["status"] = "changed"
            return FakeResponse(200, payload)
        raise AssertionError(f"unsupported method {method}")


@pytest.fixture()
def persistence(monkeypatch):
    module = importlib.import_module("tools.onboarding_persistence")
    monkeypatch.setattr(module, "_get_api_key", lambda: DUMMY_API_KEY)
    return module


def install_http(monkeypatch, module, recorder):
    monkeypatch.setattr(module.urllib.request, "urlopen", recorder.urlopen)
    return recorder


def content(response):
    return response.content


def test_tools_use_exact_connection_contract(persistence):
    for tool_obj in [persistence.persist_it_request, persistence.persist_orientation_booking]:
        creds = tool_obj.expected_credentials
        assert len(creds) == 1
        assert creds[0].app_id == "cos_onboarding"
        assert str(creds[0].type) == "api_key_auth"


def test_persist_it_request_writes_bounded_verified_json(monkeypatch, persistence):
    recorder = install_http(monkeypatch, persistence, HttpRecorder())

    result = content(persistence.persist_it_request(
        employee_name="  Ada Lovelace  ",
        employee_role="Data Analyst",
        required_systems="Slack and Jira",
    ))

    assert result["status"] == "submitted"
    assert result["persisted"] is True
    assert result["record_type"] == "it_request"
    assert result["verified"] is True
    assert result["object_key"].startswith("it_requests/")
    assert result["object_key"].endswith(".json")
    assert result["record_id"]
    assert [request.get_method() for request in recorder.requests] == ["POST", "PUT", "GET"]
    put = recorder.requests[1]
    assert put.full_url.startswith(
        "https://s3.eu-de.cloud-object-storage.appdomain.cloud/agentic-onboarding-p2-9g821-01/it_requests/"
    )
    assert put.headers["Content-type"] == "application/json"
    assert put.headers["Authorization"] == f"Bearer {DUMMY_IAM_TOKEN}"
    payload = recorder.last_payload
    assert payload == {
        "record_type": "it_request",
        "request_id": result["record_id"],
        "employee_name": "Ada Lovelace",
        "employee_role": "Data Analyst",
        "required_systems": "Slack and Jira",
        "status": "submitted",
        "created_at_utc": payload["created_at_utc"],
    }
    assert "company_email" not in payload
    assert DUMMY_API_KEY not in json.dumps(result)
    assert DUMMY_IAM_TOKEN not in json.dumps(result)


def test_persist_orientation_booking_writes_only_opaque_slot(monkeypatch, persistence):
    recorder = install_http(monkeypatch, persistence, HttpRecorder())

    result = content(persistence.persist_orientation_booking(selected_slot="slot-opaque-value"))

    assert result["status"] == "booked"
    assert result["record_type"] == "orientation_booking"
    assert result["object_key"].startswith("orientation_bookings/")
    assert recorder.last_payload == {
        "record_type": "orientation_booking",
        "booking_id": result["record_id"],
        "selected_slot": "slot-opaque-value",
        "status": "booked",
        "created_at_utc": recorder.last_payload["created_at_utc"],
    }
    assert "schedule" not in recorder.last_payload
    assert "available_slots" not in recorder.last_payload


def test_record_ids_are_unique(monkeypatch, persistence):
    recorder = install_http(monkeypatch, persistence, HttpRecorder())
    one = content(persistence.persist_it_request("A", "Role", "System"))
    two = content(persistence.persist_it_request("A", "Role", "System"))
    assert one["record_id"] != two["record_id"]
    assert len([r for r in recorder.requests if r.get_method() == "PUT"]) == 2


@pytest.mark.parametrize(
    "kwargs",
    [
        {"employee_name": "", "employee_role": "Role", "required_systems": "System"},
        {"employee_name": "Name", "employee_role": " ", "required_systems": "System"},
        {"employee_name": "Name", "employee_role": "Role", "required_systems": ""},
    ],
)
def test_it_request_requires_only_three_non_empty_business_fields(persistence, kwargs):
    with pytest.raises(ValueError):
        persistence.persist_it_request(**kwargs)


@pytest.mark.parametrize(
    "recorder, expected_message",
    [
        (HttpRecorder(fail_iam=True), "IAM token exchange failed"),
        (HttpRecorder(fail_put=True), "COS object write failed"),
        (HttpRecorder(fail_get=True), "COS object verification failed"),
        (HttpRecorder(mismatch=True), "COS object verification failed"),
    ],
)
def test_failures_are_sanitized(monkeypatch, persistence, recorder, expected_message):
    install_http(monkeypatch, persistence, recorder)
    with pytest.raises(persistence.PersistenceError) as excinfo:
        persistence.persist_it_request("Name", "Role", "System")
    message = str(excinfo.value)
    assert expected_message in message
    assert DUMMY_API_KEY not in message
    assert DUMMY_IAM_TOKEN not in message
    assert "Authorization" not in message


def test_no_unsupported_list_or_delete_api_call(monkeypatch, persistence):
    recorder = install_http(monkeypatch, persistence, HttpRecorder())
    persistence.persist_orientation_booking("slot")
    assert [request.get_method() for request in recorder.requests] == ["POST", "PUT", "GET"]
    assert "?" not in recorder.requests[1].full_url


def test_no_forbidden_third_party_http_or_cos_dependency_imported():
    source = open("tools/onboarding_persistence.py", encoding="utf-8").read()
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    forbidden = {"requests", "httpx", "boto3", "ibm_boto3", "aiohttp"}
    assert imported.isdisjoint(forbidden)
    assert "ibm-cos-sdk" not in source
