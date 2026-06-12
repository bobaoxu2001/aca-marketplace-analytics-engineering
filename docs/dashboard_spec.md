# Dashboard Specification: ACA Marketplace Market Intelligence

This specification describes a stakeholder-facing dashboard that could be built
from the dbt marts and LookML semantic layer. It intentionally avoids fabricated
screenshots or fake results; it defines the intended dashboard structure,
metrics, filters, and data-quality callouts.

A static preview generated from real aggregate mart queries is available at
`assets/dashboard_preview.png`.

## Audience

- Analytics leaders monitoring data quality and metric consistency.
- Product teams comparing plan design and benefit coverage.
- Actuarial teams benchmarking premiums by geography and segment.
- Operations teams reviewing county and service-area availability.
- Market strategy teams studying issuer competition and market density.

## Global filters

- State
- County / service area
- Rating area
- Issuer
- Metal level
- Plan type
- Age band
- Tobacco usage

## Page 1: Market availability

| Tile | Visualization | Metric | Source model | Dimensions |
| --- | --- | --- | --- | --- |
| Plan availability KPI | Big number | Plan count | `fact_plan_availability` | Current filters |
| Issuer competition KPI | Big number | Issuer count | `fact_plan_availability` | Current filters |
| County availability table | Table | Plan count by county | `fact_plan_availability` + `dim_geography` | State, county |
| Issuer concentration | Bar chart | Issuer count by county | `fact_plan_availability` | County |
| Partial county coverage | Table | Plan count | `fact_plan_availability` + `dim_geography` | State, county, partial county flag |

## Page 2: Premium benchmarking

| Tile | Visualization | Metric | Source model | Dimensions |
| --- | --- | --- | --- | --- |
| Average monthly premium | Big number | Average monthly premium | `fact_premium` | Current filters |
| Median silver premium | Big number | Median silver premium | `fact_premium` + `dim_plan` | Current filters |
| Premium by metal level | Bar chart | Average monthly premium | `fact_premium` + `dim_plan` | Metal level |
| Premium by age band | Line or bar chart | Average monthly premium | `fact_premium` | Age band, metal level |
| Rating area premium spread | Table | Average monthly premium | `fact_premium` | State, rating area, issuer |

## Page 3: Benefit design

| Tile | Visualization | Metric | Source model | Dimensions |
| --- | --- | --- | --- | --- |
| Average deductible | Big number | Average deductible | `dim_plan` | Current filters |
| Average out-of-pocket maximum | Big number | Average out-of-pocket maximum | `dim_plan` | Current filters |
| Benefit coverage | Bar chart | Benefit coverage rate | `fact_benefit_cost_sharing` + `dim_benefit` | Benefit category |
| Cost-sharing detail | Table | Copay and coinsurance fields | `fact_benefit_cost_sharing` | Plan, benefit |

## Page 4: Market strategy

| Tile | Visualization | Metric | Source model | Dimensions |
| --- | --- | --- | --- | --- |
| Issuer premium position | Scatter plot | Average premium vs. plan count | `fact_premium` + `fact_plan_availability` | Issuer, metal level |
| County opportunity table | Table | Plan count, issuer count, median silver premium | Marts joined through semantic layer | State, county |
| Metal-level comparison | Bar chart | Premium difference by metal level | `fact_premium` + `dim_plan` | Metal level, state |

## Data-quality callouts

- Display last successful raw load timestamp from `raw_load_audit`.
- Include row counts from the real validation results.
- Flag service-area rows where county is missing or partial county coverage is
  present.
- Note that CMS Service Area `County` values may need a reference join for
  display-friendly county names.
- Use dbt test status as the dashboard data freshness/trust signal.

## Suggested default view

- State: all
- Metal level: Bronze, Expanded Bronze, Silver, Gold, Platinum, Catastrophic
- Age band: 21-29, 30-39, 40-49, 50-59, 60+
- Tobacco usage: no preference / non-tobacco where available
