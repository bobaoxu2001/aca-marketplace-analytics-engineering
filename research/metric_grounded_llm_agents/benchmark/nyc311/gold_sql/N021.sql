with ranked as (
  select borough, complaint_type, count(*) as request_count,
         row_number() over (partition by borough order by count(*) desc, complaint_type) as rn
  from marts.fact_service_request
  group by 1, 2
)
select borough, complaint_type, request_count
from ranked where rn = 1 order by request_count desc, borough;
