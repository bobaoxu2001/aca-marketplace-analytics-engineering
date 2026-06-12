# Executive Summary: ACA Marketplace Analytics Warehouse

This project models the CMS Plan Year 2026 ACA Marketplace Public Use Files into
an analytics-ready warehouse for a tech-driven health insurance organization.
The warehouse connects plan pricing, benefit design, issuers, metal levels, age
bands, and county-level availability so stakeholders can answer core market
questions from reproducible data models.

## Business use case

Health insurance teams need to understand where plans are available, how prices
vary across rating areas and metal levels, and how benefit design differs by
issuer and market. This warehouse supports:

- **Analytics:** repeatable SQL-ready marts for plan, premium, availability, and
  benefits analysis.
- **Product:** comparisons of deductible, out-of-pocket, and benefit coverage
  patterns across plan designs.
- **Actuarial:** premium benchmarking by age band, rating area, issuer, and
  metal level.
- **Operations:** county-level visibility into plan availability and service
  area coverage.
- **Market strategy:** issuer competition, plan density, and premium positioning
  across geographies.

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

## Recommended executive dashboard

The dashboard should start with market coverage and competitiveness KPIs, then
drill into pricing and benefit design:

1. County market overview: plan count, issuer count, and service area coverage.
2. Premium benchmarking: average and median premiums by state, rating area,
   metal level, issuer, age band, and tobacco usage.
3. Benefit design: deductible, out-of-pocket maximum, and coverage rate by
   benefit category and metal level.
4. Market strategy deep dive: issuer premium positioning and plan availability
   gaps by county.
