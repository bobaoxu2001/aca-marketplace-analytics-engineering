with source as (
    select * from {{ source('raw', 'plan_attributes_puf_py2026') }}
)

select
    try_cast("BusinessYear" as integer) as business_year,
    upper(trim("StateCode")) as state_code,
    trim("IssuerId") as issuer_id,
    nullif(trim("IssuerMarketPlaceMarketingName"), '') as issuer_name,
    trim("PlanId") as plan_id,
    nullif(trim("StandardComponentId"), '') as standard_component_id,
    nullif(trim("PlanMarketingName"), '') as plan_name,
    nullif(trim("HIOSProductId"), '') as hios_product_id,
    nullif(trim("NetworkId"), '') as network_id,
    nullif(trim("ServiceAreaId"), '') as service_area_id,
    nullif(trim("MarketCoverage"), '') as market_coverage,
    nullif(trim("DentalOnlyPlan"), '') as dental_only_plan,
    nullif(trim("PlanType"), '') as plan_type,
    nullif(trim("MetalLevel"), '') as metal_level,
    {{ clean_numeric('"TEHBDedInnTier1Individual"') }} as medical_deductible_integrated,
    {{ clean_numeric('"MEHBDedInnTier1Individual"') }} as medical_deductible_separate,
    cast(null as double) as drug_deductible_integrated,
    {{ clean_numeric('"DEHBDedInnTier1Individual"') }} as drug_deductible_separate,
    {{ clean_numeric('"TEHBInnTier1IndividualMOOP"') }} as medical_oop_max_integrated,
    {{ clean_numeric('"MEHBInnTier1IndividualMOOP"') }} as medical_oop_max_separate,
    cast(null as double) as drug_oop_max_integrated,
    {{ clean_numeric('"DEHBInnTier1IndividualMOOP"') }} as drug_oop_max_separate,
    trim("SourceName") as source_name,
    cast(null as integer) as version_num,
    try_cast("ImportDate" as timestamp) as import_date
from source
where nullif(trim("PlanId"), '') is not null
