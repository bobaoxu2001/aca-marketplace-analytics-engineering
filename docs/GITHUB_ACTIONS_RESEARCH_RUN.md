# GitHub Actions Research Run

This repository includes a manual GitHub Actions workflow that runs the full
Metric-Grounded LLM Agents research pipeline on a GitHub-hosted runner.

Workflow file:

```text
.github/workflows/metric_grounded_research_run.yml
```

## What It Does

The workflow:

1. Checks out the repository.
2. Sets up Python 3.11.
3. Installs Python dependencies, `dbt-core`, and `dbt-duckdb`.
4. Resolves official CMS/HealthData ACA Marketplace PY2026 file assets from
   Socrata/Data.gov/CMS metadata, then downloads those CSV/ZIP files as files.
5. Validates the raw CSV files.
6. Loads raw files into DuckDB.
7. Builds the dbt marts.
8. Generates benchmark gold answers.
9. Runs the evaluation.
10. Uploads benchmark outputs, evaluation results, paper files, and a DuckDB
    artifact when the database is small enough.

The workflow does not commit raw CMS CSVs or generated databases to git.

## Trigger From GitHub UI

1. Open the repository on GitHub.
2. Go to **Actions**.
3. Select **Metric-Grounded Research Data Run**.
4. Confirm the workflow file has first been merged into `main`. GitHub cannot
   manually dispatch a brand-new workflow from a feature branch before the file
   exists on the default branch.
5. Click **Run workflow**, select `main`, and click **Run workflow** again.

## Trigger With GitHub CLI

First merge the workflow file into `main`. Then run:

```bash
gh workflow run metric_grounded_research_run.yml --ref main
```

To watch the run:

```bash
gh run list --workflow metric_grounded_research_run.yml
gh run watch
```

After the workflow exists on `main`, a branch ref can be selected for later
runs. It cannot bootstrap manual dispatch for a brand-new workflow.

## Artifacts

When the run finishes, open the workflow run page and download artifacts from
the **Artifacts** section.

Expected artifacts:

- `metric-grounded-research-outputs`
  - `research/metric_grounded_llm_agents/benchmark/gold_answers/`
  - `research/metric_grounded_llm_agents/evaluation/results/`
  - `research/metric_grounded_llm_agents/paper/`
- `aca-marketplace-duckdb`
  - included only when `data/processed/aca_marketplace_py2026.duckdb` is at or
    below the workflow size threshold
- `download-failure-diagnostics`
  - included when the official public file hosts still block downloads

The PY2026 PUF Socrata IDs are non-tabular `href`/file assets, so the row API is
not used for the main pipeline. If official file downloads fail, the workflow
fails intentionally after uploading `download_failure_report.json`; skipped
outputs should not be interpreted as research results.

## Local Equivalent

Run the same sequence locally:

```bash
make research-full-run
```

Print GitHub trigger instructions:

```bash
make research-github-help
```
