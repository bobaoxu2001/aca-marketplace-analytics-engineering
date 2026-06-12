{% macro clean_numeric(column_name) -%}
    try_cast(nullif(regexp_replace({{ column_name }}, '[^0-9\.\-]', '', 'g'), '') as double)
{%- endmacro %}
