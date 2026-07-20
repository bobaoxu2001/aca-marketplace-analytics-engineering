from evaluation.metrics import citation_coverage, execution_success, sql_valid, summarize, traceability_score, unsupported_claim


def test_sql_valid_requires_all_checks_true():
    assert sql_valid({"validation": {"a": True, "b": True}}) == 1
    assert sql_valid({"validation": {"a": True, "b": False}}) == 0


def test_citation_coverage_counts_metric_table_and_rows():
    result = {
        "status": "ok",
        "citations": [{"type": "metric"}, {"type": "table"}, {"type": "result_row"}],
    }
    assert citation_coverage(result) == 1.0


def test_traceability_score_rewards_sql_metrics_citations_validation():
    result = {"sql": "select 1", "metric_definitions": [1], "citations": [1], "validation": {"ok": True}}
    assert traceability_score(result) == 1.0


def test_execution_success_requires_ok_status():
    assert execution_success({"status": "ok"}) == 1
    assert execution_success({"status": "skipped_missing_database"}) == 0


def test_skipped_runs_are_excluded_from_unsupported_claims():
    assert unsupported_claim({"status": "skipped_missing_database"}) is None
    summary = summarize([
        {"system": "direct_llm", "status": "skipped_missing_api_key"},
        {"system": "metric_grounded", "status": "skipped_missing_database"},
    ])
    assert summary["direct_llm"]["unsupported_claim_rate"] is None
    assert summary["direct_llm"]["missing_api_key_count"] == 1
    assert summary["metric_grounded"]["missing_database_count"] == 1
    assert summary["metric_grounded"]["skipped_rate"] == 1.0
    assert summary["direct_llm"]["execution_result_match_rate"] is None
    assert summary["direct_llm"]["end_to_end_result_match_rate"] == 0.0


def test_summary_aggregates_result_usage_and_cost_metrics():
    summary = summarize([{
        "system": "metric_grounded",
        "status": "ok",
        "support_status": "supported_by_result_rows",
        "result_metrics": {
            "execution_result_match": True,
            "top_k_overlap": 0.8,
            "group_match_rate": 0.9,
            "mean_numeric_relative_error": 0.05,
        },
        "faithfulness_metrics": {"numeric_claim_faithfulness": 1.0},
        "model_call": {
            "estimated_cost_usd": 0.001,
            "usage": {"input_tokens": 100, "output_tokens": 20},
        },
    }])["metric_grounded"]
    assert summary["execution_result_match_rate"] == 1.0
    assert summary["top_k_overlap"] == 0.8
    assert summary["total_input_tokens"] == 100
    assert summary["estimated_cost_usd"] == 0.001
