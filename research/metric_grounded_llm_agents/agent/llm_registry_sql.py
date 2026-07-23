"""Metric-registry-grounded model baseline that generates SQL from schema plus
explicit metric definitions.

This condition isolates the causal effect of metric grounding on a learned SQL
generator. It is identical to :class:`agent.llm_sql.LLMSQLBaseline` in model,
task, schema context, validation policy, and permitted-table gate; the only
difference is that the prompt additionally supplies the benchmark's oracle
metric definitions (expression, primary tables, allowed dimensions, and caveats)
for the question. Comparing ``llm_sql`` (schema only) with ``llm_registry_sql``
(schema plus registry) therefore estimates how much an explicit semantic
registry changes an LLM's strict result agreement, holding everything else
fixed. Because the metric labels come from the benchmark, this is an
oracle-metric-conditioned baseline, directly comparable to the oracle-routed
deterministic compiler.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import duckdb

from .metric_registry import MetricDefinition, MetricRegistry
from .model_client import api_key, response_call
from .paths import DEFAULT_DATABASE
from .validators import validate_sql

SYSTEM_NAME = "llm_registry_sql"


def _registry_context(metrics: list[MetricDefinition]) -> str:
    """Render full metric definitions for the prompt grounding block."""
    if not metrics:
        return "(no registry metric is annotated for this question)"
    blocks: list[str] = []
    for metric in metrics:
        dimensions = ", ".join(metric.allowed_dimensions) or "(none listed)"
        caveats = "; ".join(metric.caveats) or "(none listed)"
        blocks.append(
            f"- {metric.name} ({metric.slug})\n"
            f"    expression: {metric.expression}\n"
            f"    primary_tables: {', '.join(metric.primary_tables) or '(none listed)'}\n"
            f"    allowed_dimensions: {dimensions}\n"
            f"    caveats: {caveats}"
        )
    return "\n".join(blocks)


class LLMRegistrySQLBaseline:
    """LLM SQL generation with an explicit metric-registry grounding block."""

    def __init__(self, database: Path = DEFAULT_DATABASE, registry: MetricRegistry | None = None, schema: str = "main_marts"):
        self.database = database
        self.registry = registry or MetricRegistry.from_yaml()
        self.schema = schema

    def _schema_context(self) -> str:
        with duckdb.connect(str(self.database), read_only=True) as connection:
            rows = connection.execute(
                "select table_name, column_name from information_schema.columns "
                "where table_schema = ? order by table_name, ordinal_position",
                [self.schema],
            ).fetchall()
        return "\n".join(f"{table}.{column}" for table, column in rows)

    def answer(self, question: dict[str, Any]) -> dict[str, Any]:
        start = time.perf_counter()
        if not self.database.exists():
            return {
                "system": SYSTEM_NAME,
                "question_id": question["id"],
                "status": "skipped_missing_database",
                "answer": "Local DuckDB database is missing.",
                "sql": None,
                "citations": [],
                "latency_seconds": 0.0,
            }
        allowed_tables = set(question.get("source_tables", []))
        selected_metrics = self.registry.select_for_question(question)
        registry_block = _registry_context(selected_metrics)
        prompt = (
            f"Question: {question['question']}\n"
            f"Schema:\n{self._schema_context()}\n"
            f"Metric definitions (authoritative; compute exactly these):\n{registry_block}"
        )
        instructions = (
            "Return one read-only DuckDB SELECT query and no markdown. "
            "Use only tables needed for the question. Compute the measure, grain, "
            "grouping, and filters implied by the provided metric definitions and "
            "respect their caveats."
        )
        base = {
            "system": SYSTEM_NAME,
            "question_id": question["id"],
            "prompt": prompt,
            "instructions": instructions,
            "metric_definitions": [metric.__dict__ for metric in selected_metrics],
        }
        if not api_key():
            return {
                **base,
                "status": "skipped_missing_api_key",
                "answer": "No configured model API key is available.",
                "sql": None,
                "citations": [],
                "latency_seconds": round(time.perf_counter() - start, 4),
            }
        try:
            call = response_call(prompt, instructions=instructions)
            sql = call.text.strip().removeprefix("```sql").removesuffix("```").strip()
        except Exception as exc:  # noqa: BLE001 - report any model/transport failure as a failure class
            return {
                **base,
                "status": "model_api_error",
                "answer": f"Model SQL generation failed: {exc}",
                "sql": None,
                "citations": [],
                "failure_type": type(exc).__name__,
                "latency_seconds": round(time.perf_counter() - start, 4),
            }
        try:
            validation = validate_sql(sql, allowed_tables, question.get("required_terms", []))
            if not validation.passed:
                raise ValueError("; ".join(validation.messages) or "Generated SQL failed validation")
            with duckdb.connect(str(self.database), read_only=True) as connection:
                connection.execute(f"set schema '{self.schema}'")
                result = connection.execute(sql)
                columns = [column[0] for column in result.description]
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as exc:  # noqa: BLE001 - validation or execution failure class
            return {
                **base,
                "status": "sql_execution_error",
                "answer": f"Generated SQL could not execute: {exc}",
                "sql": sql,
                "citations": [],
                "failure_type": type(exc).__name__,
                "model_call": call.metadata,
                "latency_seconds": round(time.perf_counter() - start, 4),
            }
        return {
            **base,
            "status": "ok",
            "answer": f"Top result: {rows[0] if rows else 'no rows'}",
            "sql": sql,
            "rows": rows,
            "validation": validation.checks,
            "citations": [],
            "model_call": call.metadata,
            "support_status": "supported_by_result_rows" if rows else "unsupported_no_rows",
            "latency_seconds": round(time.perf_counter() - start, 4),
        }
