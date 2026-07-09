select geography.state_code, geography.county_name, geography.service_area_id,
       count(distinct availability.plan_key) as plan_count,
       count(distinct availability.issuer_key) as issuer_count,
       plan_count * 1.0 / nullif(issuer_count, 0) as plans_per_issuer
from main_marts.fact_plan_availability as availability
join main_marts.dim_geography as geography on availability.geography_key = geography.geography_key
where geography.geography_type = 'service_area_county'
group by 1, 2, 3
having plan_count >= 10 and issuer_count <= 2
order by plans_per_issuer desc, plan_count desc
limit 20;

