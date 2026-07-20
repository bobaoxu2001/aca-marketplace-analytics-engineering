view: issuers {
  sql_table_name: main_marts.dim_issuer ;;

  dimension: issuer_key {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.issuer_key ;;
  }

  dimension: issuer_id {
    type: string
    sql: ${TABLE}.issuer_id ;;
  }

  dimension: issuer_name {
    type: string
    sql: ${TABLE}.issuer_name ;;
  }

  dimension: state_code {
    type: string
    sql: ${TABLE}.state_code ;;
  }

  dimension: business_year {
    type: number
    sql: ${TABLE}.business_year ;;
  }

  measure: issuer_count {
    type: count_distinct
    sql: ${issuer_key} ;;
  }
}
