select plans.metal_level,
       quantile_cont(premiums.monthly_premium, 0.75) - quantile_cont(premiums.monthly_premium, 0.25) as premium_iqr,
       quantile_cont(premiums.monthly_premium, 0.25) as p25_premium,
       quantile_cont(premiums.monthly_premium, 0.75) as p75_premium
from main_marts.fact_premium as premiums
join main_marts.dim_plan as plans on premiums.plan_key = plans.plan_key
group by 1
order by premium_iqr desc;

