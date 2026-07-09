with metal_state as (
    select premiums.state_code, plans.metal_level, avg(premiums.monthly_premium) as avg_premium
    from main_marts.fact_premium as premiums
    join main_marts.dim_plan as plans on premiums.plan_key = plans.plan_key
    where plans.metal_level in ('Gold', 'Silver')
    group by 1, 2
)
select gold.state_code, gold.avg_premium as gold_average_premium,
       silver.avg_premium as silver_average_premium,
       gold.avg_premium - silver.avg_premium as gold_silver_gap
from metal_state as gold
join metal_state as silver on gold.state_code = silver.state_code
where gold.metal_level = 'Gold' and silver.metal_level = 'Silver'
order by gold_silver_gap desc
limit 20;

