with source as (
    select * from {{ source('raw', 'rate_puf_py2026') }}
)

select
    try_cast("BusinessYear" as integer) as business_year,
    upper(trim("StateCode")) as state_code,
    trim("IssuerId") as issuer_id,
    trim("PlanId") as plan_id,
    trim("RatingAreaId") as rating_area_id,
    nullif(trim("Tobacco"), '') as tobacco_usage,
    nullif(trim("Age"), '') as age,
    try_cast("RateEffectiveDate" as date) as rate_effective_date,
    try_cast("RateExpirationDate" as date) as rate_expiration_date,
    {{ clean_numeric('"IndividualRate"') }} as individual_rate,
    {{ clean_numeric('"IndividualTobaccoRate"') }} as individual_tobacco_rate,
    {{ clean_numeric('"Couple"') }} as couple_rate,
    {{ clean_numeric('"PrimarySubscriberAndOneDependent"') }} as primary_subscriber_one_dependent_rate,
    {{ clean_numeric('"PrimarySubscriberAndTwoDependents"') }} as primary_subscriber_two_dependents_rate,
    {{ clean_numeric('"PrimarySubscriberAndThreeOrMoreDependents"') }} as primary_subscriber_three_plus_dependents_rate,
    trim("FederalTIN") as federal_tin,
    trim("SourceName") as source_name,
    try_cast("VersionNum" as integer) as version_num,
    try_cast("ImportDate" as timestamp) as import_date
from source
where nullif(trim("PlanId"), '') is not null
