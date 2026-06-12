with quality as (
    select * from {{ ref('stg_quality_puf') }}
),

plans as (
    select
        plan_key,
        issuer_key,
        business_year,
        state_code,
        plan_id,
        metal_level,
        medical_deductible_integrated,
        medical_oop_max_integrated
    from {{ ref('dim_plan') }}
)

select
    md5(concat_ws('|', '2026', quality.state_code, quality.issuer_id, quality.plan_id)) as plan_quality_key,
    plans.plan_key,
    coalesce(plans.issuer_key, md5(concat_ws('|', '2026', quality.state_code, quality.issuer_id))) as issuer_key,
    2026 as business_year,
    quality.state_code,
    quality.issuer_id,
    quality.plan_type,
    quality.reporting_unit_id,
    quality.plan_id,
    plans.metal_level,
    quality.overall_rating_value,
    quality.overall_rating_numeric,
    quality.medical_care_rating_value,
    quality.medical_care_rating_numeric,
    quality.member_experience_rating_value,
    quality.member_experience_rating_numeric,
    quality.plan_administration_rating_value,
    quality.plan_administration_rating_numeric,
    quality.quality_rating_status,
    plans.medical_deductible_integrated,
    plans.medical_oop_max_integrated,
    case when plans.plan_key is not null then true else false end as joins_to_dim_plan
from quality
left join plans
    on quality.state_code = plans.state_code
    and quality.plan_id = plans.plan_id
