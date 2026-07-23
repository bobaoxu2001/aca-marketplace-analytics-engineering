select quality_rating_status, count(*) as quality_rows
from main_marts.fact_plan_quality_rating
group by 1
order by quality_rows desc;
