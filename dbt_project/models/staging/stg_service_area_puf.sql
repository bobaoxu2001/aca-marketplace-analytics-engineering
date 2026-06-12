with source as (
    select * from {{ source('raw', 'service_area_puf_py2026') }}
)

select
    try_cast("BusinessYear" as integer) as business_year,
    upper(trim("StateCode")) as state_code,
    trim("IssuerId") as issuer_id,
    nullif(trim("ServiceAreaId"), '') as service_area_id,
    nullif(trim("ServiceAreaName"), '') as service_area_name,
    nullif(trim("CoverEntireState"), '') as covers_entire_state,
    nullif(trim("County"), '') as county_name,
    nullif(trim("PartialCounty"), '') as partial_county,
    nullif(trim("ZipCodes"), '') as zip_codes,
    nullif(trim("PartialCountyJustification"), '') as partial_county_justification,
    trim("SourceName") as source_name,
    try_cast("VersionNum" as integer) as version_num,
    try_cast("ImportDate" as timestamp) as import_date
from source
where nullif(trim("ServiceAreaId"), '') is not null
