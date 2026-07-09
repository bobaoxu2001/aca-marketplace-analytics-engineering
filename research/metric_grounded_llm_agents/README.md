# Metric-Grounded LLM Agents for Reliable Domain Analytics

This research layer studies a specific failure mode in analytics agents: fluent
answers that are not supported by executable domain metrics. It builds on the
existing ACA Marketplace Analytics Engineering warehouse and uses only official
CMS public Marketplace PUF data after the parent pipeline has downloaded,
loaded, and built the DuckDB/dbt marts.

## What Is Included

- A 30-question benchmark in `benchmark/questions.yaml`.
- Gold SQL for every question under `benchmark/gold_sql/`.
- A semantic metric registry in `configs/metrics.yaml`.
- Three system variants:
  - direct LLM baseline interface,
  - LLM + SQL baseline interface,
  - metric-grounded agent with metric constraints, SQL validation, and citations.
- Evaluation scripts that produce `results.csv`, `summary.json`, and
  `evaluation_report.md`.
- A CLI demo that shows the answer, SQL, metric definitions, validation checks,
  citations, and support status.
- A workshop-style paper draft in `paper/paper.md`.

## Data Honesty

This folder does not commit CMS raw CSVs, local DuckDB databases, generated dbt
targets, or fabricated benchmark outputs. If `data/processed/aca_marketplace_py2026.duckdb`
is missing, scripts return a clear skipped or missing-database status.

The required official file URLs are listed in `configs/data_sources.yaml`.

## Setup

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/download_cms_pufs.py
python3 scripts/load_to_duckdb.py
cd dbt_project
dbt build --profiles-dir .
cd ..
```

## Generate Gold Answers

```bash
python3 research/metric_grounded_llm_agents/benchmark/generate_gold_answers.py
```

For a smoke run:

```bash
python3 research/metric_grounded_llm_agents/benchmark/generate_gold_answers.py --limit 3
```

Gold answers are written to `benchmark/gold_answers/` as JSON.

## Run Evaluation

```bash
python3 research/metric_grounded_llm_agents/evaluation/run_eval.py
```

Smoke test the first three questions:

```bash
python3 research/metric_grounded_llm_agents/evaluation/run_eval.py --limit 3
```

Outputs are written to `research/metric_grounded_llm_agents/evaluation/results/`.

If the CMS raw files or local DuckDB database are missing, evaluation still
writes output files, but all data-dependent systems are marked as skipped and
`execution_success_rate` remains `0.0`. Treat that as a reproducibility
diagnostic, not as a research result.

## Run Demo

```bash
python3 research/metric_grounded_llm_agents/demo/cli.py --question-id Q001
```

The CLI prints JSON containing:

- natural-language answer,
- generated or selected SQL,
- metric definitions,
- validation checks,
- source table and result-row citations,
- final support status.

## Benchmark Design

The question set covers simple, intermediate, and hard ACA analytics tasks:
premiums, competition, plan availability, benefit coverage, plan continuity,
quality ratings, and quality-vs-premium association. Each question is paired
with gold SQL over dbt marts so numerical answers can be regenerated locally.

## Current Limitations

- The live Direct LLM adapter is intentionally a placeholder unless API
  credentials and model config are provided.
- The LLM + SQL baseline uses deterministic gold SQL until a live SQL-generation
  adapter is configured. This makes local verification possible without
  fabricating LLM behavior.
- The metric-grounded agent currently maps benchmark questions to approved
  metrics from metadata. A stronger research version should add a learned or
  rule-based mapper for unseen questions.
- No evaluation numbers should be reported in the paper until `run_eval.py`
  executes against the real local DuckDB/dbt marts.

## Reproducibility Notes

The full data-backed run depends on six official public CMS/HealthData files:
Rate PUF, Plan Attributes PUF, Benefits and Cost Sharing PUF, Service Area PUF,
Plan ID Crosswalk PUF, and Quality PUF for PY2026. In this Codex runtime, the
catalog metadata was reachable, but direct CSV/ZIP downloads returned HTTP 403,
so gold answers could not be generated here. On a local machine with access to
those public URLs, run:

```bash
python3 scripts/download_cms_pufs.py
python3 scripts/load_to_duckdb.py
cd dbt_project && dbt build --profiles-dir . && cd ..
python3 research/metric_grounded_llm_agents/benchmark/generate_gold_answers.py
python3 research/metric_grounded_llm_agents/evaluation/run_eval.py
```
