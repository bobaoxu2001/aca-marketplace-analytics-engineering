-- Quality rows flagged as joined should always resolve to a plan dimension row.
select quality.plan_quality_key
from {{ ref('fact_plan_quality_rating') }} as quality
left join {{ ref('dim_plan') }} as plans
    on quality.plan_key = plans.plan_key
where quality.joins_to_dim_plan = true
  and plans.plan_key is null
