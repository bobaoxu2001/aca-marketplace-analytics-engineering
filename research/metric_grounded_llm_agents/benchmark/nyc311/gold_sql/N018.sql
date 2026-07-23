select f.borough, count(*) as noise_requests, b.population_2020,
       count(*) * 1000.0 / b.population_2020 as noise_per_1k
from marts.fact_service_request as f
join marts.dim_borough as b on f.borough = b.borough
where f.complaint_type like 'Noise%'
group by 1, 3 order by noise_per_1k desc;
