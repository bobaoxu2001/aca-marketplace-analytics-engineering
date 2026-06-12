with benefits as (
    select distinct
        benefit_name
    from {{ ref('int_benefit_cost_sharing') }}
)

select
    md5(benefit_name) as benefit_key,
    benefit_name,
    case
        when lower(benefit_name) like '%deductible%' then 'Deductible'
        when lower(benefit_name) like '%maximum out of pocket%' then 'Out-of-pocket maximum'
        when lower(benefit_name) like '%primary care%' then 'Primary care'
        when lower(benefit_name) like '%specialist%' then 'Specialist care'
        when lower(benefit_name) like '%generic%' then 'Prescription drugs'
        when lower(benefit_name) like '%emergency%' then 'Emergency care'
        else 'Other'
    end as benefit_category
from benefits
