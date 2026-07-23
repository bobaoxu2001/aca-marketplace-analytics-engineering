select complaint_type,
       avg(response_hours) as mean_response_hours,
       median(response_hours) as median_response_hours,
       avg(response_hours) - median(response_hours) as skew_gap,
       count(*) as closed_rows
from marts.fact_service_request
where response_hours is not null
group by 1 having count(*) >= 1000
order by skew_gap desc, complaint_type limit 20;
