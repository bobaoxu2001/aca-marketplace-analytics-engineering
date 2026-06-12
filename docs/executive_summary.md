# Executive Summary: ACA Marketplace Analytics Warehouse

## One-line pitch

This project turns real CMS Plan Year 2026 ACA Marketplace Public Use Files into
a tested local analytics warehouse for premiums, benefits, issuer competition,
plan availability, and geography-level market analysis.

## Why this matters

Health insurance teams make pricing, product, actuarial, operations, and market
strategy decisions from fragmented public datasets. Raw CMS PUF files are large,
wide, and not directly stakeholder-friendly. This project demonstrates how an
analytics engineer can convert those files into trusted marts, documented
metrics, semantic models, and dashboard-ready analysis surfaces.

## Validated data scale

| Dataset | Rows validated |
| --- | ---: |
| Rate PUF - PY2026 | 2,235,761 |
| Plan Attributes PUF - PY2026 | 22,059 |
| Benefits and Cost Sharing PUF - PY2026 | 1,457,952 |
| Service Area PUF - PY2026 | 8,820 |

Final real-data dbt build status: `PASS=83 WARN=0 ERROR=0 SKIP=0`.

## Stakeholder use cases

- **Analytics:** maintain reusable SQL marts and metric definitions for plan,
  premium, benefit, issuer, and geography analysis.
- **Product:** compare metal levels, plan types, deductibles, out-of-pocket
  maximums, and covered benefits.
- **Actuarial:** benchmark monthly premiums by age band, rating area, tobacco
  usage, issuer, and metal level.
- **Operations:** understand county/service-area plan availability and partial
  county coverage flags.
- **Market strategy:** identify issuer competition, plan density, and geographic
  opportunities using public marketplace data.

## Modeled data assets

- Rate PUF - PY2026
- Plan Attributes PUF - PY2026
- Benefits and Cost Sharing PUF - PY2026
- Service Area PUF - PY2026

## Priority metrics

- Average monthly premium
- Median silver premium
- Plan count by county
- Issuer count by county
- Average deductible
- Average out-of-pocket maximum
- Benefit coverage rate
- Premium difference by metal level

## Recommended executive dashboard flow

1. **Market availability:** plan count, issuer count, and service-area coverage.
2. **Premium benchmarking:** average and median premiums by state, rating area,
   metal level, issuer, age band, and tobacco usage.
3. **Benefit design:** deductible, out-of-pocket maximum, benefit coverage rate,
   and cost-sharing details.
4. **Market strategy:** issuer premium positioning and county-level availability
   gaps.

## Important scope note

This project uses public plan design and premium data only. It does not include
claims, enrollment, subsidy eligibility, member demographics, or deployed
production infrastructure.
