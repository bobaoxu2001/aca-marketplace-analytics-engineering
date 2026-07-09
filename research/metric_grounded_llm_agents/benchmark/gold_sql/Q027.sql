select quality_rating_status,
       avg(medical_deductible_integrated) as average_deductible,
       count(*) as quality_rows
from main_marts.fact_plan_quality_rating
where medical_deductible_integrated is not null
group by 1
order by average_deductible desc;

