# Dashboard Specification: ACA Marketplace Market Intelligence

Canonical dashboard requirements now live in `docs/dashboard_spec.md`. This file
is retained in `dashboards/` for BI-oriented project structure and mirrors the
same stakeholder-facing intent.

## Audience

Analytics, product, actuarial, operations, and market strategy stakeholders at a
health insurance company.

## Filters

- State
- County
- Rating area
- Issuer
- Metal level
- Plan type
- Age band
- Tobacco usage

## Page 1: Market availability

| Tile | Visualization | Metric | Dimensions |
| --- | --- | --- | --- |
| Plan availability KPI | Big number | Plan count | Selected geography |
| Issuer competition KPI | Big number | Issuer count | Selected geography |
| County availability map/table | Map or table | Plan count by county | State, county |
| Issuer concentration | Bar chart | Issuer count by county | County |

## Page 2: Premium benchmarking

| Tile | Visualization | Metric | Dimensions |
| --- | --- | --- | --- |
| Average monthly premium | Big number | Average monthly premium | Current filters |
| Median silver premium | Big number | Median silver premium | Current filters |
| Premium by metal | Bar chart | Average monthly premium | Metal level |
| Premium by age band | Line or bar chart | Average monthly premium | Age band, metal level |
| Rating area premium spread | Table | Average monthly premium | State, rating area, issuer |

## Page 3: Benefit design

| Tile | Visualization | Metric | Dimensions |
| --- | --- | --- | --- |
| Average deductible | Big number | Average deductible | Current filters |
| Average out-of-pocket max | Big number | Average out-of-pocket maximum | Current filters |
| Benefit coverage | Bar chart | Benefit coverage rate | Benefit category |
| Cost-sharing detail | Table | Copay/coinsurance fields | Plan, benefit |

## Page 4: Market strategy

| Tile | Visualization | Metric | Dimensions |
| --- | --- | --- | --- |
| Issuer premium position | Scatter plot | Average monthly premium vs plan count | Issuer, metal level |
| County opportunity table | Table | Plan count, issuer count, median silver premium | County |
| Metal-level comparison | Bar chart | Premium difference by metal level | Metal level, state |

## Data quality callouts

- Show last successful raw load timestamp from `raw_load_audit`.
- Flag counties with partial county service area coverage.
- Display profile warnings if duplicate key checks identify unexpected duplicate
  raw rows.
