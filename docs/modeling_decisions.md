# Modeling Decisions

This document explains the major analytics engineering decisions behind the ACA
Marketplace Intelligence Mart.

## Why a star schema

The CMS PUFs are operational public-use files, not business-facing analytics
tables. A star schema makes the data easier to use in SQL, BI tools, and
semantic layers by separating descriptive dimensions from measurable facts.

The mart layer is organized around three analytical events:

1. Premium observations
2. Plan availability by geography
3. Benefit cost-sharing rows
4. Plan continuity from PY2025 to PY2026
5. Plan-level Quality PUF ratings

Shared dimensions make common filters consistent across facts.

## Fact table grains

| Fact table | Grain | Why this grain was chosen |
| --- | --- | --- |
| `fact_premium` | Plan, issuer, state, rating area, age, tobacco usage, and rate effective date | Matches Rate PUF pricing behavior and supports actuarial-style premium comparisons by geography, age, and metal level. |
| `fact_plan_availability` | Plan, issuer, service area, and service-area geography | Supports county/service-area plan count and issuer competition questions. |
| `fact_benefit_cost_sharing` | Plan, issuer, benefit, and cost-sharing configuration | Preserves benefit-level cost-sharing detail while enabling coverage-rate metrics. |
| `fact_plan_quality_rating` | Quality PUF plan row | Preserves the actual plan-level grain of the CMS Quality PUF and supports quality distribution and quality-vs-premium analysis where joins are available. |

## Dimension tables

| Dimension | Purpose |
| --- | --- |
| `dim_plan` | Conformed standard-component plan attributes, plan type, metal level, deductible, out-of-pocket maximum, and variant count. |
| `dim_issuer` | Issuer identifiers and state/year context. |
| `dim_geography` | Rating-area and service-area geography values used by premium and availability facts. |
| `dim_metal_level` | ACA metal-level ordering and accepted values. |
| `dim_benefit` | Benefit names and simple benefit categories. |
| `dim_age_band` | BI-friendly age bands for premium analysis. |
| `dim_plan_history` | PY2025 to PY2026 plan continuity and crosswalk status. |

## Conformed plan grain

Real validation showed that the Rate PUF uses standard component identifiers,
while Plan Attributes and Benefits include plan variant IDs. `dim_plan` is
therefore modeled at standard component grain so premiums can join cleanly to
plan design attributes. The column `plan_variant_count` preserves how many Plan
Attributes variants roll into each standard component.

## Plan history / SCD-style modeling

The CMS Plan ID Crosswalk PUF maps PY2025 plans to PY2026 plans and includes
crosswalk reasons plus geographic crosswalk detail. `dim_plan_history`
summarizes that raw crosswalk into a BI-friendly history dimension with:

- `effective_plan_year`
- `previous_plan_id`
- `current_plan_id`
- `is_current`
- `continuity_status`

The supported continuity statuses are:

- `continuing_same_plan`
- `crosswalked_from_prior_plan`
- `new_or_not_in_crosswalk`
- `discontinued_or_no_2026_crosswalk`

This is not a full multi-year SCD Type 2 table yet, but it demonstrates the
modeling pattern needed to track plan continuity and churn across plan years.

## Quality PUF modeling

CMS publishes both a plan-level Quality PUF and a Nationwide QRS PUF at broader
reporting-unit/product grain. This v2 project uses only the requested PY2026
Quality PUF because it supports cleaner plan-level joins to the existing marts.
Rows that do not join to `dim_plan` are retained in `fact_plan_quality_rating`
and flagged with `joins_to_dim_plan`.

## Geography modeling

Premiums are published by rating area. Plan availability is published through
service areas and county-like values. `dim_geography` supports both geography
types with a `geography_type` flag:

- `rating_area`
- `service_area_county`

Service Area PUF county values are used as published. Some behave like FIPS
codes rather than display-ready county names, so a production model should add a
county reference dimension.

## Why DuckDB locally

DuckDB is a good fit for this portfolio project because it:

- Handles multi-million-row CSV files locally.
- Requires no cloud account or paid warehouse.
- Works well with dbt through `dbt-duckdb`.
- Keeps the project reproducible for reviewers.

DuckDB is not presented as a production deployment. It is the local development
warehouse used to demonstrate analytics engineering patterns.

## Migration path to BigQuery or Snowflake

The project is designed so a cloud migration would mainly require:

1. Loading raw CMS files to object storage or warehouse staging tables.
2. Replacing the DuckDB dbt profile with BigQuery, Snowflake, Redshift, or
   Databricks credentials.
3. Reviewing dialect-specific SQL functions such as `median`, `md5`,
   `string_agg`, and date casting.
4. Adding CI/CD, scheduled ingestion, freshness tests, and access controls.
5. Publishing BI explores or semantic models against the cloud mart schemas.

## LookML semantic layer

The LookML files sit on top of the dbt marts and define business-friendly views,
dimensions, measures, and explores for:

- Plan availability
- Premium benchmarking
- Benefit cost sharing
- Geography filters

This mirrors how analytics engineering teams separate warehouse modeling from BI
metric consumption.

## Intentionally not modeled yet

- Claims, enrollment, subsidy eligibility, or member-level data.
- Provider network files.
- Nationwide QRS reporting-unit/product-level quality detail.
- County reference names and geospatial shapes.
- Production orchestration, deployment, and monitoring.
