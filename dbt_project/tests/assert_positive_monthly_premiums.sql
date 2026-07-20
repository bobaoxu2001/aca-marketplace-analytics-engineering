-- Premium amounts should not be negative where populated.
select premium_key, monthly_premium
from {{ ref('fact_premium') }}
where monthly_premium is not null
  and monthly_premium < 0
