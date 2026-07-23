select date_trunc('month', created_at) as month, count(*) as request_count
from marts.fact_service_request
group by 1 order by month;
