from pathlib import Path

from agent.metric_sql import generate_metric_sql
from agent.validators import validate_sql


def test_runtime_agent_modules_do_not_reference_benchmark_answer_files():
    agent_dir = Path(__file__).resolve().parents[1] / "agent"
    for path in agent_dir.glob("*.py"):
        assert "gold_sql" not in path.read_text(), path


def test_metric_template_is_valid_without_benchmark_answers():
    question = {
        "question": "Which states have the highest average monthly premiums?",
        "metrics": ["average_monthly_premium"],
        "source_tables": ["fact_premium"],
    }
    sql = generate_metric_sql(question)
    assert "fact_premium" in sql
    assert validate_sql(sql, {"fact_premium"}).passed
