with metal_levels as (
    select distinct
        coalesce(metal_level, 'Unknown') as metal_level
    from {{ ref('int_plan_base') }}
)

select
    md5(metal_level) as metal_level_key,
    metal_level,
    case metal_level
        when 'Catastrophic' then 1
        when 'Bronze' then 2
        when 'Expanded Bronze' then 3
        when 'Silver' then 4
        when 'Gold' then 5
        when 'Platinum' then 6
        when 'Low' then 7
        when 'High' then 8
        else 99
    end as metal_sort_order
from metal_levels
