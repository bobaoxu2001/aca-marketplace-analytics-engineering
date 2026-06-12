with plans as (
    select * from {{ ref('int_plan_base') }}
),

service_areas as (
    select * from {{ ref('stg_service_area_puf') }}
),

availability as (
    select distinct
        plans.business_year,
        plans.state_code,
        plans.issuer_id,
        plans.plan_id,
        plans.service_area_id,
        service_areas.service_area_name,
        service_areas.county_name,
        service_areas.covers_entire_state,
        service_areas.partial_county,
        service_areas.zip_codes
    from plans
    left join service_areas
        on plans.business_year = service_areas.business_year
        and plans.state_code = service_areas.state_code
        and plans.issuer_id = service_areas.issuer_id
        and plans.service_area_id = service_areas.service_area_id
)

select
    md5(
        concat_ws(
            '|',
            business_year::varchar,
            state_code,
            issuer_id,
            plan_id,
            coalesce(service_area_id, ''),
            coalesce(county_name, '')
        )
    ) as plan_availability_key,
    md5(concat_ws('|', business_year::varchar, state_code, plan_id)) as plan_key,
    md5(concat_ws('|', business_year::varchar, state_code, issuer_id)) as issuer_key,
    md5(
        concat_ws(
            '|',
            business_year::varchar,
            state_code,
            coalesce(service_area_id, ''),
            coalesce(county_name, ''),
            '',
            'service_area_county'
        )
    ) as geography_key,
    business_year,
    state_code,
    issuer_id,
    plan_id,
    service_area_id,
    service_area_name,
    county_name,
    covers_entire_state,
    partial_county,
    zip_codes,
    1 as plan_available_flag
from availability
