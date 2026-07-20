view: geography {
  sql_table_name: main_marts.dim_geography ;;

  dimension: geography_key {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.geography_key ;;
  }

  dimension: state_code {
    type: string
    sql: ${TABLE}.state_code ;;
  }

  dimension: county_name {
    type: string
    sql: ${TABLE}.county_name ;;
    description: "Raw CMS Service Area county value (often a FIPS code)."
  }

  dimension: county_display_name {
    type: string
    sql: ${TABLE}.county_display_name ;;
    description: "Display-friendly county name enriched from Census FIPS reference."
  }

  dimension: county_fips {
    type: string
    sql: ${TABLE}.county_fips ;;
    description: "Five-digit county FIPS code when resolved."
  }

  dimension: state_name {
    type: string
    sql: ${TABLE}.state_name ;;
  }

  dimension: rating_area_id {
    type: string
    sql: ${TABLE}.rating_area_id ;;
  }

  dimension: service_area_id {
    type: string
    sql: ${TABLE}.service_area_id ;;
  }

  dimension: service_area_name {
    type: string
    sql: ${TABLE}.service_area_name ;;
  }

  dimension: geography_type {
    type: string
    sql: ${TABLE}.geography_type ;;
  }

  measure: county_count {
    type: count_distinct
    sql: ${county_name} ;;
    filters: [geography_type: "service_area_county"]
  }
}
