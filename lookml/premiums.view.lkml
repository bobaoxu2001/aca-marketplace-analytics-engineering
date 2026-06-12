view: premiums {
  sql_table_name: main_marts.fact_premium ;;

  dimension: premium_key {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.premium_key ;;
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

  dimension: age_band_key {
    hidden: yes
    type: string
    sql: ${TABLE}.age_band_key ;;
  }

  dimension: state_code {
    type: string
    sql: ${TABLE}.state_code ;;
  }

  dimension: rating_area_id {
    type: string
    sql: ${TABLE}.rating_area_id ;;
  }

  dimension: age {
    type: string
    sql: ${TABLE}.age ;;
  }

  dimension: age_band {
    type: string
    sql: ${TABLE}.age_band ;;
  }

  dimension: tobacco_usage {
    type: string
    sql: ${TABLE}.tobacco_usage ;;
  }

  measure: premium_rows {
    type: count
  }

  measure: average_monthly_premium {
    label: "Average Monthly Premium"
    type: average
    value_format_name: usd
    sql: ${TABLE}.monthly_premium ;;
  }

  measure: median_monthly_premium {
    label: "Median Monthly Premium"
    type: median
    value_format_name: usd
    sql: ${TABLE}.monthly_premium ;;
  }

  measure: median_silver_premium {
    label: "Median Silver Premium"
    type: median
    value_format_name: usd
    sql: ${TABLE}.monthly_premium ;;
    filters: [plans.metal_level: "Silver"]
  }

  measure: premium_difference_by_metal_level {
    label: "Premium Difference by Metal Level"
    type: average
    value_format_name: usd
    sql: ${TABLE}.monthly_premium ;;
    drill_fields: [plans.metal_level, state_code, rating_area_id]
  }
}
