select borough,
       sum(case when status <> 'Closed' then 1 else 0 end) as unresolved_count,
       count(*) as request_rows,
       sum(case when status <> 'Closed' then 1 else 0 end) * 1.0 / count(*) as unresolved_share
from marts.fact_service_request
group by 1 order by unresolved_share desc;
