with county_competition as (
    select geography.state_code, geography.county_name,
           count(distinct availability.issuer_key) as issuer_count
    from main_marts.fact_plan_availability as availability
    join main_marts.dim_geography as geography on availability.geography_key = geography.geography_key
    where geography.geography_type = 'service_area_county'
    group by 1, 2
)
select state_code, count(*) as one_issuer_counties
from county_competition
where issuer_count = 1
group by 1
order by one_issuer_counties desc;

