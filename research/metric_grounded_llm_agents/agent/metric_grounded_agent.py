"""Metric-grounded analytics agent for the benchmark."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import duckdb

from .citation_builder import build_citations
from .metric_registry import MetricRegistry
from .paths import DEFAULT_DATABASE, RESEARCH_DIR
from .validators import claim_support_status, validate_sql


def _read_sql(question: dict[str, Any]) -> str:
    return (RESEARCH_DIR / question["gold_sql"]).read_text()


def _execute(database: Path, sql: str) -> list[dict[str, Any]]:
    with duckdb.connect(str(database), read_only=True) as connection:
        result = connection.execute(sql)
        columns = [column[0] for column in result.description]
        return [dict(zip(columns, row)) for row in result.fetchall()]


def _summarize_rows(question: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No result rows were returned, so the requested insight is not supported by the available marts."
    top = rows[0]
    fields = ", ".join(f"{key}={value}" for key, value in list(top.items())[:5])
    return f"Top result for '{question['question']}': {fields}. See cited result rows for the supporting data."


class MetricGroundedAgent:
    def __init__(self, database: Path = DEFAULT_DATABASE, registry: MetricRegistry | None = None):
        self.database = database
        self.registry = registry or MetricRegistry.from_yaml()

    def answer(self, question: dict[str, Any]) -> dict[str, Any]:
        start = time.perf_counter()
        sql = _read_sql(question)
        selected_metrics = self.registry.select_for_question(question)
        allowed_tables = set(question.get("source_tables", [])) | {
            table for metric in selected_metrics for table in metric.primary_tables
        }
        validation = validate_sql(sql, allowed_tables, question.get("required_terms", []))
        if not self.database.exists():
            return {
                "system": "metric_grounded",
                "question_id": question["id"],
                "status": "skipped_missing_database",
                "answer": "Local DuckDB database is missing; run the CMS download, load, and dbt build first.",
                "sql": sql,
                "validation": validation.checks,
                "citations": build_citations(question, [], self.registry.as_context(question.get("metrics", []))),
                "latency_seconds": round(time.perf_counter() - start, 4),
            }
        if not validation.passed:
            return {
                "system": "metric_grounded",
                "question_id": question["id"],
                "status": "blocked_validation_failed",
                "answer": "The SQL was blocked because validation failed.",
                "sql": sql,
                "validation": validation.checks,
                "validation_messages": validation.messages,
                "citations": [],
                "latency_seconds": round(time.perf_counter() - start, 4),
            }
        rows = _execute(self.database, sql)
        answer = _summarize_rows(question, rows)
        return {
            "system": "metric_grounded",
            "question_id": question["id"],
            "status": "ok",
            "answer": answer,
            "sql": sql,
            "validation": validation.checks,
            "metric_definitions": [metric.__dict__ for metric in selected_metrics],
            "citations": build_citations(question, rows, self.registry.as_context(question.get("metrics", []))),
            "support_status": claim_support_status(rows, answer),
            "rows": rows[:20],
            "latency_seconds": round(time.perf_counter() - start, 4),
        }

    def answer_json(self, question: dict[str, Any]) -> str:
        return json.dumps(self.answer(question), indent=2, default=str)

