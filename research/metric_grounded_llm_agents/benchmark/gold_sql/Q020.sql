select premiums.state_code, premiums.rating_area_id,
       median(premiums.monthly_premium) as median_silver_premium,
       count(*) as premium_rows
from main_marts.fact_premium as premiums
join main_marts.dim_plan as plans on premiums.plan_key = plans.plan_key
where plans.metal_level = 'Silver'
group by 1, 2
order by median_silver_premium desc
limit 20;

