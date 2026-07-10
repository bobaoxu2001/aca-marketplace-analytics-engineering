"""Live model baseline that generates SQL from schema context only."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import duckdb

from .model_client import api_key, response_text
from .paths import DEFAULT_DATABASE
from .validators import validate_sql


class LLMSQLBaseline:
    def __init__(self, database: Path = DEFAULT_DATABASE):
        self.database = database

    def _schema_context(self) -> str:
        with duckdb.connect(str(self.database), read_only=True) as connection:
            rows = connection.execute(
                "select table_name, column_name from information_schema.columns "
                "where table_schema = 'main' order by table_name, ordinal_position"
            ).fetchall()
        return "\n".join(f"{table}.{column}" for table, column in rows)

    def answer(self, question: dict[str, Any]) -> dict[str, Any]:
        start = time.perf_counter()
        if not api_key():
            return {"system": "llm_sql_baseline", "question_id": question["id"], "status": "skipped_missing_api_key", "answer": "No configured model API key is available.", "sql": None, "citations": [], "latency_seconds": 0.0}
        if not self.database.exists():
            return {"system": "llm_sql_baseline", "question_id": question["id"], "status": "skipped_missing_database", "answer": "Local DuckDB database is missing.", "sql": None, "citations": [], "latency_seconds": 0.0}
        allowed_tables = set(question.get("source_tables", []))
        sql: str | None = None
        try:
            sql = response_text(
                f"Question: {question['question']}\nSchema:\n{self._schema_context()}",
                instructions="Return one read-only DuckDB SELECT query and no markdown. Use only tables needed for the question.",
            ).strip().removeprefix("```sql").removesuffix("```").strip()
            validation = validate_sql(sql, allowed_tables, question.get("required_terms", []))
            if not validation.passed:
                raise ValueError("; ".join(validation.messages) or "Generated SQL failed validation")
            with duckdb.connect(str(self.database), read_only=True) as connection:
                result = connection.execute(sql)
                columns = [column[0] for column in result.description]
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as exc:
            return {"system": "llm_sql_baseline", "question_id": question["id"], "status": "sql_execution_error", "answer": f"Generated SQL could not execute: {exc}", "sql": sql, "citations": [], "latency_seconds": round(time.perf_counter() - start, 4)}
        return {"system": "llm_sql_baseline", "question_id": question["id"], "status": "ok", "answer": f"Top result: {rows[0] if rows else 'no rows'}", "sql": sql, "rows": rows[:20], "validation": validation.checks, "citations": [], "support_status": "supported_by_result_rows" if rows else "unsupported_no_rows", "latency_seconds": round(time.perf_counter() - start, 4)}
