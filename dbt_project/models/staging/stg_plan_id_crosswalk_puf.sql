with source as (
    select * from {{ source('raw', 'plan_id_crosswalk_puf_py2025_py2026') }}
)

select
    upper(trim("State")) as state_code,
    nullif(trim("DentalPlan"), '') as dental_plan_flag,
    nullif(trim("PlanID_2025"), '') as plan_id_2025,
    nullif(trim("IssuerID_2025"), '') as issuer_id_2025,
    nullif(trim("MultistatePlan_2025"), '') as multistate_plan_2025,
    nullif(trim("MetalLevel_2025"), '') as metal_level_2025,
    nullif(trim("ChildAdultOnly_2025"), '') as child_adult_only_2025,
    nullif(trim("FIPSCode"), '') as fips_code,
    nullif(trim("ZipCode"), '') as zip_code,
    nullif(trim("CrosswalkLevel"), '') as crosswalk_level,
    nullif(trim("ReasonForCrosswalk"), '') as reason_for_crosswalk,
    nullif(trim("PlanID_2026"), '') as plan_id_2026,
    nullif(trim("IssuerID_2026"), '') as issuer_id_2026,
    nullif(trim("MultistatePlan_2026"), '') as multistate_plan_2026,
    nullif(trim("MetalLevel_2026"), '') as metal_level_2026,
    nullif(trim("ChildAdultOnly_2026"), '') as child_adult_only_2026,
    nullif(trim("AgeOffPlanID_2026"), '') as age_off_plan_id_2026,
    nullif(trim("IssuerID_AgeOff2026"), '') as age_off_issuer_id_2026,
    nullif(trim("MultistatePlan_AgeOff2026"), '') as age_off_multistate_plan_2026,
    nullif(trim("MetalLevel_AgeOff2026"), '') as age_off_metal_level_2026,
    nullif(trim("ChildAdultOnly_AgeOff2026"), '') as age_off_child_adult_only_2026,
    nullif(trim("ReasonForBronzeToSilverCrosswalk"), '') as reason_for_bronze_to_silver_crosswalk,
    nullif(trim("SilverCSREligPlanID_2026"), '') as silver_csr_elig_plan_id_2026,
    nullif(trim("SilverCSREligIssuerID_2026"), '') as silver_csr_elig_issuer_id_2026
from source
where nullif(trim("PlanID_2025"), '') is not null
