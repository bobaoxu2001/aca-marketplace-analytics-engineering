select plans.metal_level, avg(premiums.monthly_premium) as average_monthly_premium, count(*) as premium_rows
from main_marts.fact_premium as premiums
join main_marts.dim_plan as plans on premiums.plan_key = plans.plan_key
group by 1
order by average_monthly_premium desc;
