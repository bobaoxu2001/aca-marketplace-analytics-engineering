select state_code, avg(monthly_premium) as average_monthly_premium, count(*) as premium_rows
from main_marts.fact_premium
group by 1
order by average_monthly_premium desc
limit 10;
