select incident_address, borough, count(*) as request_count
from marts.fact_service_request
where incident_address is not null
group by 1, 2 order by request_count desc, incident_address limit 20;
