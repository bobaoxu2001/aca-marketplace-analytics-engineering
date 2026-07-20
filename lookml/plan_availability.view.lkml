view: plan_availability {
  sql_table_name: main_marts.fact_plan_availability ;;

  dimension: plan_availability_key {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.plan_availability_key ;;
  }

  dimension: plan_key {
    hidden: yes
    type: string
    sql: ${TABLE}.plan_key ;;
  }

  dimension: issuer_key {
    hidden: yes
    type: string
    sql: ${TABLE}.issuer_key ;;
  }

  dimension: geography_key {
    hidden: yes
    type: string
    sql: ${TABLE}.geography_key ;;
  }

  dimension: state_code {
    type: string
    sql: ${TABLE}.state_code ;;
  }

  dimension: service_area_id {
    type: string
    sql: ${TABLE}.service_area_id ;;
  }

  dimension: service_area_name {
    type: string
    sql: ${TABLE}.service_area_name ;;
  }

  dimension: county_name {
    type: string
    sql: ${TABLE}.county_name ;;
    description: "Raw CMS Service Area county value."
  }

  dimension: partial_county {
    type: string
    sql: ${TABLE}.partial_county ;;
  }

  dimension: covers_entire_state {
    type: string
    sql: ${TABLE}.covers_entire_state ;;
  }

  measure: availability_rows {
    type: count
  }

  measure: plan_count {
    label: "Plan Count"
    type: count_distinct
    sql: ${plan_key} ;;
  }

  measure: issuer_count {
    label: "Issuer Count"
    type: count_distinct
    sql: ${issuer_key} ;;
  }
}
