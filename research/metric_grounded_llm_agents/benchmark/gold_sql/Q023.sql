select facts.state_code, issuers.issuer_name,
       avg(case when facts.is_covered_flag then 1.0 else 0.0 end) as coverage_rate,
       count(*) as benefit_rows
from main_marts.fact_benefit_cost_sharing as facts
join main_marts.dim_issuer as issuers on facts.issuer_key = issuers.issuer_key
group by 1, 2
having benefit_rows >= 100
order by coverage_rate asc
limit 20;
