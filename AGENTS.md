# AGENTS.md

## Cursor Cloud specific instructions

This repo is a **local, batch ELT data pipeline** (Python + DuckDB + dbt). There
is **no server, API, frontend, or listening port** — everything runs as CLI
steps against an embedded DuckDB file. The "app working" bar is a clean
`dbt build` (`PASS=108 WARN=0 ERROR=0`). See `README.md` Quickstart for the
canonical command list.

### Environment

- Python deps are installed into a `.venv` at the repo root by the update script.
  Always activate it first: `source .venv/bin/activate` (or call binaries via
  `.venv/bin/...`). `.venv/` is gitignored.
- System package `python3.12-venv` is required to create the venv and is already
  present in the cloud image. (`python3 -m venv` fails without it.)

### Required data (not in git, must be fetched once)

- Raw CMS PUF CSVs and the DuckDB warehouse are gitignored and **not committed**,
  so a fresh checkout has no data. The update script does **not** download them
  (large ~700MB download + heavy load; kept out of startup).
- Hydrate the warehouse before running dbt:
  ```bash
  source .venv/bin/activate
  python3 scripts/download_cms_pufs.py   # needs network; saves to data/raw/py2026/
  python3 scripts/load_to_duckdb.py      # builds data/processed/aca_marketplace_py2026.duckdb
  ```
  `download_cms_pufs.py` is idempotent (skips existing files; `--force` to
  redownload). The Data.HealthCare.gov / catalog.data.gov discovery endpoints
  log `HTTP 404` and are skipped — this is expected; the direct
  `download.cms.gov` ZIP URLs are what actually succeed.

### Run / test / build (from `dbt_project/`)

- dbt's `profiles.yml` lives **inside** `dbt_project/`, so every dbt command needs
  `--profiles-dir .`:
  ```bash
  cd dbt_project && source ../.venv/bin/activate
  dbt debug --profiles-dir .
  dbt build --profiles-dir .          # builds models + runs all 108 tests
  dbt docs generate --profiles-dir .  # optional
  ```
- There is no separate lint step; dbt model/test validation via `dbt build` is the
  test+build gate. `dbt build` fails if `load_to_duckdb.py` has not been run
  (source tables missing).

### Optional outputs

- `python3 scripts/profile_raw_data.py` → raw profile reports in `data/processed/`.
- `python3 scripts/generate_case_study_outputs.py` → regenerates
  `docs/insight_snapshot.md` and PNGs in `assets/`. Note its markdown output has
  minor non-deterministic row ordering; avoid committing that churn unless intended.
