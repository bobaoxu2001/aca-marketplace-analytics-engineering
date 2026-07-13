# PhD Application Research Brief

## Metric-Grounded Analytics Agents: Measuring Semantic Reliability Beyond Executable SQL

This independent project studies whether explicit metric definitions and
execution evidence make natural-language analytics agents easier to verify. It
combines a DuckDB/dbt warehouse over six official CMS PY2026 public-use files,
a 30-question ACA Marketplace benchmark, three distinct agent conditions, and
failure-aware result-level evaluation.

The main methodological contribution is a strict result contract that separates
successful execution from identical output, plus compatible-projection, Top-k,
group, numeric-error, traceability, abstention, and claim-support diagnostics.
In a three-repeat subscription-Codex pilot, all 90 generated SQL queries
executed but only 3.3% strictly matched the reference result; 18.9% matched the
more permissive compatible projection. A benchmark-specific oracle compiler
reached 80.0% strict match on original questions, but only 40.0% on a locked,
model-generated high-shift challenge. These are pilot/development diagnostics,
not model-general or confirmatory results.

The project is suitable as a PhD application research sample because its
research question, negative findings, measurement corrections, and claim
boundaries are inspectable. Before workshop submission it still needs a fresh
human-authored or independently validated locked set, two completed independent
reviews, a second gold-SQL audit, and a model-specific API rerun.

Natural doctoral extensions include learned semantic routing under schema
shift, calibrated abstention, claim-to-cell entailment, cross-domain transfer,
and human studies comparing evidence-first with answer-first interfaces.
