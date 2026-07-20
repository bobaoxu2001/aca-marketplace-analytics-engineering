select metal_level, avg(medical_oop_max_integrated) as average_oop_max, count(*) as plan_rows
from main_marts.dim_plan
where medical_oop_max_integrated is not null
group by 1
order by average_oop_max desc;
