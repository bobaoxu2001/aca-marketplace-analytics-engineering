select metal_level, avg(medical_deductible_integrated) as average_deductible, count(*) as plan_rows
from main_marts.dim_plan
where medical_deductible_integrated is not null
group by 1
order by average_deductible desc;
