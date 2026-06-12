# Metric Dictionary

This dictionary defines stakeholder-facing metrics modeled from official CMS
PY2026 ACA Marketplace Public Use Files. Metrics are intended for marketplace
analytics and plan design analysis, not claims experience or enrollment
reporting.

| Metric | Business question | Definition / formula | Primary model | Suggested dimensions | Caveats |
| --- | --- | --- | --- | --- | --- |
| Average monthly premium | How expensive are plans in a market segment? | `avg(fact_premium.monthly_premium)` | `fact_premium` | State, rating area, issuer, plan, metal level, age band, tobacco usage | Premium rows are at rating-area, age, tobacco, and effective-date grain. |
| Median silver premium | What is the typical Silver plan premium? | `median(monthly_premium)` where `dim_plan.metal_level = 'Silver'` | `fact_premium` + `dim_plan` | State, rating area, issuer, age band | Public premium data only; not enrollment weighted. |
| Plan count by county | How many standard-component plans are available in each county/service area? | `count(distinct plan_key)` | `fact_plan_availability` | State, county/service area, issuer, metal level | CMS county values may require a reference join for friendly county names. |
| Issuer count by county | How competitive is a county by issuer presence? | `count(distinct issuer_key)` | `fact_plan_availability` | State, county/service area, metal level | Counts issuers with at least one available plan. |
| Average deductible | How does cost exposure vary by product design? | `avg(dim_plan.medical_deductible_integrated)` | `dim_plan` | State, issuer, metal level, plan type | Uses PY2026 Plan Attributes TEHB/MEHB/DEHB plan design fields. |
| Average out-of-pocket maximum | What is the average maximum member exposure? | `avg(dim_plan.medical_oop_max_integrated)` | `dim_plan` | State, issuer, metal level, plan type | Plan design attribute; not observed spend. |
| Benefit coverage rate | Which benefits are broadly covered? | `sum(is_covered_flag) / count(*)` | `fact_benefit_cost_sharing` | Benefit, benefit category, plan, issuer, metal level | Uses CMS `IsCovered`; null/ambiguous values should be reviewed in detailed analysis. |
| Premium difference by metal level | How do premiums compare across benefit richness tiers? | Metal-level average premium minus benchmark average premium | `fact_premium` + `dim_plan` | State, rating area, issuer, age band | Choose comparison benchmark explicitly: state average, Silver, or overall average. |

## Grain notes

- `fact_premium` is modeled at plan, rating area, age, tobacco, and effective
  date grain.
- `fact_plan_availability` is modeled at plan and service-area county grain.
- `fact_benefit_cost_sharing` is modeled at plan-benefit-cost-sharing grain.
- `dim_plan` is conformed at CMS standard component grain so Rate PUF premiums
  can join cleanly to plan attributes; `plan_variant_count` preserves the number
  of Plan Attributes variants represented by each standard component.
- Plan-level deductible and out-of-pocket metrics come from Plan Attributes PUF
  columns and should be interpreted as plan design attributes rather than claims
  experience.

## Metric ownership assumptions

- Analytics engineering owns model correctness, tests, documentation, and
  metric definitions.
- Business stakeholders should confirm metric interpretation before operational
  use.
- Any production BI deployment should add freshness monitoring, access controls,
  and a county reference dimension.
