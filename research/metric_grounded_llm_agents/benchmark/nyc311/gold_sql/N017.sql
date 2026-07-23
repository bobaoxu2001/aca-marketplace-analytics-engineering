select complaint_type,
       sum(case when status <> 'Closed' then 1 else 0 end) as unresolved_count,
       count(*) as request_rows
from marts.fact_service_request
group by 1 order by unresolved_count desc, complaint_type limit 20;
