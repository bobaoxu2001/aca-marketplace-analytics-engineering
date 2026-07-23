select representative_reason_for_crosswalk, count(*) as history_rows
from main_marts.dim_plan_history
where representative_reason_for_crosswalk is not null
group by 1
order by history_rows desc
limit 20;
