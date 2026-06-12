# Executive Summary: ACA Marketplace Analytics Warehouse

## One-line pitch

This project turns real CMS Plan Year 2026 ACA Marketplace Public Use Files into
a tested local analytics warehouse for premiums, benefits, issuer competition,
plan availability, plan history, quality ratings, and geography-level market
analysis.

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
| Plan ID Crosswalk PUF - PY2025 to PY2026 | 158,746 |
| Quality PUF - PY2026 | 4,302 |

Final real-data dbt build status: `PASS=108 WARN=0 ERROR=0 SKIP=0`.

## Selected descriptive findings

Generated from the dbt marts in `docs/insight_snapshot.md`:

- The marts model 5,144 conformed standard-component plans across 30 states and
  359 issuers.
- Silver plans represent 29.7% of modeled plans.
- TX has the most issuers represented in the marts, with 32 issuers.
- 4,394 of 5,923 service-area geography rows have one issuer represented,
  marking them for closer market review.
- Platinum has the highest median modeled monthly premium at $1,480.33 across
  all premium rows; Low has the lowest at $19.96.
- Plan history modeling identifies 3,815 current plans that continue under the
  same plan ID and 909 current plans that are new or not represented in the
  crosswalk.
- The Quality PUF contributes 4,302 plan-level quality rows; 4,183 join to the
  modeled PY2026 plan dimension for quality-vs-cost analysis.

These findings are descriptive summaries of public CMS data and are not
enrollment weighted.

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
- Plan continuity status
- Quality rating distribution
- Quality vs premium where plan-level joins are supported

## Recommended executive dashboard flow

1. **Market availability:** plan count, issuer count, and service-area coverage.
2. **Premium benchmarking:** average and median premiums by state, rating area,
   metal level, issuer, age band, and tobacco usage.
3. **Benefit design:** deductible, out-of-pocket maximum, benefit coverage rate,
   and cost-sharing details.
4. **Market strategy:** issuer premium positioning and county-level availability
   gaps.
5. **Plan history and quality:** continuity/churn from PY2025 to PY2026 and
   quality-vs-premium summaries where public Quality PUF rows join to modeled
   plans.

## Important scope note

This project uses public plan design and premium data only. It does not include
claims, enrollment, subsidy eligibility, member demographics, or deployed
production infrastructure.

For technical tradeoffs and future improvements, see:

- `docs/modeling_decisions.md`
- `docs/limitations_and_next_steps.md`
