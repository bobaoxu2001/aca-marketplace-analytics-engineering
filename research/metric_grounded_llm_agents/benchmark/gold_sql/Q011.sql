with coverage as (
    select benefits.benefit_category, plans.metal_level,
           avg(case when facts.is_covered_flag then 1.0 else 0.0 end) as coverage_rate
    from main_marts.fact_benefit_cost_sharing as facts
    join main_marts.dim_benefit as benefits on facts.benefit_key = benefits.benefit_key
    join main_marts.dim_plan as plans on facts.plan_key = plans.plan_key
    group by 1, 2
)
select benefit_category, max(coverage_rate) - min(coverage_rate) as coverage_rate_spread,
       min(coverage_rate) as lowest_coverage_rate, max(coverage_rate) as highest_coverage_rate
from coverage
group by 1
order by coverage_rate_spread desc
limit 10;

