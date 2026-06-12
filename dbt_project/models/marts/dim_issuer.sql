with issuers as (
    select
        business_year,
        state_code,
        issuer_id,
        max(issuer_name) as issuer_name
    from {{ ref('int_plan_base') }}
    group by 1, 2, 3
)

select
    md5(concat_ws('|', business_year::varchar, state_code, issuer_id)) as issuer_key,
    business_year,
    state_code,
    issuer_id,
    issuer_name
from issuers
