view: quality {
  sql_table_name: main_marts.fact_plan_quality_rating ;;

  dimension: plan_quality_key {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.plan_quality_key ;;
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

  dimension: state_code {
    type: string
    sql: ${TABLE}.state_code ;;
  }

  dimension: plan_id {
    type: string
    sql: ${TABLE}.plan_id ;;
  }

  dimension: plan_type {
    type: string
    sql: ${TABLE}.plan_type ;;
  }

  dimension: quality_rating_status {
    type: string
    sql: ${TABLE}.quality_rating_status ;;
  }

  dimension: overall_rating_value {
    type: string
    sql: ${TABLE}.overall_rating_value ;;
  }

  dimension: overall_rating_numeric {
    type: number
    sql: ${TABLE}.overall_rating_numeric ;;
  }

  dimension: joins_to_dim_plan {
    type: yesno
    sql: ${TABLE}.joins_to_dim_plan ;;
  }

  measure: quality_plan_rows {
    type: count
  }

  measure: rated_plan_rows {
    type: count
    filters: [quality_rating_status: "rated"]
  }

  measure: average_overall_rating {
    type: average
    value_format_name: decimal_2
    sql: ${TABLE}.overall_rating_numeric ;;
  }

  measure: average_medical_care_rating {
    type: average
    value_format_name: decimal_2
    sql: ${TABLE}.medical_care_rating_numeric ;;
  }

  measure: average_member_experience_rating {
    type: average
    value_format_name: decimal_2
    sql: ${TABLE}.member_experience_rating_numeric ;;
  }

  measure: average_plan_administration_rating {
    type: average
    value_format_name: decimal_2
    sql: ${TABLE}.plan_administration_rating_numeric ;;
  }
}
