select agency, count(distinct complaint_type) as distinct_complaint_types, count(*) as request_rows
from marts.fact_service_request
group by 1 order by distinct_complaint_types desc, agency limit 15;
