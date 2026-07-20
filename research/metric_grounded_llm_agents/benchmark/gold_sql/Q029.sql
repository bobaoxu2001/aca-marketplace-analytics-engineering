select representative_reason_for_crosswalk, representative_crosswalk_level, count(*) as history_rows
from main_marts.dim_plan_history
where representative_reason_for_crosswalk is not null
group by 1, 2
order by history_rows desc
limit 20;
