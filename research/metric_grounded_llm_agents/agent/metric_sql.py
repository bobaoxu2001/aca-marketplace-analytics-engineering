"""Hand-authored metric query templates for the grounded system.

These rules are derived from the metric registry and mart schemas. They are
the planned query generator for the no-key path; they are not answer keys and
do not read benchmark files at runtime.
"""

from __future__ import annotations

from typing import Any


def generate_metric_sql(question: dict[str, Any]) -> str:
    """Generate a safe query from metric tags plus explicit question semantics.

    This is a transparent rule-based upper bound: benchmark metadata supplies
    the metric route, while the question text determines grain, filters, and
    ranking. It intentionally does not read gold SQL or gold answers.
    """
    metrics = question.get("metrics") or [""]
    metric = metrics[0]
    text = question.get("question", "").lower()
    if {"quality_rating_distribution", "average_deductible"}.issubset(metrics) and "deductible" in text:
        return """select quality_rating_status,
avg(medical_deductible_integrated) as average_deductible, count(*) as quality_rows
from fact_plan_quality_rating where medical_deductible_integrated is not null
group by 1 order by average_deductible desc"""
    if "premium" in text and any(term in text for term in ("variation", "variability", "atypical")):
        return """select state_code, avg(monthly_premium) as average_monthly_premium,
stddev_samp(monthly_premium) as premium_stddev, min(monthly_premium) as min_premium,
max(monthly_premium) as max_premium, count(*) as premium_rows
from fact_premium group by 1 order by premium_stddev desc limit 10"""
    if "interquartile" in text:
        return """select p.metal_level,
quantile_cont(f.monthly_premium, 0.75) - quantile_cont(f.monthly_premium, 0.25) as premium_iqr,
quantile_cont(f.monthly_premium, 0.25) as p25_premium,
quantile_cont(f.monthly_premium, 0.75) as p75_premium
from fact_premium as f join dim_plan as p using (plan_key)
group by 1 order by premium_iqr desc"""
    if metric == "average_monthly_premium":
        if "metal" in text:
            return """select p.metal_level, avg(f.monthly_premium) as average_monthly_premium
from fact_premium as f join dim_plan as p using (plan_key)
group by 1 order by 2 desc"""
        return """select state_code, avg(monthly_premium) as average_monthly_premium
from fact_premium group by 1 order by 2 desc limit 10"""
    if metric == "median_silver_premium":
        if "issuer" in text:
            return """select f.state_code, i.issuer_name,
median(f.monthly_premium) as median_silver_premium, count(*) as premium_rows
from fact_premium as f join dim_plan as p using (plan_key)
join dim_issuer as i on f.issuer_key = i.issuer_key
where p.metal_level = 'Silver' group by 1, 2 having count(*) >= 20
order by median_silver_premium desc, f.state_code, i.issuer_name limit 20"""
        if "rating area" in text:
            return """select f.state_code, f.rating_area_id,
median(f.monthly_premium) as median_silver_premium, count(*) as premium_rows
from fact_premium as f join dim_plan as p using (plan_key)
where p.metal_level = 'Silver' group by 1, 2
order by median_silver_premium desc, f.state_code, f.rating_area_id limit 20"""
        return """select f.state_code, median(f.monthly_premium) as median_silver_premium,
count(*) as premium_rows from fact_premium as f join dim_plan as p using (plan_key)
where p.metal_level = 'Silver' group by 1 order by median_silver_premium desc limit 10"""
    if metric in {"issuer_count_by_county", "plan_count_by_county"}:
        if metric == "issuer_count_by_county" and "competition" in text and "county" not in text:
            return """select state_code, count(distinct issuer_key) as issuer_count
from fact_plan_availability group by 1 order by issuer_count desc, state_code limit 10"""
        if metric == "plan_count_by_county" and "metal" in text:
            return """select p.metal_level, count(distinct f.plan_key) as distinct_plan_count
from fact_plan_availability as f join dim_plan as p using (plan_key)
group by 1 order by distinct_plan_count desc"""
        if "plan" in text and "issuer" in text and any(term in text for term in ("many", "numerous")) and any(term in text for term in ("few", "small number")):
            return """select f.state_code, g.county_name, g.service_area_id,
count(distinct f.plan_key) as plan_count, count(distinct f.issuer_key) as issuer_count,
count(distinct f.plan_key) * 1.0 / nullif(count(distinct f.issuer_key), 0) as plans_per_issuer
from fact_plan_availability as f join dim_geography as g using (geography_key)
where g.geography_type = 'service_area_county' group by 1, 2, 3
having count(distinct f.plan_key) >= 10 and count(distinct f.issuer_key) <= 2
order by plans_per_issuer desc, plan_count desc, f.state_code, g.county_name, g.service_area_id limit 20"""
        if metric == "issuer_count_by_county" and ("one issuer" in text or "single-issuer" in text):
            return """with county_competition as (
select state_code, county_name, count(distinct issuer_key) as issuer_count
from fact_plan_availability group by 1, 2)
select state_code, count(*) as one_issuer_counties from county_competition
where issuer_count = 1 group by 1 order by one_issuer_counties desc"""
        if metric == "plan_count_by_county" and "issuer" in text and any(term in text for term in ("distinct", "unique", "number")):
            return """select f.state_code, i.issuer_name, count(distinct f.plan_key) as distinct_plan_count
from fact_plan_availability as f join dim_issuer as i using (issuer_key)
group by 1, 2 order by distinct_plan_count desc limit 20"""
        if metric == "plan_count_by_county" and "state" in text and any(term in text for term in ("distinct", "unique", "number")):
            return """select state_code, count(distinct plan_key) as distinct_plan_count
from fact_plan_availability group by 1 order by distinct_plan_count desc"""
        if "plan" in text and "issuer" in text and any(term in text for term in ("many", "numerous")) and any(term in text for term in ("few", "small number")):
            return """select f.state_code, g.county_name, g.service_area_id,
count(distinct f.plan_key) as plan_count, count(distinct f.issuer_key) as issuer_count,
count(distinct f.plan_key) * 1.0 / nullif(count(distinct f.issuer_key), 0) as plans_per_issuer
from fact_plan_availability as f join dim_geography as g using (geography_key)
where g.geography_type = 'service_area_county' group by 1, 2, 3
having count(distinct f.plan_key) >= 10 and count(distinct f.issuer_key) <= 2
order by plans_per_issuer desc, plan_count desc, f.state_code, g.county_name, g.service_area_id limit 20"""
        if metric == "issuer_count_by_county" and any(term in text for term in ("limited", "few")) and "choice" in text:
            return """select f.state_code, g.county_name, g.service_area_id,
count(distinct f.issuer_key) as issuer_count, count(distinct f.plan_key) as plan_count
from fact_plan_availability as f join dim_geography as g using (geography_key)
where g.geography_type = 'service_area_county' group by 1, 2, 3
having count(distinct f.issuer_key) <= 1 order by plan_count asc, f.state_code, g.county_name limit 25"""
        measure = "count(distinct issuer_key)" if metric == "issuer_count_by_county" else "count(distinct plan_key)"
        return f"""select state_code, county_name, {measure} as metric_value
from fact_plan_availability group by 1, 2 order by 3 asc limit 25"""
    if metric == "quality_rating_distribution" and "deductible" in text:
        return """select quality_rating_status,
avg(medical_deductible_integrated) as average_deductible, count(*) as quality_rows
from fact_plan_quality_rating where medical_deductible_integrated is not null
group by 1 order by average_deductible desc"""
    if metric == "quality_rating_distribution":
        return """select quality_rating_status, overall_rating_value, count(*) as quality_rows
from fact_plan_quality_rating group by 1, 2 order by quality_rows desc"""
    if metric == "plan_continuity_status":
        if "issuer" in text and any(term in text for term in ("worst", "poorest")):
            return """select h.state_code, coalesce(i.issuer_name, h.current_issuer_id, h.previous_issuer_id) as issuer_label,
sum(case when h.continuity_status in ('new_or_not_in_crosswalk', 'discontinued_or_no_2026_crosswalk') then 1 else 0 end) as non_continuing_rows,
count(*) as total_history_rows,
sum(case when h.continuity_status in ('new_or_not_in_crosswalk', 'discontinued_or_no_2026_crosswalk') then 1 else 0 end) * 1.0 / nullif(count(*), 0) as non_continuity_rate
from dim_plan_history as h left join dim_issuer as i using (issuer_key)
group by 1, 2 having count(*) >= 5
order by non_continuity_rate desc, non_continuing_rows desc, h.state_code, issuer_label limit 20"""
        if "new" in text and any(term in text for term in ("share", "proportion")):
            return """select state_code,
sum(case when continuity_status = 'new_or_not_in_crosswalk' then 1 else 0 end) as new_current_plans,
sum(case when is_current then 1 else 0 end) as current_history_rows,
sum(case when continuity_status = 'new_or_not_in_crosswalk' then 1 else 0 end) * 1.0 /
nullif(sum(case when is_current then 1 else 0 end), 0) as new_plan_share
from dim_plan_history group by 1 having sum(case when is_current then 1 else 0 end) > 0
order by new_plan_share desc, state_code limit 20"""
        if "crosswalk" in text and "reason" in text:
            return """select representative_reason_for_crosswalk, representative_crosswalk_level,
count(*) as history_rows from dim_plan_history
where representative_reason_for_crosswalk is not null group by 1, 2 order by history_rows desc limit 20"""
        return """select state_code, continuity_status, count(*) as plan_count
from dim_plan_history group by 1, 2 order by 3 desc limit 20"""
    if metric == "benefit_coverage_rate":
        if "metal" in text and any(term in text for term in ("differ", "difference", "vary")):
            return """with coverage as (
select b.benefit_category, p.metal_level,
avg(case when f.is_covered_flag then 1.0 else 0.0 end) as coverage_rate
from fact_benefit_cost_sharing as f join dim_benefit as b using (benefit_key)
join dim_plan as p using (plan_key) group by 1, 2)
select benefit_category, max(coverage_rate) - min(coverage_rate) as coverage_rate_spread,
min(coverage_rate) as lowest_coverage_rate, max(coverage_rate) as highest_coverage_rate
from coverage group by 1 order by coverage_rate_spread desc limit 10"""
        if "categor" in text and any(term in text for term in ("highest", "greatest")):
            return """select b.benefit_category,
avg(case when f.is_covered_flag then 1.0 else 0.0 end) as coverage_rate, count(*) as benefit_rows
from fact_benefit_cost_sharing as f join dim_benefit as b using (benefit_key)
group by 1 order by coverage_rate desc"""
        if "issuer" in text and any(term in text for term in ("lowest", "smallest")):
            return """select f.state_code, i.issuer_name,
avg(case when f.is_covered_flag then 1.0 else 0.0 end) as coverage_rate, count(*) as benefit_rows
from fact_benefit_cost_sharing as f join dim_issuer as i using (issuer_key)
group by 1, 2 having count(*) >= 100 order by coverage_rate asc limit 20"""
        if "quantity limits" in text:
            return """select benefit_name,
avg(case when has_quantity_limit_flag then 1.0 else 0.0 end) as quantity_limit_rate,
count(*) as benefit_rows from fact_benefit_cost_sharing group by 1
having count(*) >= 100 order by quantity_limit_rate desc, benefit_rows desc, benefit_name limit 20"""
        return """select benefit_name, avg(case when is_covered_flag then 1.0 else 0.0 end) as benefit_coverage_rate
from fact_benefit_cost_sharing group by 1 order by 2 desc limit 25"""
    if metric == "average_deductible":
        return """select metal_level, avg(medical_deductible_integrated) as average_deductible
from dim_plan where medical_deductible_integrated is not null group by 1 order by 2 desc"""
    if metric == "average_oop_max":
        dimension = "plan_type" if "plan types" in text else "metal_level"
        return f"""select {dimension}, avg(medical_oop_max_integrated) as average_oop_max
from dim_plan where medical_oop_max_integrated is not null group by 1 order by 2 desc"""
    if metric == "premium_difference_by_metal":
        return """with metal_state as (
select f.state_code, p.metal_level, avg(f.monthly_premium) as avg_premium
from fact_premium as f join dim_plan as p using (plan_key)
where p.metal_level in ('Gold', 'Silver') group by 1, 2)
select gold.state_code, gold.avg_premium as gold_average_premium,
silver.avg_premium as silver_average_premium,
gold.avg_premium - silver.avg_premium as gold_silver_gap
from metal_state as gold join metal_state as silver using (state_code)
where gold.metal_level = 'Gold' and silver.metal_level = 'Silver'
order by gold_silver_gap desc limit 20"""
    if metric == "quality_vs_premium":
        if "which states" in text:
            return """with plan_premium as (
select plan_key, avg(monthly_premium) as average_monthly_premium
from fact_premium group by 1)
select q.state_code, count(distinct q.plan_key) as rated_joined_plan_count,
avg(p.average_monthly_premium) as average_rated_plan_premium
from fact_plan_quality_rating as q join plan_premium as p using (plan_key)
where q.quality_rating_status = 'rated' group by 1
order by average_rated_plan_premium desc limit 20"""
        return """with plan_premium as (
select plan_key, avg(monthly_premium) as average_monthly_premium
from fact_premium group by 1)
select q.overall_rating_value, count(distinct q.plan_key) as joined_plan_count,
avg(p.average_monthly_premium) as average_monthly_premium
from fact_plan_quality_rating as q join plan_premium as p using (plan_key)
where q.overall_rating_numeric is not null group by 1
order by try_cast(q.overall_rating_value as integer)"""
    raise ValueError(f"No metric template is available for {metric!r}.")
