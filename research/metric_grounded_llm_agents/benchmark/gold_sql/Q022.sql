with plan_premium as (
    select plan_key, avg(monthly_premium) as average_monthly_premium
    from main_marts.fact_premium
    group by 1
)
select quality.state_code, count(distinct quality.plan_key) as rated_joined_plan_count,
       avg(plan_premium.average_monthly_premium) as average_rated_plan_premium
from main_marts.fact_plan_quality_rating as quality
join plan_premium on quality.plan_key = plan_premium.plan_key
where quality.quality_rating_status = 'rated'
group by 1
order by average_rated_plan_premium desc
limit 20;

