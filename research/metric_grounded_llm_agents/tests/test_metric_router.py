from agent.metric_registry import MetricRegistry
from agent.metric_router import LexicalMetricRouter


def test_lexical_router_recovers_obvious_metric():
    questions = [{
        "question": "Which states have the highest average monthly premiums?",
        "metrics": ["average_monthly_premium"],
    }]
    router = LexicalMetricRouter.from_questions(questions, MetricRegistry.from_yaml())
    assert router.predict("Where are average monthly premiums greatest?")[0] == "average_monthly_premium"


def test_router_ranking_is_deterministic():
    questions = [{
        "question": "Which benefits have the highest coverage rate?",
        "metrics": ["benefit_coverage_rate"],
    }]
    router = LexicalMetricRouter.from_questions(questions, MetricRegistry.from_yaml())
    assert router.rank("What benefits are covered most often?") == router.rank("What benefits are covered most often?")
