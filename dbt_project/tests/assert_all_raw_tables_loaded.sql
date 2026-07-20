-- Fail when any expected CMS raw table is missing from the load audit log.
with expected_tables as (
    select *
    from (
        values
            ('rate_puf_py2026'),
            ('plan_attributes_puf_py2026'),
            ('benefits_cost_sharing_puf_py2026'),
            ('service_area_puf_py2026'),
            ('plan_id_crosswalk_puf_py2025_py2026'),
            ('quality_puf_py2026')
    ) as expected(table_name)
)

select expected.table_name
from expected_tables as expected
left join {{ source('raw', 'raw_load_audit') }} as audit
    on expected.table_name = audit.table_name
where audit.table_name is null
