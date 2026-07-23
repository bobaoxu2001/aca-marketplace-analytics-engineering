select agency, count(*) as request_count,
       count(*) * 1.0 / sum(count(*)) over () as request_share
from marts.fact_service_request
group by 1 order by request_share desc, agency limit 15;
