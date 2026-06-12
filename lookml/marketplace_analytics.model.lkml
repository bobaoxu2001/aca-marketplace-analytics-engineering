connection: "duckdb"

include: "*.view.lkml"

explore: plans {
  label: "Plan Availability"
  description: "County-level plan and issuer availability from Plan Attributes and Service Area PUFs."

  join: geography {
    type: left_outer
    relationship: many_to_many
    sql_on:
      ${plans.state_code} = ${geography.state_code}
      and ${plans.service_area_id} = ${geography.service_area_id}
      and ${geography.geography_type} = 'service_area_county' ;;
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
}

explore: benefits {
  label: "Benefits and Cost Sharing"
  description: "Benefit coverage and cost-sharing analysis by plan and benefit."

  join: plans {
    type: left_outer
    relationship: many_to_one
    sql_on: ${benefits.plan_key} = ${plans.plan_key} ;;
  }
}
