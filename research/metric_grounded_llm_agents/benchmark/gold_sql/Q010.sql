select state_code, avg(monthly_premium) as average_monthly_premium,
       stddev_samp(monthly_premium) as premium_stddev,
       min(monthly_premium) as min_premium,
       max(monthly_premium) as max_premium,
       count(*) as premium_rows
from main_marts.fact_premium
group by 1
order by premium_stddev desc
limit 10;

