with plan_premium as (
    select plan_key, avg(monthly_premium) as average_monthly_premium
    from main_marts.fact_premium
    group by 1
)
select quality.overall_rating_value, count(distinct quality.plan_key) as joined_plan_count,
       avg(plan_premium.average_monthly_premium) as average_monthly_premium
from main_marts.fact_plan_quality_rating as quality
join plan_premium on quality.plan_key = plan_premium.plan_key
where quality.overall_rating_numeric is not null
group by 1
order by try_cast(quality.overall_rating_value as integer);
