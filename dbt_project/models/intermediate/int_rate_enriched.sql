with rates as (
    select * from {{ ref('stg_rate_puf') }}
)

select
    business_year,
    state_code,
    issuer_id,
    plan_id,
    rating_area_id,
    tobacco_usage,
    age,
    case
        when try_cast(age as integer) between 0 and 20 then '0-20'
        when try_cast(age as integer) between 21 and 29 then '21-29'
        when try_cast(age as integer) between 30 and 39 then '30-39'
        when try_cast(age as integer) between 40 and 49 then '40-49'
        when try_cast(age as integer) between 50 and 59 then '50-59'
        when try_cast(age as integer) >= 60 then '60+'
        else 'Family/Other'
    end as age_band,
    rate_effective_date,
    rate_expiration_date,
    individual_rate,
    individual_tobacco_rate,
    couple_rate,
    primary_subscriber_one_dependent_rate,
    primary_subscriber_two_dependents_rate,
    primary_subscriber_three_plus_dependents_rate
from rates
where individual_rate is not null
