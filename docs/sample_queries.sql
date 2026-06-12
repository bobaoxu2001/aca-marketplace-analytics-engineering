/*
Sample stakeholder SQL for the ACA Marketplace Analytics warehouse.

Assumptions:
- dbt has been built in DuckDB using the default profile.
- Mart relations live under the `main_marts` schema.
- These queries return examples of metric logic; they do not fabricate outputs.
*/

-- 1. Data freshness / raw load audit.
select
    table_name,
    row_count,
    loaded_at_utc
from main.raw_load_audit
order by table_name;

-- 2. Average monthly premium by state and metal level.
select
    premiums.state_code,
    plans.metal_level,
    avg(premiums.monthly_premium) as average_monthly_premium
from main_marts.fact_premium as premiums
join main_marts.dim_plan as plans
    on premiums.plan_key = plans.plan_key
group by 1, 2
order by 1, 3 desc;

-- 3. Median silver premium by state and rating area.
select
    premiums.state_code,
    premiums.rating_area_id,
    median(premiums.monthly_premium) as median_silver_premium
from main_marts.fact_premium as premiums
join main_marts.dim_plan as plans
    on premiums.plan_key = plans.plan_key
where plans.metal_level = 'Silver'
group by 1, 2
order by 1, 2;

-- 4. Plan and issuer count by CMS service-area county value.
select
    geography.state_code,
    geography.county_name,
    count(distinct availability.plan_key) as plan_count,
    count(distinct availability.issuer_key) as issuer_count
from main_marts.fact_plan_availability as availability
join main_marts.dim_geography as geography
    on availability.geography_key = geography.geography_key
where geography.geography_type = 'service_area_county'
group by 1, 2
order by 1, 2;

-- 5. Average deductible and out-of-pocket maximum by metal level.
select
    metal_level,
    avg(medical_deductible_integrated) as average_deductible,
    avg(medical_oop_max_integrated) as average_out_of_pocket_maximum
from main_marts.dim_plan
group by 1
order by 1;

-- 6. Benefit coverage rate by benefit category.
select
    benefit.benefit_category,
    sum(case when facts.is_covered_flag then 1.0 else 0.0 end)
        / nullif(count(*), 0) as benefit_coverage_rate
from main_marts.fact_benefit_cost_sharing as facts
join main_marts.dim_benefit as benefit
    on facts.benefit_key = benefit.benefit_key
group by 1
order by 2 desc;

-- 7. Premium difference by metal level compared with statewide average.
with metal_premiums as (
    select
        premiums.state_code,
        plans.metal_level,
        avg(premiums.monthly_premium) as average_premium
    from main_marts.fact_premium as premiums
    join main_marts.dim_plan as plans
        on premiums.plan_key = plans.plan_key
    group by 1, 2
),

state_premiums as (
    select
        state_code,
        avg(average_premium) as state_average_premium
    from metal_premiums
    group by 1
)

select
    metal_premiums.state_code,
    metal_premiums.metal_level,
    metal_premiums.average_premium,
    metal_premiums.average_premium - state_premiums.state_average_premium
        as premium_difference_from_state_average
from metal_premiums
join state_premiums
    on metal_premiums.state_code = state_premiums.state_code
order by 1, 4 desc;
