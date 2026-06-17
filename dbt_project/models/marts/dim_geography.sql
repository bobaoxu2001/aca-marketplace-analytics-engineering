with service_area_geography as (
    select
        business_year,
        state_code,
        service_area_id,
        max(service_area_name) as service_area_name,
        county_name,
        cast(null as varchar) as rating_area_id,
        max(covers_entire_state) as covers_entire_state,
        max(partial_county) as partial_county,
        string_agg(distinct zip_codes, '; ') as zip_codes,
        'service_area_county' as geography_type
    from {{ ref('stg_service_area_puf') }}
    group by 1, 2, 3, 5
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
),

base_geography as (
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
)

select
    base.geography_key,
    base.business_year,
    base.state_code,
    base.service_area_id,
    base.service_area_name,
    base.county_name,
    base.rating_area_id,
    base.covers_entire_state,
    base.partial_county,
    base.zip_codes,
    base.geography_type,
    coalesce(cast(counties.full_fips as varchar), base.county_name) as county_fips,
    coalesce(counties.county_display_name, base.county_name) as county_display_name,
    coalesce(counties.state_name, base.state_code) as state_name
from base_geography as base
left join {{ ref('county_fips_reference') }} as counties
    on base.geography_type = 'service_area_county'
    and base.state_code = counties.state_code
    and (
        base.county_name = cast(counties.full_fips as varchar)
        or base.county_name = counties.county_fips
        or lower(base.county_name) = lower(counties.county_name)
    )
