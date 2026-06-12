# Insight Snapshot: PY2026 ACA Marketplace Marts

Generated from real dbt mart tables in `data/processed/aca_marketplace_py2026.duckdb`.
No numbers in this document are hand-entered or fabricated.

## Executive KPI snapshot

| Metric | Value |
| --- | --- |
| Raw CMS rows loaded | 3,724,592 |
| Conformed plans modeled | 5,144 |
| Issuers modeled | 359 |
| States represented | 30 |
| Total geography rows | 6,272 |
| Service-area geography rows | 5,923 |
| Rating-area geography rows | 349 |

## Selected findings from PY2026 CMS data

- The marts model 5,144 conformed standard-component plans across 30 states and 359 issuers.
- Silver plans represent 29.7% of modeled plans (1,528 plans).
- Across all modeled premium rows, Platinum has the highest median monthly premium at $1,480.33; Low has the lowest at $19.96.
- TX has the most issuers represented in the marts (32 issuers).
- 16 states have more than 10 issuers represented.
- 4,394 of 5,923 service-area geography rows have one issuer represented, marking them for closer market review.

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
| OH | 39151 | OHS001 | 94 | 6 |
| FL | 12117 | FLS001 | 93 | 8 |
| OH | 39093 | OHS001 | 93 | 6 |
| TX | 48085 | TXS001 | 90 | 10 |
| TX | 48113 | TXS001 | 90 | 10 |
| FL | 12099 | FLS001 | 85 | 9 |
| FL | 12069 | FLS001 | 84 | 8 |
| TX | 48139 | TXS001 | 83 | 9 |
| TX | 48397 | TXS001 | 83 | 9 |

CMS Service Area `County` values are used as published and may be FIPS-like identifiers rather than display-friendly county names.

## Examples of low-competition markets

| State | Geography label | Service area | Plan count | Issuer count |
| --- | --- | --- | --- | --- |
| MI | MIS009 | MIS009 | 29 | 1 |
| FL | 12021 | FLS004 | 25 | 1 |
| FL | 12061 | FLS004 | 25 | 1 |
| FL | 12065 | FLS004 | 25 | 1 |
| FL | 12089 | FLS004 | 25 | 1 |
| FL | 12115 | FLS004 | 25 | 1 |
| FL | 12129 | FLS004 | 25 | 1 |
| NE | 31025 | NES002 | 20 | 1 |
| NE | 31059 | NES002 | 20 | 1 |
| NE | 31097 | NES002 | 20 | 1 |

The marts identify 4,394 service-area geography rows with one issuer represented. These markets may merit closer product, actuarial, or operations review, but public PUF data alone does not explain the cause of limited competition.

## Limitations surfaced by the insight queries

- County display names are not modeled yet; the Service Area PUF county field is used as published.
- Premium metrics are not enrollment weighted because enrollment is not included in the selected public PUFs.
- The current model focuses on public plan design, premiums, and availability; it does not include quality ratings, provider networks, claims, or member-level data.
- The dashboard preview in `assets/dashboard_preview.png` is a static visual generated from these aggregate queries, not a deployed BI application.

## Reproduce this snapshot

```bash
python3 scripts/load_to_duckdb.py
cd dbt_project && dbt build --profiles-dir .
cd ..
python3 scripts/generate_case_study_outputs.py
```
