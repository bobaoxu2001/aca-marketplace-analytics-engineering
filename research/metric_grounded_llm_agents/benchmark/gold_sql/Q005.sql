select plans.metal_level, count(distinct availability.plan_key) as distinct_plan_count
from main_marts.fact_plan_availability as availability
join main_marts.dim_plan as plans on availability.plan_key = plans.plan_key
group by 1
order by distinct_plan_count desc;

