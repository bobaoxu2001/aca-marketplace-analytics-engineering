select geography.state_code, geography.county_name, geography.service_area_id,
       count(distinct availability.issuer_key) as issuer_count,
       count(distinct availability.plan_key) as plan_count
from main_marts.fact_plan_availability as availability
join main_marts.dim_geography as geography on availability.geography_key = geography.geography_key
where geography.geography_type = 'service_area_county'
group by 1, 2, 3
having issuer_count <= 1
order by plan_count asc, state_code, county_name
limit 25;

