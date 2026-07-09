select benefits.benefit_category,
       avg(case when facts.is_covered_flag then 1.0 else 0.0 end) as coverage_rate,
       count(*) as benefit_rows
from main_marts.fact_benefit_cost_sharing as facts
join main_marts.dim_benefit as benefits on facts.benefit_key = benefits.benefit_key
group by 1
order by coverage_rate desc;

