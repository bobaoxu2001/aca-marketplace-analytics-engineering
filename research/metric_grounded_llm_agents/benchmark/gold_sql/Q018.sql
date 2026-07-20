select availability.state_code, issuers.issuer_name,
       count(distinct availability.plan_key) as distinct_plan_count
from main_marts.fact_plan_availability as availability
join main_marts.dim_issuer as issuers on availability.issuer_key = issuers.issuer_key
group by 1, 2
order by distinct_plan_count desc
limit 20;
