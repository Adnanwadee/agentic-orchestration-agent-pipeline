import pytest

from scripts import build_support_triage_evaluation_report as evaluation_report


def test_evaluation_report_selects_frozen_v2_dev_and_verified_heldout():
    report = evaluation_report.build_report()

    assert report["inference_performed"] is False
    assert report["source_selection"]["development"]["path"] == (
        "artifacts/evaluations/support_triage/dev_initial/"
        "20260818T002957.432847Z/development_results.json"
    )
    assert report["source_selection"]["development"]["sha256"] == (
        "9476cb261888adb4abdb2fdb65d52daf7960377ee4efac0913c4388c9ce1c295"
    )
    assert report["source_selection"]["held_out"]["sha256_status"] == "PASS"
    assert report["source_selection"]["held_out"]["sha256"] == evaluation_report.EXPECTED_HELD_OUT_SHA256


def test_evaluation_report_integrity_and_metrics_match_frozen_sources():
    report = evaluation_report.build_report()
    validation = report["validation"]
    metrics = report["metrics"]

    assert validation == {
        "TOTAL_RECORDS": 30,
        "UNIQUE_IDS": 30,
        "DEV_COUNT": 15,
        "HELD_OUT_COUNT": 15,
        "OVERLAP": 0,
        "DROPPED": 0,
        "DUPLICATES": 0,
    }
    assert report["integrity"]["every_record_structured"] is True
    assert metrics["category_correct"] == 27
    assert metrics["category_denominator"] == 30
    assert metrics["category_threshold_result"] == "PASS"
    assert metrics["urgency_correct"] == 25
    assert metrics["urgency_denominator"] == 28
    assert metrics["urgency_threshold_result"] == "PASS"
    assert metrics["human_review_count"] == 10
    assert metrics["auto_routed_count"] == 20
    assert metrics["draft_failed_count"] == 0
    assert metrics["auto_route_correct"] == 18
    assert metrics["auto_route_denominator"] == 20


def test_evaluation_report_telemetry_is_recorded_not_recomputed_inference():
    report = evaluation_report.build_report()
    classifier = report["telemetry"]["classifier"]
    drafter = report["telemetry"]["drafter_recorded_held_out_only"]
    estimate = report["operational_estimate"]

    assert classifier["calls_with_token_usage"] == 30
    assert classifier["total_tokens"] > 0
    assert classifier["latency_sample_count"] == 30
    assert drafter["calls_with_token_usage"] == 12
    assert drafter["total_tokens"] > 0
    assert drafter["latency_sample_count"] == 12
    assert estimate["tickets_per_day"] == 1000
    assert estimate["dollar_cost_status"] == "ESTIMATED_FROM_OFFICIAL_IBM_PUBLIC_RATE"
    assert estimate["expected_drafter_calls_per_day"] == 1000 * (20 / 30)
    assert estimate["pricing"]["source"] == "https://www.ibm.com/products/watsonx-ai/pricing"
    assert estimate["pricing"]["access_date"] == "2026-08-18"
    assert estimate["pricing"]["input_rate_usd_per_million_tokens"] == 0.371
    assert estimate["pricing"]["output_rate_usd_per_million_tokens"] == 1.484
    assert estimate["classifier_cost_per_ticket_usd"] == pytest.approx(0.0003281124)
    assert estimate["drafter_cost_per_actual_call_usd"] == pytest.approx(0.0001203586)
    assert estimate["estimated_model_inference_cost_per_ticket_usd"] == pytest.approx(0.00040835146)
    assert estimate["estimated_model_inference_cost_per_1000_tickets_usd"] == pytest.approx(0.40835146)
