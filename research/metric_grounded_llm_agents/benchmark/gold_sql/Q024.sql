select state_code,
       sum(case when continuity_status = 'new_or_not_in_crosswalk' then 1 else 0 end) as new_current_plans,
       sum(case when is_current then 1 else 0 end) as current_history_rows,
       new_current_plans * 1.0 / nullif(current_history_rows, 0) as new_plan_share
from main_marts.dim_plan_history
group by 1
having current_history_rows > 0
order by new_plan_share desc
limit 20;

