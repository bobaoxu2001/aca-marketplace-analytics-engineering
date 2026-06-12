with source as (
    select * from {{ source('raw', 'benefits_cost_sharing_puf_py2026') }}
)

select
    try_cast("BusinessYear" as integer) as business_year,
    upper(trim("StateCode")) as state_code,
    trim("IssuerId") as issuer_id,
    trim("PlanId") as plan_id,
    nullif(trim("StandardComponentId"), '') as standard_component_id,
    nullif(trim("BenefitName"), '') as benefit_name,
    nullif(trim("IsCovered"), '') as is_covered,
    nullif(trim("IsEHB"), '') as is_ehb,
    nullif(trim("QuantLimitOnSvc"), '') as has_quantity_limit,
    {{ clean_numeric('"LimitQty"') }} as limit_quantity,
    nullif(trim("LimitUnit"), '') as limit_unit,
    nullif(trim("Exclusions"), '') as exclusions,
    nullif(trim("Explanation"), '') as explanation,
    nullif(trim("CopayInnTier1"), '') as copay_in_network_tier_1,
    nullif(trim("CopayInnTier2"), '') as copay_in_network_tier_2,
    nullif(trim("CopayOutofNet"), '') as copay_out_of_network,
    nullif(trim("CoinsInnTier1"), '') as coinsurance_in_network_tier_1,
    nullif(trim("CoinsInnTier2"), '') as coinsurance_in_network_tier_2,
    nullif(trim("CoinsOutofNet"), '') as coinsurance_out_of_network,
    trim("SourceName") as source_name,
    cast(null as integer) as version_num,
    try_cast("ImportDate" as timestamp) as import_date
from source
where nullif(trim("PlanId"), '') is not null
