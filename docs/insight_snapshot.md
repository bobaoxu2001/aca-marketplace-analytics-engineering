# Insight Snapshot: PY2026 ACA Marketplace Marts

Generated from real dbt mart tables in `data/processed/aca_marketplace_py2026.duckdb`.
No numbers in this document are hand-entered or fabricated.

## Executive KPI snapshot

| Metric | Value |
| --- | --- |
| Raw CMS rows loaded | 3,887,640 |
| Conformed plans modeled | 5,144 |
| Issuers modeled | 359 |
| States represented | 30 |
| Total geography rows | 6,272 |
| Service-area geography rows | 5,923 |
| Rating-area geography rows | 349 |
| Quality PUF plan rows | 4,302 |

## Selected findings from PY2026 CMS data

- The marts model 5,144 conformed standard-component plans across 30 states and 359 issuers.
- Silver plans represent 29.7% of modeled plans (1,528 plans).
- Across all modeled premium rows, Platinum has the highest median monthly premium at $1,480.33; Low has the lowest at $19.96.
- TX has the most issuers represented in the marts (32 issuers).
- 16 states have more than 10 issuers represented.
- 4,394 of 5,923 service-area geography rows have one issuer represented, marking them for closer market review.
- Plan history modeling identifies 3,815 current plans that continue under the same plan ID and 909 current plans that are new or not represented in the crosswalk.
- The Quality PUF contributes 4,302 plan-level quality rows; 1,603 have an overall 3-star rating and 1,005 have an overall 4-star rating.
- 4,183 Quality PUF rows join to the modeled PY2026 plan dimension for quality-vs-cost analysis.

These findings are descriptive summaries of public CMS plan and premium data. They are not causal conclusions and are not enrollment weighted.

## Plan count by metal level

| Metal level | Plan count | Percent of plans |
| --- | --- | --- |
| Silver | 1,528 | 29.7% |
| Gold | 1,217 | 23.7% |
| Expanded Bronze | 1,180 | 22.9% |
| Low | 523 | 10.2% |
| High | 419 | 8.1% |
| Bronze | 149 | 2.9% |
| Catastrophic | 75 | 1.5% |
| Platinum | 53 | 1.0% |

## Issuer count by state

| State | Issuer count |
| --- | --- |
| TX | 32 |
| FL | 26 |
| OH | 24 |
| MI | 21 |
| WI | 19 |
| AZ | 17 |
| MO | 16 |
| IN | 14 |
| UT | 14 |
| NC | 13 |
| OK | 13 |
| TN | 13 |
| LA | 12 |
| AL | 11 |
| KS | 11 |

Only the top 15 states are shown here for readability.

## Premium by metal level

| Metal level | Premium rows | Average monthly premium | Median monthly premium |
| --- | --- | --- | --- |
| Platinum | 45,492 | $1,753.93 | $1,480.33 |
| Gold | 378,114 | $969.95 | $815.89 |
| Silver | 484,602 | $910.86 | $766.34 |
| Bronze | 46,257 | $723.27 | $615.63 |
| Expanded Bronze | 372,759 | $703.95 | $595.63 |
| Catastrophic | 13,923 | $540.10 | $459.43 |
| High | 400,558 | $32.17 | $34.29 |
| Low | 494,056 | $92.36 | $19.96 |

Premium metrics are calculated across modeled Rate PUF rows and therefore vary by rating area, age, tobacco status, and effective date. They are not enrollment weighted.

## Deductible and out-of-pocket maximum by metal level

| Metal level | Plan count | Average deductible | Average out-of-pocket maximum |
| --- | --- | --- | --- |
| Catastrophic | 75 | $10,600 | $10,600 |
| Bronze | 149 | $9,299 | $10,457 |
| Expanded Bronze | 1,180 | $7,258 | $9,859 |
| Silver | 1,528 | $5,114 | $9,129 |
| Gold | 1,217 | $1,772 | $8,106 |
| Platinum | 53 | $51 | $4,370 |
| Low | 523 | n/a | n/a |
| High | 419 | n/a | n/a |

Deductible and out-of-pocket maximum values come from public Plan Attributes PUF plan design fields, not claims or member spend.

## Top 10 service-area geographies by plan count

| State | Geography label | Service area | Plan count | Issuer count |
| --- | --- | --- | --- | --- |
| OH | OHS001 | OHS001 | 97 | 14 |
| OH | Stark | OHS001 | 94 | 6 |
| FL | Seminole | FLS001 | 93 | 8 |
| OH | Lorain | OHS001 | 93 | 6 |
| TX | Collin | TXS001 | 90 | 10 |
| TX | Dallas | TXS001 | 90 | 10 |
| FL | Palm Beach | FLS001 | 85 | 9 |
| FL | Lake | FLS001 | 84 | 8 |
| TX | Ellis | TXS001 | 83 | 9 |
| TX | Rockwall | TXS001 | 83 | 9 |

Geography labels prefer `county_display_name` from the Census FIPS seed; unmatched CMS county values retain the raw Service Area value.

## Examples of low-competition markets

| State | Geography label | Service area | Plan count | Issuer count |
| --- | --- | --- | --- | --- |
| MI | MIS009 | MIS009 | 29 | 1 |
| FL | Collier | FLS004 | 25 | 1 |
| FL | Indian River | FLS004 | 25 | 1 |
| FL | Jefferson | FLS004 | 25 | 1 |
| FL | Nassau | FLS004 | 25 | 1 |
| FL | Sarasota | FLS004 | 25 | 1 |
| FL | Wakulla | FLS004 | 25 | 1 |
| NE | Cass | NES002 | 20 | 1 |
| NE | Fillmore | NES002 | 20 | 1 |
| NE | Johnson | NES002 | 20 | 1 |

The marts identify 4,394 service-area geography rows with one issuer represented. These markets may merit closer product, actuarial, or operations review, but public PUF data alone does not explain the cause of limited competition.

## Plan continuity and market churn

| Continuity status | History rows | Current plans | Previous plans |
| --- | --- | --- | --- |
| continuing_same_plan | 3,815 | 3,815 | 3,679 |
| new_or_not_in_crosswalk | 909 | 909 | 0 |
| crosswalked_from_prior_plan | 420 | 420 | 370 |
| discontinued_or_no_2026_crosswalk | 415 | 0 | 415 |

## Top issuers by current plan count

| State | Issuer ID | Current plans | New/not-in-crosswalk plans | Crosswalked plans |
| --- | --- | --- | --- | --- |
| TX | 33602 | 552 | 11 | 1 |
| NC | 11512 | 117 | 17 | 3 |
| AZ | 53901 | 115 | 0 | 0 |
| TX | 20069 | 100 | 35 | 0 |
| OK | 87571 | 98 | 4 | 0 |
| TN | 14002 | 96 | 34 | 0 |
| WI | 38166 | 89 | 59 | 0 |
| FL | 30252 | 83 | 6 | 5 |
| NE | 29678 | 78 | 28 | 6 |
| SC | 26065 | 76 | 2 | 1 |

## Quality rating distribution

| Overall rating value | Quality PUF rows |
| --- | --- |
| 1 | 43 |
| 2 | 444 |
| 3 | 1,603 |
| 4 | 1,005 |
| 5 | 44 |
| NR - New-Ineligible for Scoring | 491 |
| NR - Not Rated | 672 |

## Quality vs premium where plan joins are available

| Overall rating | Joined plans | Average monthly premium | Median plan premium |
| --- | --- | --- | --- |
| 1 | 40 | $868.56 | $713.38 |
| 2 | 437 | $804.33 | $651.29 |
| 3 | 1,569 | $865.39 | $704.97 |
| 4 | 994 | $768.20 | $623.99 |
| 5 | 43 | $768.98 | $653.62 |

Quality-vs-premium metrics are limited to Quality PUF rows that join to `dim_plan`. The Quality PUF also includes some rows outside the modeled Exchange PUF plan universe; those rows are retained and flagged with `joins_to_dim_plan` in `fact_plan_quality_rating`.

## Limitations surfaced by the insight queries

- County display names are enriched from the Census FIPS reference seed when a match is found; unmatched CMS county values retain the raw Service Area value.
- Premium metrics are not enrollment weighted because enrollment is not included in the selected public PUFs.
- The current model focuses on public plan design, premiums, availability, plan history, and Quality PUF ratings; it does not include provider networks, claims, or member-level data.
- The dashboard preview in `assets/dashboard_preview.png` is a static visual generated from these aggregate queries, not a deployed BI application.

## Reproduce this snapshot

```bash
python3 scripts/load_to_duckdb.py
cd dbt_project && dbt build --profiles-dir .
cd ..
python3 scripts/generate_case_study_outputs.py
```
