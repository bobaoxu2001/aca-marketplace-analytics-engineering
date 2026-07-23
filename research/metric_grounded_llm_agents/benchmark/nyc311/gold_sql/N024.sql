with borough_stats as (
  select f.borough, count(*) as request_count, b.population_2020,
         count(*) * 1000.0 / b.population_2020 as requests_per_1k,
         avg(case when f.status = 'Closed' then 1.0 else 0.0 end) as resolution_rate
  from marts.fact_service_request as f
  join marts.dim_borough as b on f.borough = b.borough
  group by 1, 3
)
select borough, requests_per_1k, resolution_rate, request_count
from borough_stats order by requests_per_1k desc, resolution_rate asc;
