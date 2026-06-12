# ACA Marketplace Analytics Engineering

Portfolio-grade analytics engineering project using official CMS Plan Year 2026
ACA Marketplace Public Use Files. The project builds a reproducible local
warehouse that models plan pricing, benefit design, issuer competition, and
county-level plan availability for a tech-driven health insurance company.

## Business framing

Health insurance stakeholders need a trusted way to answer market questions:

- Which issuers and plans are available in each county?
- How do premiums vary by rating area, metal level, age band, and tobacco usage?
- How do deductible and out-of-pocket maximums differ by product design?
- Which benefits are commonly covered across plans and issuers?

This warehouse supports:

- **Analytics teams** with reproducible dbt marts and documented SQL metrics.
- **Product teams** with plan design, deductible, and benefit comparisons.
- **Actuarial teams** with premium benchmarks by age, geography, issuer, and
  metal level.
- **Operations teams** with county/service-area availability reporting.
- **Market strategy teams** with issuer competition and county opportunity
  analysis.

## Data source

Real data only. The pipeline is designed for official CMS/Data.HealthCare.gov
Health Insurance Exchange Public Use Files, Plan Year 2026:

1. Rate PUF - PY2026
2. Plan Attributes PUF - PY2026
3. Benefits and Cost Sharing PUF - PY2026
4. Service Area PUF - PY2026

Raw CSV files are intentionally ignored by git.

## Real data validation results

This project was validated against real official CMS PY2026 Marketplace PUF CSVs
downloaded from `https://download.cms.gov/marketplace-puf/2026/`.

| Dataset | Real rows validated |
| --- | ---: |
| Rate PUF - PY2026 | 2,235,761 |
| Plan Attributes PUF - PY2026 | 22,059 |
| Benefits and Cost Sharing PUF - PY2026 | 1,457,952 |
| Service Area PUF - PY2026 | 8,820 |

Final real-data `dbt build` status:

```text
PASS=83 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=83
```

See `docs/real_data_validation_results.md` for raw profiling highlights, mart
row counts, known limitations, and exact reproduction commands.

## Repository structure

```text
.
├── data/
│   ├── raw/py2026/              # Manual fallback location for CMS CSV files
│   └── processed/               # Local DuckDB database and profiling outputs
├── dbt_project/                 # dbt DuckDB project
│   ├── macros/
│   └── models/
│       ├── staging/
│       ├── intermediate/
│       └── marts/
├── docs/                        # Executive summary, metrics, sample SQL
├── dashboards/                  # Dashboard specification
├── lookml/                      # LookML semantic layer
└── scripts/                     # Download, profile, and DuckDB load scripts
```

## Quickstart

### 1. Create a Python environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Download or place raw CMS files

Try automatic discovery and download:

```bash
python scripts/download_cms_pufs.py
```

If automatic discovery succeeds, the four CSV files will be saved under
`data/raw/py2026/`.

### 3. Profile raw files

```bash
python scripts/profile_raw_data.py
```

Outputs:

- `data/processed/raw_profile_py2026.json`
- `data/processed/raw_profile_py2026.md`

The profile includes row counts, column counts, null rates, duplicate key checks,
and sample values.

### 4. Load raw CSVs into DuckDB

```bash
python scripts/load_to_duckdb.py
```

Output database:

```text
data/processed/aca_marketplace_py2026.duckdb
```

### 5. Build and test dbt models

```bash
cd dbt_project
dbt debug --profiles-dir .
dbt build --profiles-dir .
dbt docs generate --profiles-dir .
```

## Manual data download fallback

CMS public dataset links can change. If `scripts/download_cms_pufs.py` cannot
discover a reliable file URL, manually download the Plan Year 2026 Marketplace
PUF CSV files from CMS or Data.HealthCare.gov and place them in:

```text
data/raw/py2026/
```

Rename the files exactly:

```text
rate_puf_py2026.csv
plan_attributes_puf_py2026.csv
benefits_cost_sharing_puf_py2026.csv
service_area_puf_py2026.csv
```

Then continue with:

```bash
python scripts/profile_raw_data.py
python scripts/load_to_duckdb.py
cd dbt_project && dbt build --profiles-dir .
```

## Pipeline overview

1. **Download:** `scripts/download_cms_pufs.py` searches CMS,
   Data.HealthCare.gov, and catalog.data.gov metadata for Plan Year 2026 CSV/ZIP
   resources. If discovery fails, it prints clear manual fallback instructions.
2. **Profile:** `scripts/profile_raw_data.py` uses Polars lazy CSV scans to
   profile large files, including the Rate PUF.
3. **Load:** `scripts/load_to_duckdb.py` loads the four raw CSVs into a local
   DuckDB database as raw tables.
4. **Transform:** dbt builds layered staging, intermediate, and mart models.
5. **Serve:** LookML and sample SQL expose stakeholder-facing metrics.

## dbt architecture

### Staging

- `stg_rate_puf`
- `stg_plan_attributes_puf`
- `stg_benefits_cost_sharing_puf`
- `stg_service_area_puf`

Staging models standardize names, trim text fields, and cast dates/numeric
values.

### Intermediate

- `int_plan_base`
- `int_rate_enriched`
- `int_benefit_cost_sharing`

Intermediate models define reusable business grain and normalized attributes,
such as age bands and benefit coverage flags.

### Marts

Dimensions:

- `dim_issuer`
- `dim_plan`
- `dim_geography`
- `dim_metal_level`
- `dim_benefit`
- `dim_age_band`

Facts:

- `fact_premium`
- `fact_plan_availability`
- `fact_benefit_cost_sharing`

## Data quality and dbt tests

The dbt project includes:

- `not_null` tests on required keys and facts
- `unique` tests on dimensional surrogate keys and fact primary keys
- `accepted_values` tests for metal levels, geography types, and age bands
- `relationships` tests from facts to dimensions
- Model and column descriptions for dbt docs

## Business metrics

Defined in `docs/metric_dictionary.md`, `docs/sample_queries.sql`, and LookML:

- Average monthly premium
- Median silver premium
- Plan count by county
- Issuer count by county
- Average deductible
- Average out-of-pocket maximum
- Benefit coverage rate
- Premium difference by metal level

## Semantic layer

LookML files in `lookml/`:

- `plans.view.lkml`
- `premiums.view.lkml`
- `benefits.view.lkml`
- `geography.view.lkml`
- `marketplace_analytics.model.lkml`

These files define explores and measures for plan availability, premiums, and
benefit cost sharing.

## Stakeholder deliverables

- `docs/executive_summary.md`
- `docs/metric_dictionary.md`
- `docs/sample_queries.sql`
- `dashboards/dashboard_specification.md`

## Notes for cloud warehouse readiness

The project uses DuckDB locally for development, but the layered model design is
portable to Snowflake, BigQuery, Redshift, or Databricks with adapter-specific
profile changes. Raw file ingestion, staged typing, conformed dimensions, fact
grains, dbt tests, docs, and LookML semantics mirror production analytics
engineering workflows.
