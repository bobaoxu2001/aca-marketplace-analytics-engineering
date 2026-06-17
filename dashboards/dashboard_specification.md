# Dashboard Specification: ACA Marketplace Market Intelligence

Canonical dashboard requirements live in `docs/dashboard_spec.md`. This file is
retained in `dashboards/` for BI-oriented project structure and mirrors the
same stakeholder-facing intent.

## Audience

Analytics, product, actuarial, operations, and market strategy stakeholders at a
health insurance company.

## Filters

- State
- County / service area (`county_display_name`, county FIPS)
- Rating area
- Issuer (name and ID)
- Metal level
- Plan type
- Age band
- Tobacco usage
- Continuity status
- Quality rating status

## Page 1: Market availability

| Tile | Visualization | Metric | Source model | Dimensions |
| --- | --- | --- | --- | --- |
| Plan availability KPI | Big number | Plan count | `fact_plan_availability` | Current filters |
| Issuer competition KPI | Big number | Issuer count | `fact_plan_availability` | Current filters |
| County availability map/table | Map or table | Plan count by county | `fact_plan_availability` + `dim_geography` | State, county display name |
| Issuer concentration | Bar chart | Issuer count by county | `fact_plan_availability` | County |
| Partial county coverage | Table | Plan count | `fact_plan_availability` + `dim_geography` | State, county, partial county flag |

## Page 2: Premium benchmarking

| Tile | Visualization | Metric | Source model | Dimensions |
| --- | --- | --- | --- | --- |
| Average monthly premium | Big number | Average monthly premium | `fact_premium` | Current filters |
| Median silver premium | Big number | Median silver premium | `fact_premium` + `dim_plan` | Current filters |
| Premium by metal | Bar chart | Average monthly premium | `fact_premium` + `dim_plan` | Metal level |
| Premium by age band | Line or bar chart | Average monthly premium | `fact_premium` | Age band, metal level |
| Rating area premium spread | Table | Average monthly premium | `fact_premium` | State, rating area, issuer |

## Page 3: Benefit design

| Tile | Visualization | Metric | Source model | Dimensions |
| --- | --- | --- | --- | --- |
| Average deductible | Big number | Average deductible | `dim_plan` | Current filters |
| Average out-of-pocket max | Big number | Average out-of-pocket maximum | `dim_plan` | Current filters |
| Benefit coverage | Bar chart | Benefit coverage rate | `fact_benefit_cost_sharing` | Benefit category |
| Cost-sharing detail | Table | Copay/coinsurance fields | `fact_benefit_cost_sharing` | Plan, benefit |

## Page 4: Market strategy

| Tile | Visualization | Metric | Source model | Dimensions |
| --- | --- | --- | --- | --- |
| Issuer premium position | Scatter plot | Average monthly premium vs plan count | `fact_premium` + `dim_issuer` | Issuer, metal level |
| County opportunity table | Table | Plan count, issuer count, median silver premium | `fact_plan_availability` + `dim_geography` | County display name |
| Metal-level comparison | Bar chart | Average monthly premium by metal level | `fact_premium` + `dim_plan` | Metal level, state |

## Page 5: Plan history and quality

| Tile | Visualization | Metric | Source model | Dimensions |
| --- | --- | --- | --- | --- |
| Continuity status | Bar chart | Current plan count by continuity status | `dim_plan_history` | State, issuer |
| Quality distribution | Bar chart | Quality PUF row count | `fact_plan_quality_rating` | Overall rating value |
| Quality vs premium | Table | Plan-level average premium by rating | `fact_plan_quality_rating` + plan-level premium summary | State, issuer, metal level |
| Unjoined quality rows | Table | Rows where `joins_to_dim_plan = false` | `fact_plan_quality_rating` | State, issuer, plan ID |

## Data quality callouts

- Show last successful raw load timestamp from `raw_load_audit`.
- Flag counties with partial county service area coverage.
- Display profile warnings if duplicate key checks identify unexpected duplicate raw rows.
- Show county FIPS enrichment match rate from `dim_geography`.
