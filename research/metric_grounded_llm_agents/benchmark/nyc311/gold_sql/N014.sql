select borough, median(response_hours) as median_response_hours,
       avg(response_hours) as mean_response_hours, count(*) as closed_rows
from marts.fact_service_request
where response_hours is not null
group by 1 order by median_response_hours desc;
