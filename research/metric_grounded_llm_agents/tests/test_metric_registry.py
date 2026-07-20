from agent.metric_registry import MetricRegistry


def test_metric_registry_loads_metrics():
    registry = MetricRegistry.from_yaml()
    metric = registry.get("average_monthly_premium")
    assert metric.name == "Average monthly premium"
    assert "fact_premium" in metric.primary_tables


def test_metric_context_mentions_selected_metric():
    registry = MetricRegistry.from_yaml()
    context = registry.as_context(["issuer_count_by_county"])
    assert "Issuer count by county" in context
