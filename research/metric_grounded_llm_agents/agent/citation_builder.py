"""Build compact data citations for agent answers."""

from __future__ import annotations

from typing import Any


def build_citations(question: dict[str, Any], rows: list[dict[str, Any]], metric_context: str) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    for metric in question.get("metrics", []):
        citations.append({"type": "metric", "id": metric, "detail": metric_context})
    for table in question.get("source_tables", []):
        citations.append({"type": "table", "id": table, "detail": "ACA Marketplace dbt mart"})
    for idx, row in enumerate(rows[:5], start=1):
        citations.append({"type": "result_row", "id": idx, "detail": row})
    return citations

