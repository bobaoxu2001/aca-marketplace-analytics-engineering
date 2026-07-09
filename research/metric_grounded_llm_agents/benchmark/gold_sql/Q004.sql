select state_code, count(distinct issuer_key) as issuer_count
from main_marts.fact_plan_availability
group by 1
order by issuer_count desc, state_code
limit 10;

