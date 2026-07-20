select quality_rating_status, overall_rating_value, count(*) as quality_rows
from main_marts.fact_plan_quality_rating
group by 1, 2
order by quality_rows desc;
