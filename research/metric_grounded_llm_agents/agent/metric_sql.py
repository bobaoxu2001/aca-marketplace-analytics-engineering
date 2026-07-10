"""Hand-authored metric query templates for the grounded system.

These rules are derived from the metric registry and mart schemas. They are
the planned query generator for the no-key path; they are not answer keys and
do not read benchmark files at runtime.
"""

from __future__ import annotations

from typing import Any


def generate_metric_sql(question: dict[str, Any]) -> str:
    """Generate a safe, inspectable query from the requested metric category."""
    metric = (question.get("metrics") or [""])[0]
    text = question.get("question", "").lower()
    if metric == "average_monthly_premium":
        if "metal" in text:
            return """select p.metal_level, avg(f.monthly_premium) as average_monthly_premium
from fact_premium as f join dim_plan as p using (plan_key)
group by 1 order by 2 desc"""
        return """select state_code, avg(monthly_premium) as average_monthly_premium
from fact_premium group by 1 order by 2 desc limit 10"""
    if metric == "median_silver_premium":
        dimension = "p.issuer_id" if "issuer" in text else "f.rating_area_id" if "rating area" in text else "f.state_code"
        return f"""select {dimension} as dimension, median(f.monthly_premium) as median_silver_premium
from fact_premium as f join dim_plan as p using (plan_key)
where p.metal_level = 'Silver' group by 1 order by 2 desc limit 10"""
    if metric in {"issuer_count_by_county", "plan_count_by_county"}:
        measure = "count(distinct issuer_key)" if metric == "issuer_count_by_county" else "count(distinct plan_key)"
        return f"""select state_code, county_name, {measure} as metric_value
from fact_plan_availability group by 1, 2 order by 3 asc limit 25"""
    if metric == "quality_rating_distribution":
        return """select quality_rating_status, count(*) as plan_count
from fact_plan_quality_rating group by 1 order by 2 desc"""
    if metric == "plan_continuity_status":
        return """select state_code, continuity_status, count(*) as plan_count
from dim_plan_history where is_current = true
group by 1, 2 order by 3 desc"""
    if metric == "benefit_coverage_rate":
        return """select benefit_name, avg(case when is_covered_flag then 1.0 else 0.0 end) as benefit_coverage_rate
from fact_benefit_cost_sharing group by 1 order by 2 desc limit 25"""
    if metric == "average_deductible":
        return """select metal_level, avg(medical_deductible_integrated) as average_deductible
from dim_plan group by 1 order by 2 desc"""
    if metric == "average_oop_max":
        return """select metal_level, avg(medical_oop_max_integrated) as average_oop_max
from dim_plan group by 1 order by 2 desc"""
    if metric == "premium_difference_by_metal":
        return """select p.metal_level, avg(f.monthly_premium) as average_monthly_premium
from fact_premium as f join dim_plan as p using (plan_key)
where p.metal_level in ('Gold', 'Silver') group by 1 order by 2 desc"""
    if metric == "quality_vs_premium":
        return """select q.overall_rating_value, avg(f.monthly_premium) as average_monthly_premium
from fact_plan_quality_rating as q join fact_premium as f using (plan_key)
where q.joins_to_dim_plan = true group by 1 order by 2 desc"""
    raise ValueError(f"No metric template is available for {metric!r}.")
