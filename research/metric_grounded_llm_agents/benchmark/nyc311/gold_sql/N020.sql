select agency, avg(case when status = 'Closed' then 1.0 else 0.0 end) as resolution_rate,
       count(*) as request_rows
from marts.fact_service_request
group by 1 having count(*) >= 1000
order by resolution_rate desc, agency limit 15;
