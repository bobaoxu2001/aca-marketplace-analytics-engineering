select borough, count(*) as request_count,
       sum(case when open_data_channel_type = 'ONLINE' then 1 else 0 end) * 1.0 / count(*) as online_share
from marts.fact_service_request
group by 1 order by online_share desc;
