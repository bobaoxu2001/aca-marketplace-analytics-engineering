with source as (
    select * from {{ source('raw', 'quality_puf_py2026') }}
)

select
    try_cast("IssuerID" as integer) as issuer_id_numeric,
    nullif(trim("IssuerID"), '') as issuer_id,
    upper(trim("State")) as state_code,
    nullif(trim("Plan Type"), '') as plan_type,
    nullif(trim("Reportingunitid"), '') as reporting_unit_id,
    nullif(trim("PlanID"), '') as plan_id,
    nullif(trim("OverallRatingValue"), '') as overall_rating_value,
    try_cast(nullif(trim("OverallRatingValue"), '') as integer) as overall_rating_numeric,
    nullif(trim("MedicalCareRatingValue"), '') as medical_care_rating_value,
    try_cast(nullif(trim("MedicalCareRatingValue"), '') as integer) as medical_care_rating_numeric,
    nullif(trim("MemberExperienceRatingValue"), '') as member_experience_rating_value,
    try_cast(nullif(trim("MemberExperienceRatingValue"), '') as integer) as member_experience_rating_numeric,
    nullif(trim("PlanAdministrationRatingValue"), '') as plan_administration_rating_value,
    try_cast(nullif(trim("PlanAdministrationRatingValue"), '') as integer) as plan_administration_rating_numeric,
    case
        when nullif(trim("OverallRatingValue"), '') in ('1', '2', '3', '4', '5') then 'rated'
        when nullif(trim("OverallRatingValue"), '') = 'NR - New-Ineligible for Scoring' then 'not_rated_new'
        when nullif(trim("OverallRatingValue"), '') = 'NR - Not Rated' then 'not_rated'
        else 'unknown'
    end as quality_rating_status
from source
where nullif(trim("PlanID"), '') is not null
