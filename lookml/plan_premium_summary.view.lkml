view: plan_premium_summary {
  derived_table: {
    sql:
      SELECT
        plan_key,
        AVG(monthly_premium) AS avg_monthly_premium,
        MEDIAN(monthly_premium) AS median_monthly_premium
      FROM main_marts.fact_premium
      GROUP BY 1 ;;
  }

  dimension: plan_key {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.plan_key ;;
  }

  measure: avg_monthly_premium {
    label: "Average Monthly Premium (Plan Level)"
    type: average
    value_format_name: usd
    sql: ${TABLE}.avg_monthly_premium ;;
  }

  measure: median_monthly_premium {
    label: "Median Monthly Premium (Plan Level)"
    type: median
    value_format_name: usd
    sql: ${TABLE}.median_monthly_premium ;;
  }
}
