# NYC 311 Second-Domain Benchmark

A second, non-healthcare domain used to test whether the paper's core finding —
executable SQL is a weak proxy for semantic correctness, and metric grounding
helps executability/fidelity without reaching strict correctness — holds outside
the CMS Marketplace benchmark. If it reproduces here, the "you may be overfit to
your own benchmark" objection is removed.

## Contents

- `questions.yaml` — 30 questions (10 simple / 12 intermediate / 8 hard) mirroring
  the CMS benchmark schema (id, difficulty, category, metrics, source_tables,
  gold_sql).
- `gold_sql/N0*.sql` — one reference query per question, against the `marts`
  schema of `data/processed/nyc311_2024.duckdb`.
- `gold_answers/N0*.json` — executed reference results (row_count + rows).

## Data & warehouse

- Source: NYC Open Data 311 Service Requests (`erm2-nwe9`), full-year 2024,
  3,456,770 rows (all `unique_key` distinct).
- Download: `data/raw/nyc311/download_paginated.sh` (Socrata caps single
  responses ~230k rows, so it paginates 50k pages under a total order).
- Build: `benchmark/build_nyc311_warehouse.py` → `marts.fact_service_request`,
  `dim_agency`, `dim_complaint`, `dim_borough` (2020 Census population).
- Registry: `configs/metrics.nyc311.yaml`.

Raw CSVs and the `.duckdb` are gitignored; rebuild from the two scripts.

## Verification (audit)

All 30 gold SQL execute against the built warehouse and return non-empty results.
The design deliberately encodes contested definitions so the schema-only LLM
baseline can diverge from the registry-grounded condition:

| Trap | Questions | Registry-correct behavior |
| --- | --- | --- |
| Per-capita vs raw counts | N011, N018, N024 | join `dim_borough`, divide by population; excludes `Unspecified` (no population). Bronx leads per-capita (501/1k) though Brooklyn leads raw counts. |
| Unresolved handling in response time | N006, N010, N012, N014, N015, N022, N023, N025, N026 | `response_hours` is null unless closed and closed>=created; open requests excluded, not counted as zero. |
| Which statuses count as resolved | N007, N008, N017, N020, N030 | only `status = 'Closed'`; the other six statuses do not. |
| Mean vs median under heavy right skew | N014, N015, N028 | median is the default; mean reported only alongside it (max response ~22,028 h). |
| Window denominator for shares | N013, N019 | `sum(count(*)) over ()` / per-borough total, not a re-scanned count. |
| Complaint_type vs descriptor grain | N003, N021, N029 | complaint_type is the default grain; descriptor (959 values) is finer and not used unless asked. |

Some volume/rate questions intentionally return 6 borough rows (5 boroughs +
`Unspecified`); per-capita questions return 5 (the join drops `Unspecified`).
This asymmetry is the intended, documented behavior, not an inconsistency.

## Status

Reference benchmark complete and execution-verified. Running the LLM conditions
(direct / llm_sql / llm_registry_sql / metric_grounded) on this domain additionally
requires pointing the agent at the NYC registry+warehouse and an API key; that
harness wiring is the remaining step before second-domain results can be reported.
