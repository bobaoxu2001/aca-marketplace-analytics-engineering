select state_code, continuity_status, count(*) as history_rows
from main_marts.dim_plan_history
group by 1, 2
order by history_rows desc
limit 20;
