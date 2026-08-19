import json
import hashlib
from pathlib import Path


SEED_PATH = Path("data/support_tickets_seed.json")
GROUND_TRUTH_PATH = Path("data/support_tickets_ground_truth.json")
SPLIT_PATH = Path("data/support_tickets_split.json")
FREEZE_MANIFEST_PATH = Path("data/support_tickets_freeze_manifest.json")

ALLOWED_CATEGORIES = {"billing", "technical", "account", "general"}
ALLOWED_URGENCIES = {"low", "medium", "high", "critical"}
EXPECTED_IDS = [f"T{index:02d}" for index in range(1, 31)]
EXPECTED_FROZEN_HASHES = {
    "support_tickets_seed": "40901dbbc12ec559ca1b5fc257adb8b1a3406eac08caca66da970e323ff5d7b3",
    "support_tickets_ground_truth": "ef1a83c4a379065917bd4220f4db8eaed6ea3ada2715a4c31a6b1948d2075f81",
    "support_tickets_split": "c56860c4cdf337a9c7c1fa7b465fc2a2bde0703871ed2d3627987c822a798be2",
}

EXPECTED_SUPPLIED_TEXTS = {
    "T01": "I was charged twice for my subscription this month. I need this fixed immediately — I can't afford to have money taken from my account like this.",
    "T02": "Hi, just wondering if you offer student discounts? No rush.",
    "T03": "The application crashes every time I try to export a report. I've tried reinstalling but the problem persists. This is blocking my entire team from closing month-end.",
    "T04": "I forgot my password and the reset email isn't arriving. I've checked spam.",
    "T05": "Everything is down. None of our staff can log in. We have a client presentation in 2 hours.",
    "T06": "How do I change the email address on my account?",
    "T07": "I cancelled my subscription 3 weeks ago but I was still charged this month. I want a refund and I want to know why this happened.",
    "T08": "The export feature is a bit slow sometimes. Not urgent, just flagging it.",
    "T09": "I need to transfer my account to a different email address because I'm changing companies. I also need an invoice for the last 12 months for my accountant.",
    "T10": "it doesnt work fix it",
}

EXPECTED_SUPPLIED_LABELS = {
    "T01": ("billing", None, "high"),
    "T02": ("billing", None, "low"),
    "T03": ("technical", None, "critical"),
    "T04": ("account", None, "medium"),
    "T05": ("technical", None, "critical"),
    "T06": ("account", None, "low"),
    "T07": ("billing", None, "high"),
    "T08": ("technical", None, "low"),
    "T09": ("account", "billing", "medium"),
    "T10": ("technical", None, None),
}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def labels_by_id():
    return {
        record["ticket_id"]: (
            record["expected_category"],
            record["expected_secondary_category"],
            record["expected_urgency"],
        )
        for record in load_json(GROUND_TRUTH_PATH)
    }


def test_seed_dataset_identity_and_sources():
    tickets = load_json(SEED_PATH)
    ids = [ticket["id"] for ticket in tickets]
    texts = [ticket["text"] for ticket in tickets]

    assert len(tickets) == 30
    assert ids == EXPECTED_IDS
    assert len(set(ids)) == 30
    assert len(set(texts)) == 30
    assert [ticket["source"] for ticket in tickets[:10]] == ["supplied"] * 10
    assert [ticket["source"] for ticket in tickets[10:]] == ["synthetic"] * 20


def test_supplied_ticket_texts_and_labels_are_preserved():
    tickets = {ticket["id"]: ticket for ticket in load_json(SEED_PATH)}
    labels = labels_by_id()

    for ticket_id, expected_text in EXPECTED_SUPPLIED_TEXTS.items():
        assert tickets[ticket_id]["text"] == expected_text

    for ticket_id, expected_label in EXPECTED_SUPPLIED_LABELS.items():
        assert labels[ticket_id] == expected_label


def test_ground_truth_contract():
    records = load_json(GROUND_TRUTH_PATH)
    ids = [record["ticket_id"] for record in records]

    assert len(records) == 30
    assert ids == EXPECTED_IDS
    assert len(set(ids)) == 30

    forbidden_fields = {
        "confidence",
        "expected_confidence",
        "review_required",
        "assigned_team",
        "sla",
        "response_draft",
        "reasoning",
        "rationale",
    }
    for record in records:
        assert not forbidden_fields.intersection(record)
        assert record["expected_category"] in ALLOWED_CATEGORIES
        secondary = record["expected_secondary_category"]
        assert secondary is None or secondary in ALLOWED_CATEGORIES
        urgency = record["expected_urgency"]
        assert urgency is None or urgency in ALLOWED_URGENCIES
        assert urgency != "unknown"

    labels = labels_by_id()
    assert labels["T09"] == ("account", "billing", "medium")
    assert labels["T10"] == ("technical", None, None)


def test_split_contract_and_design_fixtures():
    split = load_json(SPLIT_PATH)
    development_ids = split["development_ids"]
    held_out_ids = split["held_out_ids"]

    assert len(development_ids) == 15
    assert len(held_out_ids) == 15
    assert len(set(development_ids)) == 15
    assert len(set(held_out_ids)) == 15
    assert set(development_ids).isdisjoint(held_out_ids)
    assert sorted(development_ids + held_out_ids) == EXPECTED_IDS
    assert "T09" in development_ids
    assert "T10" in development_ids


def test_complete_and_split_category_coverage():
    labels = labels_by_id()
    split = load_json(SPLIT_PATH)

    complete_categories = {label[0] for label in labels.values()}
    development_categories = {
        labels[ticket_id][0] for ticket_id in split["development_ids"]
    }
    held_out_categories = {labels[ticket_id][0] for ticket_id in split["held_out_ids"]}

    assert complete_categories == ALLOWED_CATEGORIES
    assert development_categories == ALLOWED_CATEGORIES
    assert held_out_categories == ALLOWED_CATEGORIES

    development_urgencies = {
        labels[ticket_id][2]
        for ticket_id in split["development_ids"]
        if labels[ticket_id][2] is not None
    }
    held_out_urgencies = {
        labels[ticket_id][2]
        for ticket_id in split["held_out_ids"]
        if labels[ticket_id][2] is not None
    }

    assert development_urgencies == ALLOWED_URGENCIES
    assert held_out_urgencies == ALLOWED_URGENCIES


def test_freeze_manifest_matches_approved_artifacts():
    manifest = load_json(FREEZE_MANIFEST_PATH)
    split = load_json(SPLIT_PATH)

    assert manifest["freeze_version"] == "g3-support-triage-dataset-v1"
    assert manifest["status"] == "frozen"
    assert manifest["supervisor_approval_state"] == "approved"
    assert manifest["ticket_count"] == 30
    assert manifest["development_count"] == 15
    assert manifest["held_out_count"] == 15
    assert manifest["development_ids"] == split["development_ids"]
    assert manifest["held_out_ids"] == split["held_out_ids"]
    assert manifest["null_urgency_metric_rule"]["rule_id"] == (
        "null-urgency-separate-reporting-v1"
    )
    assert manifest["sha256"] == EXPECTED_FROZEN_HASHES
    assert sha256(SEED_PATH) == EXPECTED_FROZEN_HASHES["support_tickets_seed"]
    assert sha256(GROUND_TRUTH_PATH) == EXPECTED_FROZEN_HASHES[
        "support_tickets_ground_truth"
    ]
    assert sha256(SPLIT_PATH) == EXPECTED_FROZEN_HASHES["support_tickets_split"]


def test_t21_freeze_resolution_is_approved():
    tickets = {ticket["id"]: ticket for ticket in load_json(SEED_PATH)}
    labels = labels_by_id()
    split = load_json(SPLIT_PATH)

    assert tickets["T21"]["text"] == "Something looks wrong in my workspace."
    assert labels["T21"] == ("technical", None, None)
    assert "T21" in split["development_ids"]
