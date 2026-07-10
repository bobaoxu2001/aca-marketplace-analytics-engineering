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


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_system: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        by_system.setdefault(result["system"], []).append(result)
    summary: dict[str, Any] = {}
    for system, rows in by_system.items():
        n = max(len(rows), 1)
        executed = [row for row in rows if row.get("status") == "ok"]
        unsupported = [unsupported_claim(row) for row in executed]
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
        }
    return summary
