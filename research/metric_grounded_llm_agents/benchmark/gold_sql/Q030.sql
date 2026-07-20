select benefit_name,
       avg(case when has_quantity_limit_flag then 1.0 else 0.0 end) as quantity_limit_rate,
       count(*) as benefit_rows
from main_marts.fact_benefit_cost_sharing
group by 1
having benefit_rows >= 100
order by quantity_limit_rate desc, benefit_rows desc, benefit_name
limit 20;
