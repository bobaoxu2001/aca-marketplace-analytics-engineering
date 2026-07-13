from evaluation.result_metrics import compare_result_rows, numeric_claim_faithfulness


def test_projection_match_does_not_count_as_strict_complete_match():
    predicted = [
        {"state_code": "TX", "average_monthly_premium": 501.0},
        {"state_code": "FL", "average_monthly_premium": 450.0},
    ]
    gold = [
        {"state_code": "TX", "average_monthly_premium": 501.0, "premium_rows": 100},
        {"state_code": "FL", "average_monthly_premium": 450.0, "premium_rows": 80},
    ]
    result = compare_result_rows(predicted, gold)
    assert result["execution_result_match"] is False
    assert result["compatible_projection_match"] is True
    assert result["top_k_overlap"] == 1.0
    assert result["group_match_rate"] == 1.0
    assert result["mean_numeric_relative_error"] == 0.0
    assert result["numeric_smape"] == 0.0
    assert result["mean_numeric_absolute_error"] == 0.0


def test_strict_result_match_requires_same_schema_and_values():
    rows = [{"state_code": "TX", "premium": 501.0}]
    result = compare_result_rows(rows, rows)
    assert result["execution_result_match"] is True
    assert result["strict_columns_match"] is True


def test_strict_match_ignores_row_order_but_reports_rank_order_separately():
    predicted = [{"state": "TX", "metric": 1}, {"state": "CA", "metric": 1}]
    gold = list(reversed(predicted))
    result = compare_result_rows(predicted, gold)
    assert result["execution_result_match"] is True
    assert result["rank_order_match"] is False


def test_positional_wrong_measure_is_not_strict_match():
    predicted = [{"state_code": "TX", "issuer_count": 10}]
    gold = [{"state_code": "TX", "plan_count": 10}]
    result = compare_result_rows(predicted, gold)
    assert result["execution_result_match"] is False
    assert result["compatible_projection_match"] is True


def test_group_f1_penalizes_extra_groups_and_top_k_penalizes_short_output():
    predicted = [
        {"state_code": "TX", "metric": 3},
        {"state_code": "EXTRA", "metric": 2},
    ]
    gold = [
        {"state_code": "TX", "metric": 3},
        {"state_code": "CA", "metric": 2},
        {"state_code": "FL", "metric": 1},
    ]
    result = compare_result_rows(predicted, gold, top_k=3)
    assert result["group_precision"] == 0.5
    assert result["group_recall"] == 0.333333
    assert result["group_match_rate"] == 0.4
    assert result["top_k_recall"] == 0.333333
    assert result["top_k_overlap"] == 0.25


def test_result_comparison_detects_rank_and_numeric_error():
    predicted = [
        {"state_code": "FL", "metric": 400.0},
        {"state_code": "TX", "metric": 500.0},
    ]
    gold = [
        {"state_code": "TX", "metric": 500.0},
        {"state_code": "CA", "metric": 450.0},
    ]
    result = compare_result_rows(predicted, gold, top_k=1)
    assert result["execution_result_match"] is False
    assert result["top_k_overlap"] == 0.0
    assert result["group_match_rate"] == 0.5


def test_numeric_claim_faithfulness_uses_evidence_values():
    result = numeric_claim_faithfulness(
        "Texas has a premium of $501.00 across 100 rows.",
        [{"state_code": "TX", "premium": 501.0, "premium_rows": 100}],
    )
    assert result["numeric_claim_count"] == 2
    assert result["numeric_claim_faithfulness"] == 1.0


def test_qualitative_answer_requires_human_review():
    result = numeric_claim_faithfulness("Texas ranks highest.", [{"state_code": "TX"}])
    assert result["numeric_claim_faithfulness"] is None
    assert result["qualitative_review_required"] is True
