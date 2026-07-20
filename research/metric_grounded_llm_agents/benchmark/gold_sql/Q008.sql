select history.state_code, coalesce(issuers.issuer_name, history.current_issuer_id, history.previous_issuer_id) as issuer_label,
       sum(case when history.continuity_status in ('new_or_not_in_crosswalk', 'discontinued_or_no_2026_crosswalk') then 1 else 0 end) as non_continuing_rows,
       count(*) as total_history_rows,
       non_continuing_rows * 1.0 / nullif(total_history_rows, 0) as non_continuity_rate
from main_marts.dim_plan_history as history
left join main_marts.dim_issuer as issuers on history.issuer_key = issuers.issuer_key
group by 1, 2
having total_history_rows >= 5
order by non_continuity_rate desc, non_continuing_rows desc, history.state_code, issuer_label
limit 20;
