select premiums.state_code, issuers.issuer_name,
       median(premiums.monthly_premium) as median_silver_premium,
       count(*) as premium_rows
from main_marts.fact_premium as premiums
join main_marts.dim_plan as plans on premiums.plan_key = plans.plan_key
join main_marts.dim_issuer as issuers on premiums.issuer_key = issuers.issuer_key
where plans.metal_level = 'Silver'
group by 1, 2
having premium_rows >= 20
order by median_silver_premium desc
limit 20;

