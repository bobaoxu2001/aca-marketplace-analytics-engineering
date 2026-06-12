with service_area_geography as (
    select distinct
        business_year,
        state_code,
        service_area_id,
        service_area_name,
        county_name,
        cast(null as varchar) as rating_area_id,
        covers_entire_state,
        partial_county,
        zip_codes,
        'service_area_county' as geography_type
    from {{ ref('stg_service_area_puf') }}
),

rating_area_geography as (
    select distinct
        business_year,
        state_code,
        cast(null as varchar) as service_area_id,
        cast(null as varchar) as service_area_name,
        cast(null as varchar) as county_name,
        rating_area_id,
        cast(null as varchar) as covers_entire_state,
        cast(null as varchar) as partial_county,
        cast(null as varchar) as zip_codes,
        'rating_area' as geography_type
    from {{ ref('stg_rate_puf') }}
)

select
    md5(
        concat_ws(
            '|',
            business_year::varchar,
            state_code,
            coalesce(service_area_id, ''),
            coalesce(county_name, ''),
            coalesce(rating_area_id, ''),
            geography_type
        )
    ) as geography_key,
    business_year,
    state_code,
    service_area_id,
    service_area_name,
    county_name,
    rating_area_id,
    covers_entire_state,
    partial_county,
    zip_codes,
    geography_type
from service_area_geography

union all

select
    md5(
        concat_ws(
            '|',
            business_year::varchar,
            state_code,
            coalesce(service_area_id, ''),
            coalesce(county_name, ''),
            coalesce(rating_area_id, ''),
            geography_type
        )
    ) as geography_key,
    business_year,
    state_code,
    service_area_id,
    service_area_name,
    county_name,
    rating_area_id,
    covers_entire_state,
    partial_county,
    zip_codes,
    geography_type
from rating_area_geography
