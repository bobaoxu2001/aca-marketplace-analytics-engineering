"""Evaluation metrics for benchmark outputs."""

from __future__ import annotations

from typing import Any


def sql_valid(result: dict[str, Any]) -> int:
    validation = result.get("validation") or {}
    return int(bool(validation) and all(validation.values()))


def citation_coverage(result: dict[str, Any]) -> float:
    citations = result.get("citations") or []
    expected = {"metric", "table", "result_row"}
    present = {citation.get("type") for citation in citations}
    if result.get("status") != "ok":
        return 0.0
    return round(len(expected.intersection(present)) / len(expected), 3)


SKIPPED_STATUSES = {
    "skipped_missing_database",
    "skipped_missing_api_key",
    "skipped_dependency",
    "skipped_missing_gold",
    "skipped_missing_data",
}


def unsupported_claim(result: dict[str, Any]) -> int | None:
    status = result.get("support_status", "")
    if result.get("status") != "ok":
        return None
    return int(status not in {"supported_by_result_rows", "unsupported_claim_marked"})


def traceability_score(result: dict[str, Any]) -> float:
    score = 0.0
    if result.get("sql"):
        score += 0.35
    if result.get("metric_definitions"):
        score += 0.25
    if result.get("citations"):
        score += 0.25
    if result.get("validation"):
        score += 0.15
    return round(score, 3)


def execution_success(result: dict[str, Any]) -> int:
    return int(result.get("status") == "ok")


def _mean(values: list[float | int | None]) -> float | None:
    present = [float(value) for value in values if value is not None]
    return round(sum(present) / len(present), 6) if present else None


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_system: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        by_system.setdefault(result["system"], []).append(result)
    summary: dict[str, Any] = {}
    for system, rows in by_system.items():
        n = max(len(rows), 1)
        executed = [row for row in rows if row.get("status") == "ok"]
        unsupported = [unsupported_claim(row) for row in executed]
        result_metrics = [row.get("result_metrics") or {} for row in rows]
        faithfulness = [row.get("faithfulness_metrics") or {} for row in rows]
        costs = [
            ((row.get("model_call") or {}).get("estimated_cost_usd"))
            for row in rows
        ]
        compared_matches = [
            metric.get("execution_result_match")
            for metric in result_metrics
            if metric.get("execution_result_match") is not None
        ]
        compatible_matches = [
            metric.get("compatible_projection_match")
            for metric in result_metrics
            if metric.get("compatible_projection_match") is not None
        ]
        successful_exact = sum(
            bool((row.get("result_metrics") or {}).get("execution_result_match"))
            for row in rows
        )
        successful_compatible = sum(
            bool((row.get("result_metrics") or {}).get("compatible_projection_match"))
            for row in rows
        )
        summary[system] = {
            "questions": len(rows),
            "ok": sum(row.get("status") == "ok" for row in rows),
            "execution_success_rate": round(sum(execution_success(row) for row in rows) / n, 3),
            "sql_valid_rate": round(sum(sql_valid(row) for row in rows) / n, 3),
            "unsupported_claim_rate": round(sum(unsupported) / len(unsupported), 3) if unsupported else None,
            "citation_coverage": round(sum(citation_coverage(row) for row in rows) / n, 3),
            "traceability_score": round(sum(traceability_score(row) for row in rows) / n, 3),
            "skipped_rate": round(sum(row.get("status") in SKIPPED_STATUSES for row in rows) / n, 3),
            "missing_database_count": sum(row.get("status") == "skipped_missing_database" for row in rows),
            "missing_api_key_count": sum(row.get("status") == "skipped_missing_api_key" for row in rows),
            "sql_error_count": sum(row.get("status") == "sql_execution_error" for row in rows),
            "model_api_error_count": sum(row.get("status") == "model_api_error" for row in rows),
            "router_abstention_count": sum(row.get("status") == "router_abstention" for row in rows),
            "end_to_end_result_match_rate": round(successful_exact / n, 6),
            "end_to_end_compatible_projection_rate": round(successful_compatible / n, 6),
            "execution_result_match_rate": _mean([int(value) for value in compared_matches]),
            "compatible_projection_match_rate": _mean([int(value) for value in compatible_matches]),
            "top_k_overlap": _mean([metric.get("top_k_overlap") for metric in result_metrics]),
            "top_k_precision": _mean([metric.get("top_k_precision") for metric in result_metrics]),
            "top_k_recall": _mean([metric.get("top_k_recall") for metric in result_metrics]),
            "group_match_rate": _mean([metric.get("group_match_rate") for metric in result_metrics]),
            "group_precision": _mean([metric.get("group_precision") for metric in result_metrics]),
            "group_recall": _mean([metric.get("group_recall") for metric in result_metrics]),
            "group_jaccard": _mean([metric.get("group_jaccard") for metric in result_metrics]),
            "mean_numeric_relative_error": _mean([
                metric.get("mean_numeric_relative_error") for metric in result_metrics
            ]),
            "mean_numeric_absolute_error": _mean([
                metric.get("mean_numeric_absolute_error") for metric in result_metrics
            ]),
            "numeric_smape": _mean([metric.get("numeric_smape") for metric in result_metrics]),
            "numeric_claim_faithfulness": _mean([
                metric.get("numeric_claim_faithfulness") for metric in faithfulness
            ]),
            "estimated_cost_usd": round(sum(float(value) for value in costs if value is not None), 8),
            "total_input_tokens": sum(
                int((((row.get("model_call") or {}).get("usage") or {}).get("input_tokens") or 0))
                for row in rows
            ),
            "total_output_tokens": sum(
                int((((row.get("model_call") or {}).get("usage") or {}).get("output_tokens") or 0))
                for row in rows
            ),
            "failure_types": dict(sorted({
                failure: sum(row.get("failure_type") == failure for row in rows)
                for failure in {row.get("failure_type") for row in rows if row.get("failure_type")}
            }.items())),
        }
    return summary
