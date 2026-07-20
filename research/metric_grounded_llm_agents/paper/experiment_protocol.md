# Publication Experiment Protocol

## Freeze before running

- Create a release tag and record the commit SHA.
- Record source URLs, retrieval timestamps, byte sizes, and SHA-256 hashes.
- Record Python, DuckDB, dbt, model, and operating-system versions.
- Freeze prompts, model temperature, retry policy, and question ordering.
- Have a second reviewer inspect all 30 reference SQL queries.

## Primary comparisons

1. Direct LLM versus schema-conditioned LLM-to-SQL.
2. Schema-conditioned LLM-to-SQL versus oracle-routed metric grounding.
3. All systems by question difficulty and domain.

The metric-grounded condition is an oracle-routing upper bound. Do not describe
it as end-to-end natural-language metric selection.

## Required outputs

- One immutable JSON record per system-question run.
- Generated SQL and validation outcomes.
- Normalized result comparison with the reference answer.
- Support status and citations.
- Latency, failure class, and retry count.
- Aggregate tables generated from JSON, never manually copied.

The implemented runner additionally records the exact prompt and instructions,
model snapshot, response identifier, request parameters, input/output token
usage, dated pricing snapshot, estimated USD cost, latency, exception class,
and repeat index. Run at least three repeats for each stochastic
system-question condition. Run deterministic conditions once for statistical
analysis; any retained duplicate technical records must be labeled and averaged
within question rather than treated as independent observations.

The primary automated measure is end-to-end strict result match: identical
columns, row count, and complete cell values after scalar normalization, with
failures and abstentions counted as zero. Compatible projection, rank order,
numeric error/SMAPE, Top-k precision/recall/Jaccard, group
precision/recall/F1/Jaccard, and numeric-claim faithfulness are diagnostics.
Conditional metrics must state their executed-run denominator. Qualitative
faithfulness is intentionally reserved for human review below.

## Human review

Hide system labels from two independent reviewers for a stratified sample
covering every domain and difficulty. This is system-label blinding, not full
condition blinding: SQL and evidence format may reveal system family. Rate
metric correctness, answer faithfulness, caveat quality, and whether each
numerical claim is supported. Report agreement and adjudication rules.

A 90-item packet covering all 30 questions for Direct Codex, Codex-to-SQL, and
metric-grounded repeat zero is generated under `evaluation/human_review_v1/`.
Reviewers receive only `human_review_packet.csv`; the system key remains hidden
until both reviews are complete.

## Claims gate

Do not insert comparative percentages into the manuscript unless the complete
run finishes with real CMS marts and the output directory contains the commit,
data-provenance, and model metadata. Blocked runs are reproducibility findings,
not model-performance results.
