from pathlib import Path

import yaml
from agent.metric_grounded_agent import MetricGroundedAgent
from agent.metric_registry import MetricRegistry
from agent.metric_sql import generate_metric_sql
from agent.paths import DEFAULT_QUESTIONS
from agent.validators import validate_sql
from evaluation.run_codex_pilot import build_condition_prompts


def test_runtime_agent_modules_do_not_reference_benchmark_answer_files():
    agent_dir = Path(__file__).resolve().parents[1] / "agent"
    for path in agent_dir.glob("*.py"):
        source = path.read_text()
        assert "gold_sql" not in source, path
        assert "gold_answers" not in source, path


def test_metric_template_is_valid_without_benchmark_answers():
    question = {
        "question": "Which states have the highest average monthly premiums?",
        "metrics": ["average_monthly_premium"],
        "source_tables": ["fact_premium"],
    }
    sql = generate_metric_sql(question)
    assert "fact_premium" in sql
    assert validate_sql(sql, {"fact_premium"}).passed


def test_all_benchmark_questions_compile_to_valid_runtime_sql():
    questions = yaml.safe_load(DEFAULT_QUESTIONS.read_text())["questions"]
    registry = MetricRegistry.from_yaml()
    for question in questions:
        selected = registry.select_for_question(question)
        allowed_tables = set(question.get("source_tables", [])) | {
            table for metric in selected for table in metric.primary_tables
        }
        sql = generate_metric_sql(question)
        result = validate_sql(sql, allowed_tables, question.get("required_terms", []))
        assert result.passed, (question["id"], result.messages, sql)


def test_metric_agent_executes_against_dbt_marts_schema(tmp_path):
    import duckdb

    database = tmp_path / "test.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute("create schema main_marts")
        connection.execute("create table main_marts.fact_premium(state_code varchar, monthly_premium double)")
        connection.execute("insert into main_marts.fact_premium values ('TX', 500.0)")
    question = {
        "id": "QTEST",
        "question": "Which states have the highest average monthly premiums?",
        "metrics": ["average_monthly_premium"],
        "source_tables": ["fact_premium"],
    }
    result = MetricGroundedAgent(database=database).answer(question)
    assert result["status"] == "ok"
    assert result["rows"][0]["state_code"] == "TX"


def test_direct_codex_prompt_does_not_require_a_database(tmp_path):
    questions = [{"id": "QTEST", "question": "What is the result?"}]
    prompts = build_condition_prompts(
        questions,
        tmp_path / "database-does-not-exist.duckdb",
        {"direct_codex_batched"},
    )

    assert len(prompts) == 1
    assert prompts[0][0] == "direct_codex_batched"
    assert "QTEST: What is the result?" in prompts[0][1]
