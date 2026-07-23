select f.borough, count(*) as request_count, b.population_2020,
       count(*) * 1000.0 / b.population_2020 as requests_per_1k
from marts.fact_service_request as f
join marts.dim_borough as b on f.borough = b.borough
group by 1, 3 order by requests_per_1k desc;
