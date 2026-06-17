connection: "duckdb"

include: "*.view.lkml"

explore: plan_availability {
  label: "Plan Availability"
  description: "County-level plan and issuer availability at plan × service-area county grain."

  join: geography {
    type: left_outer
    relationship: many_to_one
    sql_on: ${plan_availability.geography_key} = ${geography.geography_key} ;;
  }

  join: plans {
    type: left_outer
    relationship: many_to_one
    sql_on: ${plan_availability.plan_key} = ${plans.plan_key} ;;
  }

  join: issuers {
    type: left_outer
    relationship: many_to_one
    sql_on: ${plan_availability.issuer_key} = ${issuers.issuer_key} ;;
  }
}

explore: plans {
  label: "Plans"
  description: "Conformed standard-component plan attributes for product and benefit design analysis."

  join: issuers {
    type: left_outer
    relationship: many_to_one
    sql_on: ${plans.issuer_key} = ${issuers.issuer_key} ;;
  }
}

explore: premiums {
  label: "Premiums"
  description: "Rating-area premium analysis by plan, issuer, metal level, and age band."

  join: plans {
    type: left_outer
    relationship: many_to_one
    sql_on: ${premiums.plan_key} = ${plans.plan_key} ;;
  }

  join: geography {
    type: left_outer
    relationship: many_to_one
    sql_on: ${premiums.geography_key} = ${geography.geography_key} ;;
  }

  join: issuers {
    type: left_outer
    relationship: many_to_one
    sql_on: ${premiums.issuer_key} = ${issuers.issuer_key} ;;
  }
}

explore: benefits {
  label: "Benefits and Cost Sharing"
  description: "Benefit coverage and cost-sharing analysis by plan and benefit."

  join: plans {
    type: left_outer
    relationship: many_to_one
    sql_on: ${benefits.plan_key} = ${plans.plan_key} ;;
  }

  join: issuers {
    type: left_outer
    relationship: many_to_one
    sql_on: ${benefits.issuer_key} = ${issuers.issuer_key} ;;
  }
}

explore: plan_history {
  label: "Plan Continuity"
  description: "PY2025 to PY2026 plan continuity and crosswalk analysis."

  join: plans {
    type: left_outer
    relationship: many_to_one
    sql_on: ${plan_history.plan_key} = ${plans.plan_key} ;;
  }

  join: issuers {
    type: left_outer
    relationship: many_to_one
    sql_on: ${plan_history.issuer_key} = ${issuers.issuer_key} ;;
  }
}

explore: quality {
  label: "Quality Ratings"
  description: >
    PY2026 plan-level Quality PUF ratings. Plan-level premium summaries join
    through plan_premium_summary to avoid fan-out from rating-area premium rows.

  join: plans {
    type: left_outer
    relationship: many_to_one
    sql_on: ${quality.plan_key} = ${plans.plan_key} ;;
  }

  join: plan_premium_summary {
    type: left_outer
    relationship: one_to_one
    sql_on: ${quality.plan_key} = ${plan_premium_summary.plan_key} ;;
  }

  join: issuers {
    type: left_outer
    relationship: many_to_one
    sql_on: ${quality.issuer_key} = ${issuers.issuer_key} ;;
  }
}
