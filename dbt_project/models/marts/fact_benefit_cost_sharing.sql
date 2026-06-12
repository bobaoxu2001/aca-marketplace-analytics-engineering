with benefits as (
    select * from {{ ref('int_benefit_cost_sharing') }}
),

deduped as (
    select distinct
        business_year,
        state_code,
        issuer_id,
        plan_id,
        standard_component_id,
        benefit_name,
        is_covered_flag,
        is_ehb_flag,
        has_quantity_limit_flag,
        limit_quantity,
        limit_unit,
        exclusions,
        explanation,
        copay_in_network_tier_1,
        copay_in_network_tier_2,
        copay_out_of_network,
        coinsurance_in_network_tier_1,
        coinsurance_in_network_tier_2,
        coinsurance_out_of_network
    from benefits
)

select
    md5(
        concat_ws(
            '|',
            business_year::varchar,
            state_code,
            issuer_id,
            plan_id,
            benefit_name,
            coalesce(copay_in_network_tier_1, ''),
            coalesce(coinsurance_in_network_tier_1, '')
        )
    ) as benefit_cost_sharing_key,
    md5(concat_ws('|', business_year::varchar, state_code, plan_id)) as plan_key,
    md5(concat_ws('|', business_year::varchar, state_code, issuer_id)) as issuer_key,
    md5(benefit_name) as benefit_key,
    business_year,
    state_code,
    issuer_id,
    plan_id,
    standard_component_id,
    benefit_name,
    is_covered_flag,
    is_ehb_flag,
    has_quantity_limit_flag,
    limit_quantity,
    limit_unit,
    exclusions,
    explanation,
    copay_in_network_tier_1,
    copay_in_network_tier_2,
    copay_out_of_network,
    coinsurance_in_network_tier_1,
    coinsurance_in_network_tier_2,
    coinsurance_out_of_network
from deduped
