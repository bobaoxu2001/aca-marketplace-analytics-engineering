select state_code, count(distinct plan_key) as distinct_plan_count
from main_marts.fact_plan_availability
group by 1
order by distinct_plan_count desc;
