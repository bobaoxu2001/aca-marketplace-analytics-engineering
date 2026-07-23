with top5 as (
  select complaint_type from marts.fact_service_request
  group by 1 order by count(*) desc, complaint_type limit 5
)
select f.borough, median(f.response_hours) as median_response_hours, count(*) as closed_rows
from marts.fact_service_request as f
where f.response_hours is not null and f.complaint_type in (select complaint_type from top5)
group by 1 order by median_response_hours desc, f.borough;
