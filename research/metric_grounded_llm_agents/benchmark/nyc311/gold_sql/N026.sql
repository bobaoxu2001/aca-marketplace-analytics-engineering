select agency, borough, median(response_hours) as median_response_hours, count(*) as closed_rows
from marts.fact_service_request
where response_hours is not null
group by 1, 2 having count(*) >= 500
order by median_response_hours desc, agency, borough limit 20;
