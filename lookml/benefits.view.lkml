view: benefits {
  sql_table_name: main_marts.fact_benefit_cost_sharing ;;

  dimension: benefit_cost_sharing_key {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.benefit_cost_sharing_key ;;
  }

  dimension: plan_key {
    hidden: yes
    type: string
    sql: ${TABLE}.plan_key ;;
  }

  dimension: benefit_key {
    hidden: yes
    type: string
    sql: ${TABLE}.benefit_key ;;
  }

  dimension: benefit_name {
    type: string
    sql: ${TABLE}.benefit_name ;;
  }

  dimension: is_covered {
    type: yesno
    sql: ${TABLE}.is_covered_flag ;;
  }

  dimension: is_ehb {
    label: "Is Essential Health Benefit"
    type: yesno
    sql: ${TABLE}.is_ehb_flag ;;
  }

  dimension: has_quantity_limit {
    type: yesno
    sql: ${TABLE}.has_quantity_limit_flag ;;
  }

  dimension: copay_in_network_tier_1 {
    type: string
    sql: ${TABLE}.copay_in_network_tier_1 ;;
  }

  dimension: coinsurance_in_network_tier_1 {
    type: string
    sql: ${TABLE}.coinsurance_in_network_tier_1 ;;
  }

  measure: benefit_rows {
    type: count
  }

  measure: covered_benefit_rows {
    type: count
    filters: [is_covered: "yes"]
  }

  measure: benefit_coverage_rate {
    label: "Benefit Coverage Rate"
    type: number
    value_format_name: percent_2
    sql: 1.0 * ${covered_benefit_rows} / nullif(${benefit_rows}, 0) ;;
  }
}
