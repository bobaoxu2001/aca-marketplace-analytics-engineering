"""Metric-constrained analytics agent using explicit, non-oracle query rules."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import duckdb

from typing import Callable

from .citation_builder import build_citations
from .metric_registry import MetricRegistry
from .metric_sql import generate_metric_sql
from .paths import DEFAULT_DATABASE
from .validators import claim_support_status, validate_sql


def _execute(database: Path, sql: str, schema: str = "main_marts") -> list[dict[str, Any]]:
    with duckdb.connect(str(database), read_only=True) as connection:
        connection.execute(f"set schema '{schema}'")
        result = connection.execute(sql)
        columns = [column[0] for column in result.description]
        return [dict(zip(columns, row)) for row in result.fetchall()]


class MetricGroundedAgent:
    """Runs a documented metric-template generator over approved mart tables."""

    def __init__(
        self,
        database: Path = DEFAULT_DATABASE,
        registry: MetricRegistry | None = None,
        schema: str = "main_marts",
        compiler: Callable[[dict[str, Any]], str] = generate_metric_sql,
    ):
        self.database = database
        self.registry = registry or MetricRegistry.from_yaml()
        self.schema = schema
        self.compiler = compiler

    def answer(self, question: dict[str, Any]) -> dict[str, Any]:
        start = time.perf_counter()
        selected_metrics = self.registry.select_for_question(question)
        allowed_tables = set(question.get("source_tables", [])) | {
            table for metric in selected_metrics for table in metric.primary_tables
        }
        sql = self.compiler(question)
        validation = validate_sql(sql, allowed_tables, question.get("required_terms", []))
        base = {
            "system": "metric_grounded",
            "question_id": question["id"],
            "sql": sql,
            "validation": validation.checks,
            "metric_definitions": [metric.__dict__ for metric in selected_metrics],
        }
        if not self.database.exists():
            return {
                **base,
                "status": "skipped_missing_database",
                "answer": "Local DuckDB database is missing; run the CMS download, load, and dbt build first.",
                "citations": build_citations(question, [], self.registry.as_context(question.get("metrics", []))),
                "latency_seconds": round(time.perf_counter() - start, 4),
            }
        if not validation.passed:
            return {
                **base,
                "status": "blocked_validation_failed",
                "answer": "The metric-template SQL was blocked by validation.",
                "validation_messages": validation.messages,
                "citations": [],
                "latency_seconds": round(time.perf_counter() - start, 4),
            }
        try:
            rows = _execute(self.database, sql, self.schema)
        except duckdb.Error as exc:
            return {
                **base,
                "status": "sql_execution_error",
                "answer": f"Metric-template SQL could not execute: {exc}",
                "failure_type": type(exc).__name__,
                "citations": [],
                "latency_seconds": round(time.perf_counter() - start, 4),
            }
        answer = f"Top result: {rows[0]}." if rows else "No result rows were returned."
        return {
            **base,
            "status": "ok",
            "answer": answer,
            "citations": build_citations(question, rows, self.registry.as_context(question.get("metrics", []))),
            "support_status": claim_support_status(rows, answer),
            "rows": rows,
            "latency_seconds": round(time.perf_counter() - start, 4),
        }

    def answer_json(self, question: dict[str, Any]) -> str:
        return json.dumps(self.answer(question), indent=2, default=str)
