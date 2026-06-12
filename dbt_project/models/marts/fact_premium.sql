with rates as (
    select * from {{ ref('int_rate_enriched') }}
),

deduped as (
    select
        business_year,
        state_code,
        issuer_id,
        plan_id,
        rating_area_id,
        tobacco_usage,
        age,
        age_band,
        rate_effective_date,
        rate_expiration_date,
        avg(individual_rate) as monthly_premium,
        avg(individual_tobacco_rate) as monthly_tobacco_premium,
        avg(couple_rate) as couple_premium,
        avg(primary_subscriber_one_dependent_rate) as primary_subscriber_one_dependent_premium,
        avg(primary_subscriber_two_dependents_rate) as primary_subscriber_two_dependents_premium,
        avg(primary_subscriber_three_plus_dependents_rate) as primary_subscriber_three_plus_dependents_premium
    from rates
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
)

select
    md5(
        concat_ws(
            '|',
            business_year::varchar,
            state_code,
            issuer_id,
            plan_id,
            rating_area_id,
            coalesce(tobacco_usage, ''),
            coalesce(age, ''),
            coalesce(rate_effective_date::varchar, '')
        )
    ) as premium_key,
    md5(concat_ws('|', business_year::varchar, state_code, plan_id)) as plan_key,
    md5(concat_ws('|', business_year::varchar, state_code, issuer_id)) as issuer_key,
    md5(age_band) as age_band_key,
    md5(concat_ws('|', business_year::varchar, state_code, '', '', coalesce(rating_area_id, ''), 'rating_area')) as geography_key,
    business_year,
    state_code,
    issuer_id,
    plan_id,
    rating_area_id,
    tobacco_usage,
    age,
    age_band,
    rate_effective_date,
    rate_expiration_date,
    monthly_premium,
    monthly_tobacco_premium,
    couple_premium,
    primary_subscriber_one_dependent_premium,
    primary_subscriber_two_dependents_premium,
    primary_subscriber_three_plus_dependents_premium
from deduped
