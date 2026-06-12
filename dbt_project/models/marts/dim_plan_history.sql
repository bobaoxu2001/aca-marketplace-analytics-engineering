with current_plans as (
    select * from {{ ref('dim_plan') }}
),

valid_crosswalks as (
    select
        state_code,
        plan_id_2025,
        issuer_id_2025,
        plan_id_2026,
        issuer_id_2026,
        reason_for_crosswalk,
        crosswalk_level
    from {{ ref('stg_plan_id_crosswalk_puf') }}
    where plan_id_2026 is not null
        and plan_id_2026 not like '00000%'
),

current_plan_crosswalk as (
    select
        state_code,
        plan_id_2026 as current_plan_id,
        min(plan_id_2025) as previous_plan_id,
        min(issuer_id_2025) as previous_issuer_id,
        count(distinct plan_id_2025) as previous_plan_count,
        max(case when plan_id_2025 = plan_id_2026 then 1 else 0 end) as has_same_plan_id,
        max(reason_for_crosswalk) as representative_reason_for_crosswalk,
        max(crosswalk_level) as representative_crosswalk_level
    from valid_crosswalks
    group by 1, 2
),

current_history as (
    select
        md5(concat_ws('|', '2026', plans.state_code, plans.plan_id, 'current')) as plan_history_key,
        plans.plan_key,
        plans.issuer_key,
        2026 as effective_plan_year,
        crosswalk.previous_plan_id,
        plans.plan_id as current_plan_id,
        plans.state_code,
        plans.issuer_id as current_issuer_id,
        crosswalk.previous_issuer_id,
        true as is_current,
        case
            when crosswalk.current_plan_id is null then 'new_or_not_in_crosswalk'
            when crosswalk.has_same_plan_id = 1 then 'continuing_same_plan'
            else 'crosswalked_from_prior_plan'
        end as continuity_status,
        coalesce(crosswalk.previous_plan_count, 0) as previous_plan_count,
        crosswalk.representative_reason_for_crosswalk,
        crosswalk.representative_crosswalk_level
    from current_plans as plans
    left join current_plan_crosswalk as crosswalk
        on plans.state_code = crosswalk.state_code
        and plans.plan_id = crosswalk.current_plan_id
),

discontinued_history as (
    select
        md5(concat_ws('|', '2025', state_code, plan_id_2025, 'discontinued')) as plan_history_key,
        cast(null as varchar) as plan_key,
        cast(null as varchar) as issuer_key,
        2025 as effective_plan_year,
        plan_id_2025 as previous_plan_id,
        cast(null as varchar) as current_plan_id,
        state_code,
        cast(null as varchar) as current_issuer_id,
        min(issuer_id_2025) as previous_issuer_id,
        false as is_current,
        'discontinued_or_no_2026_crosswalk' as continuity_status,
        1 as previous_plan_count,
        max(reason_for_crosswalk) as representative_reason_for_crosswalk,
        max(crosswalk_level) as representative_crosswalk_level
    from {{ ref('stg_plan_id_crosswalk_puf') }}
    where plan_id_2026 like '00000%'
    group by 1, 4, 5, 6, 7, 8, 10, 11, 12
)

select * from current_history

union all

select * from discontinued_history
