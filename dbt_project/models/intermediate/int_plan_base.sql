with plan_rows as (
    select * from {{ ref('stg_plan_attributes_puf') }}
)

select
    business_year,
    state_code,
    issuer_id,
    max(issuer_name) as issuer_name,
    plan_id,
    max(standard_component_id) as standard_component_id,
    max(plan_name) as plan_name,
    max(hios_product_id) as hios_product_id,
    max(network_id) as network_id,
    max(service_area_id) as service_area_id,
    max(market_coverage) as market_coverage,
    max(dental_only_plan) as dental_only_plan,
    max(plan_type) as plan_type,
    max(metal_level) as metal_level,
    max(medical_deductible_integrated) as medical_deductible_integrated,
    max(medical_deductible_separate) as medical_deductible_separate,
    max(drug_deductible_integrated) as drug_deductible_integrated,
    max(drug_deductible_separate) as drug_deductible_separate,
    max(medical_oop_max_integrated) as medical_oop_max_integrated,
    max(medical_oop_max_separate) as medical_oop_max_separate,
    max(drug_oop_max_integrated) as drug_oop_max_integrated,
    max(drug_oop_max_separate) as drug_oop_max_separate
from plan_rows
group by 1, 2, 3, 5
