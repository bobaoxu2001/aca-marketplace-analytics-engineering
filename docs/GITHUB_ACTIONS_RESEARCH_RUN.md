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
4. Downloads the official CMS/HealthData ACA Marketplace PY2026 public files
   through Socrata row APIs when the official views are tabular. If the official
   PY2026 views are exposed only as Socrata `href` assets, the workflow records
   that as a data-access diagnostic instead of fabricating rows.
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
4. Click **Run workflow**.
5. Choose the branch containing this workflow.
6. Click **Run workflow** again.

## Trigger With GitHub CLI

After the workflow branch is pushed:

```bash
gh workflow run metric_grounded_research_run.yml --ref research/github-actions-data-run
```

To watch the run:

```bash
gh run list --workflow metric_grounded_research_run.yml
gh run watch
```

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

If the official Socrata views are non-tabular `href` assets or the download
fails, the workflow fails intentionally after uploading
`socrata_download_report.json` and `download_failure_report.json`; skipped
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
