# Metric Dictionary

| Metric | Definition | Primary model | Suggested dimensions |
| --- | --- | --- | --- |
| Average monthly premium | Average `monthly_premium` from Rate PUF rows. | `fact_premium` | State, rating area, issuer, plan, metal level, age band, tobacco usage |
| Median silver premium | Median `monthly_premium` where the joined plan metal level is `Silver`. | `fact_premium` + `dim_plan` | State, rating area, issuer, age band |
| Plan count by county | Distinct count of `plan_key` where a plan is joined to service-area county geography. | `fact_plan_availability` or LookML `plans` explore | State, county, issuer, metal level |
| Issuer count by county | Distinct count of `issuer_key` where issuers have at least one plan in a county. | `fact_plan_availability` or LookML `plans` explore | State, county, metal level |
| Average deductible | Average integrated medical deductible from `dim_plan.medical_deductible_integrated`. | `dim_plan` | State, issuer, metal level, plan type |
| Average out-of-pocket maximum | Average integrated medical out-of-pocket maximum from `dim_plan.medical_oop_max_integrated`. | `dim_plan` | State, issuer, metal level, plan type |
| Benefit coverage rate | Covered benefit rows divided by total benefit rows. | `fact_benefit_cost_sharing` | Benefit, benefit category, plan, issuer, metal level |
| Premium difference by metal level | Difference between a metal level's average premium and a comparison metal level or overall average. | `fact_premium` + `dim_plan` | State, rating area, issuer, age band |

## Grain notes

- `fact_premium` is modeled at plan, rating area, age, tobacco, and effective
  date grain.
- `fact_plan_availability` is modeled at plan and service-area county grain.
- `fact_benefit_cost_sharing` is modeled at plan-benefit-cost-sharing grain.
- Plan-level deductible and out-of-pocket metrics come from Plan Attributes PUF
  columns and should be interpreted as plan design attributes rather than claims
  experience.
