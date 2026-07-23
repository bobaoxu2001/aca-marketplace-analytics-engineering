"""Tests for the metric-registry-grounded LLM SQL ablation condition.

These tests run fully offline: they never require an API key, because the
grounding prompt is assembled before any model call. This lets CI verify that
the only intended difference from the schema-only ``llm_sql`` baseline—the
injected metric-registry block—is present, without spending tokens.
"""

from __future__ import annotations

import duckdb
from agent.llm_registry_sql import SYSTEM_NAME, LLMRegistrySQLBaseline


def _marts_database(tmp_path):
    database = tmp_path / "test.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute("create schema main_marts")
        connection.execute(
            "create table main_marts.fact_premium(state_code varchar, monthly_premium double)"
        )
        connection.execute("insert into main_marts.fact_premium values ('TX', 500.0)")
    return database


def test_skips_gracefully_without_database(tmp_path):
    question = {"id": "QTEST", "question": "test?", "metrics": [], "source_tables": []}
    result = LLMRegistrySQLBaseline(database=tmp_path / "missing.duckdb").answer(question)
    assert result["system"] == SYSTEM_NAME
    assert result["status"] == "skipped_missing_database"


def test_prompt_contains_registry_grounding_block(tmp_path, monkeypatch):
    # Ensure no key is present so the call stops after prompt assembly.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    database = _marts_database(tmp_path)
    question = {
        "id": "Q001",
        "question": "Which states have the highest average monthly premiums?",
        "metrics": ["average_monthly_premium"],
        "source_tables": ["fact_premium"],
    }
    result = LLMRegistrySQLBaseline(database=database).answer(question)

    assert result["status"] == "skipped_missing_api_key"
    # The grounding block must carry the metric name, expression, and caveats.
    assert "average_monthly_premium" in result["prompt"]
    assert "expression:" in result["prompt"]
    assert "caveats:" in result["prompt"]
    # Metric definitions are recorded for provenance.
    assert result["metric_definitions"]
    assert result["metric_definitions"][0]["slug"] == "average_monthly_premium"


def test_prompt_matches_schema_only_baseline_except_for_registry(tmp_path, monkeypatch):
    """The ablation must differ from llm_sql only by the added registry block."""
    from agent.llm_sql import LLMSQLBaseline

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    database = _marts_database(tmp_path)
    question = {
        "id": "Q001",
        "question": "Which states have the highest average monthly premiums?",
        "metrics": ["average_monthly_premium"],
        "source_tables": ["fact_premium"],
    }
    schema_only = LLMSQLBaseline(database=database).answer(question)
    grounded = LLMRegistrySQLBaseline(database=database).answer(question)

    # Both stop at the same gate and share the identical schema context.
    assert schema_only["status"] == grounded["status"] == "skipped_missing_api_key"
    assert "Metric definitions" not in schema_only["prompt"]
    assert "Metric definitions" in grounded["prompt"]
    assert grounded["prompt"].startswith("Question: Which states")


def test_schema_parameter_reads_a_non_default_schema(tmp_path, monkeypatch):
    """A second domain uses a different marts schema (e.g. NYC 311 -> 'marts')."""
    from agent.llm_sql import LLMSQLBaseline

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    database = tmp_path / "nyc.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute("create schema marts")
        connection.execute(
            "create table marts.fact_service_request(unique_key varchar, borough varchar)"
        )
    question = {
        "id": "N001",
        "question": "Which boroughs receive the most service requests?",
        "metrics": [],
        "source_tables": ["fact_service_request"],
    }
    for baseline in (
        LLMSQLBaseline(database=database, schema="marts"),
        LLMRegistrySQLBaseline(database=database, schema="marts"),
    ):
        result = baseline.answer(question)
        assert result["status"] == "skipped_missing_api_key"
        # The schema context is read from the 'marts' schema, not the CMS default.
        assert "fact_service_request.borough" in result["prompt"]
