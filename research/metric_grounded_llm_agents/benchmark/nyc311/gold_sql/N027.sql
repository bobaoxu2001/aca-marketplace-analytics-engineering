with monthly as (
  select date_trunc('month', created_at) as month, count(*) as request_count
  from marts.fact_service_request group by 1
)
select month, request_count,
       request_count - lag(request_count) over (order by month) as mom_change
from monthly order by month;
