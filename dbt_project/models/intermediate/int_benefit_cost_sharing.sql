with benefits as (
    select * from {{ ref('stg_benefits_cost_sharing_puf') }}
)

select
    business_year,
    state_code,
    issuer_id,
    plan_id,
    standard_component_id,
    benefit_name,
    case
        when lower(is_covered) in ('covered', 'yes', 'true') then true
        when lower(is_covered) in ('not covered', 'no', 'false') then false
        else null
    end as is_covered_flag,
    case
        when lower(is_ehb) in ('yes', 'true') then true
        when lower(is_ehb) in ('no', 'false') then false
        else null
    end as is_ehb_flag,
    case
        when lower(has_quantity_limit) in ('yes', 'true') then true
        when lower(has_quantity_limit) in ('no', 'false') then false
        else null
    end as has_quantity_limit_flag,
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
where benefit_name is not null
