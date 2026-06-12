with plans as (
    select * from {{ ref('int_plan_base') }}
)

select
    md5(concat_ws('|', business_year::varchar, state_code, plan_id)) as plan_key,
    md5(concat_ws('|', business_year::varchar, state_code, issuer_id)) as issuer_key,
    md5(coalesce(metal_level, 'Unknown')) as metal_level_key,
    business_year,
    state_code,
    issuer_id,
    plan_id,
    standard_component_id,
    plan_variant_count,
    plan_name,
    hios_product_id,
    network_id,
    service_area_id,
    market_coverage,
    dental_only_plan,
    plan_type,
    coalesce(metal_level, 'Unknown') as metal_level,
    medical_deductible_integrated,
    medical_deductible_separate,
    drug_deductible_integrated,
    drug_deductible_separate,
    medical_oop_max_integrated,
    medical_oop_max_separate,
    drug_oop_max_integrated,
    drug_oop_max_separate
from plans
