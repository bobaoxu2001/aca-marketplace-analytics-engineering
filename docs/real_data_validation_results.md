# Real Data Validation Results

Validated on June 12, 2026 using official CMS Plan Year 2026 Marketplace Public
Use Files downloaded from `https://download.cms.gov/marketplace-puf/2026/`.

## Download results

The downloader attempted Data.HealthCare.gov and catalog.data.gov metadata
discovery first; those API searches returned HTTP 404 in this environment. The
script then used direct CMS Marketplace PUF ZIP URLs and successfully downloaded
all four required files.

| Dataset | CMS ZIP URL | Local filename | Rows | Columns |
| --- | --- | --- | ---: | ---: |
| Rate PUF - PY2026 | `https://download.cms.gov/marketplace-puf/2026/rate-puf.zip` | `rate_puf_py2026.csv` | 2,235,761 | 20 |
| Plan Attributes PUF - PY2026 | `https://download.cms.gov/marketplace-puf/2026/plan-attributes-puf.zip` | `plan_attributes_puf_py2026.csv` | 22,059 | 151 |
| Benefits and Cost Sharing PUF - PY2026 | `https://download.cms.gov/marketplace-puf/2026/benefits-and-cost-sharing-puf.zip` | `benefits_cost_sharing_puf_py2026.csv` | 1,457,952 | 24 |
| Service Area PUF - PY2026 | `https://download.cms.gov/marketplace-puf/2026/service-area-puf.zip` | `service_area_puf_py2026.csv` | 8,820 | 14 |

## Raw profiling highlights

| Dataset | Duplicate check key | Duplicate groups | Key field coverage notes |
| --- | --- | ---: | --- |
| Rate PUF | BusinessYear, StateCode, IssuerId, PlanId, RatingAreaId, Tobacco, Age, RateEffectiveDate | 0 | All key fields were 100% populated except Tobacco at 99.99%. |
| Plan Attributes PUF | BusinessYear, StateCode, IssuerId, PlanId | 0 | All selected key fields were 100% populated. |
| Benefits and Cost Sharing PUF | BusinessYear, StateCode, IssuerId, PlanId, BenefitName | 0 | All selected key fields were 100% populated. |
| Service Area PUF | BusinessYear, StateCode, IssuerId, ServiceAreaId, County | 0 | BusinessYear, StateCode, IssuerId, and ServiceAreaId were 100% populated; County was 97.14% populated because some service areas cover an entire state or have non-county rows. |

Full null-rate and sample-value profiles are generated locally at:

- `data/processed/raw_profile_py2026.json`
- `data/processed/raw_profile_py2026.md`

These files are generated artifacts and are intentionally not committed.

## DuckDB load results

| Raw table | Rows loaded |
| --- | ---: |
| `rate_puf_py2026` | 2,235,761 |
| `plan_attributes_puf_py2026` | 22,059 |
| `benefits_cost_sharing_puf_py2026` | 1,457,952 |
| `service_area_puf_py2026` | 8,820 |

## dbt validation status

Commands run against the real DuckDB database:

```bash
cd dbt_project
dbt parse --profiles-dir . --no-partial-parse
dbt run --profiles-dir .
dbt test --profiles-dir .
dbt build --profiles-dir .
```

Final `dbt build` status:

```text
PASS=83 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=83
```

## Mart row counts

| Model | Rows |
| --- | ---: |
| `dim_issuer` | 359 |
| `dim_plan` | 5,144 |
| `dim_geography` | 6,272 |
| `dim_metal_level` | 8 |
| `dim_benefit` | 273 |
| `dim_age_band` | 7 |
| `fact_premium` | 2,235,761 |
| `fact_plan_availability` | 73,842 |
| `fact_benefit_cost_sharing` | 1,457,952 |

## Real-data modeling fixes made during validation

- PY2026 Rate, Benefits, and Service Area files do not include `VersionNum`; the
  staging models now emit a nullable `version_num` field.
- PY2026 Rate PUF does not include `FederalTIN`; `stg_rate_puf` now emits a
  nullable `federal_tin` field.
- PY2026 Plan Attributes stores deductible and out-of-pocket maximum values in
  detailed `TEHB`, `MEHB`, and `DEHB` columns. Staging now maps:
  - `TEHBDedInnTier1Individual` to integrated deductible metrics.
  - `MEHBDedInnTier1Individual` to medical deductible metrics.
  - `DEHBDedInnTier1Individual` to drug deductible metrics.
  - `TEHBInnTier1IndividualMOOP` to integrated out-of-pocket maximum metrics.
- Rate PUF uses standard component identifiers, while Plan Attributes and
  Benefits include plan variant IDs. `dim_plan` is now conformed at standard
  component grain and includes `plan_variant_count`.
- Service Area rows repeat across issuers and market contexts. `dim_geography`
  now deduplicates service-area county geography at the natural geography grain.

## Known limitations

- Raw CSVs, profile outputs, DuckDB database files, dbt targets, and caches are
  local generated artifacts and are not committed.
- CMS Service Area `County` values are used as published. They often behave like
  county FIPS identifiers rather than display-ready county names; production BI
  use should join to a county reference dimension for friendly names.
- The warehouse uses public plan design and premium data only. It does not
  include claims, enrollment, subsidy eligibility, or member demographics.
- DuckDB is used for local development. The dbt layering, tests, and marts are
  structured to be portable to a cloud warehouse with adapter-specific profile
  changes.

## How to reproduce

```bash
python3 -m pip install -r requirements.txt
python3 scripts/download_cms_pufs.py --force
python3 scripts/profile_raw_data.py
python3 scripts/load_to_duckdb.py
cd dbt_project
dbt parse --profiles-dir . --no-partial-parse
dbt run --profiles-dir .
dbt test --profiles-dir .
dbt build --profiles-dir .
```
