view: plan_history {
  sql_table_name: main_marts.dim_plan_history ;;

  dimension: plan_history_key {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.plan_history_key ;;
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

  dimension: effective_plan_year {
    type: number
    sql: ${TABLE}.effective_plan_year ;;
  }

  dimension: previous_plan_id {
    type: string
    sql: ${TABLE}.previous_plan_id ;;
  }

  dimension: current_plan_id {
    type: string
    sql: ${TABLE}.current_plan_id ;;
  }

  dimension: continuity_status {
    type: string
    sql: ${TABLE}.continuity_status ;;
  }

  dimension: is_current {
    type: yesno
    sql: ${TABLE}.is_current ;;
  }

  measure: plan_history_rows {
    type: count
  }

  measure: current_plan_count {
    type: count_distinct
    sql: ${current_plan_id} ;;
    filters: [is_current: "yes"]
  }

  measure: continuing_plan_count {
    type: count_distinct
    sql: ${current_plan_id} ;;
    filters: [continuity_status: "continuing_same_plan"]
  }

  measure: crosswalked_plan_count {
    type: count_distinct
    sql: ${current_plan_id} ;;
    filters: [continuity_status: "crosswalked_from_prior_plan"]
  }

  measure: new_or_unmatched_plan_count {
    type: count_distinct
    sql: ${current_plan_id} ;;
    filters: [continuity_status: "new_or_not_in_crosswalk"]
  }
}
