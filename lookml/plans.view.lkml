view: plans {
  sql_table_name: main_marts.dim_plan ;;

  dimension: plan_key {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.plan_key ;;
  }

  dimension: plan_id {
    type: string
    sql: ${TABLE}.plan_id ;;
  }

  dimension: plan_name {
    type: string
    sql: ${TABLE}.plan_name ;;
  }

  dimension: issuer_key {
    hidden: yes
    type: string
    sql: ${TABLE}.issuer_key ;;
  }

  dimension: metal_level_key {
    hidden: yes
    type: string
    sql: ${TABLE}.metal_level_key ;;
  }

  dimension: metal_level {
    type: string
    sql: ${TABLE}.metal_level ;;
  }

  dimension: state_code {
    type: string
    sql: ${TABLE}.state_code ;;
  }

  dimension: service_area_id {
    type: string
    sql: ${TABLE}.service_area_id ;;
  }

  dimension: plan_type {
    type: string
    sql: ${TABLE}.plan_type ;;
  }

  dimension: market_coverage {
    type: string
    sql: ${TABLE}.market_coverage ;;
  }

  dimension: medical_deductible_integrated {
    type: number
    value_format_name: usd
    sql: ${TABLE}.medical_deductible_integrated ;;
  }

  dimension: medical_oop_max_integrated {
    type: number
    value_format_name: usd
    sql: ${TABLE}.medical_oop_max_integrated ;;
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

  measure: average_deductible {
    label: "Average Deductible"
    type: average
    value_format_name: usd
    sql: ${TABLE}.medical_deductible_integrated ;;
  }

  measure: average_out_of_pocket_maximum {
    label: "Average Out-of-Pocket Maximum"
    type: average
    value_format_name: usd
    sql: ${TABLE}.medical_oop_max_integrated ;;
  }
}
