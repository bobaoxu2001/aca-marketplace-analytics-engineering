select agency, count(*) as request_count
from marts.fact_service_request
group by 1 order by request_count desc, agency limit 10;
