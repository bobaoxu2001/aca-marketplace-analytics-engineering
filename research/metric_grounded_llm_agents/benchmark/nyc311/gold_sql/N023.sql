select case when complaint_type like 'Noise%' then 'Noise'
            when upper(complaint_type) like '%HEAT%' then 'Heat/Hot Water' end as category,
       median(response_hours) as median_response_hours, count(*) as closed_rows
from marts.fact_service_request
where response_hours is not null
  and (complaint_type like 'Noise%' or upper(complaint_type) like '%HEAT%')
group by 1 order by median_response_hours;
