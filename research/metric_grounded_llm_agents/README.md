# Metric-Grounded Analytics Agents: Measuring Semantic Reliability Beyond Executable SQL

**A research prototype for measuring semantic reliability, evidence traceability,
and failure behavior in natural-language analytics over U.S. ACA Marketplace
data.**

Status: **manuscript in preparation**. The current experiments are
benchmark-specific development and diagnostic studies, not evidence of general
healthcare reasoning or universal hallucination reduction.

Graduate admissions and faculty reviewers can use the
[PhD research-sample start page](../../docs/phd_application/README.md) for a
short, application-oriented reading path.

## Research question

Executable SQL can still encode the wrong measure, grain, population, grouping,
or ranking. This project asks:

> When analytics questions are routed through an explicit metric registry and a
> constrained SQL compiler, which intermediate failures can be localized, and
> which semantic errors remain?

The contribution is an evaluation scaffold and failure analysis. The project
does not claim that metric grounding alone solves text-to-SQL or analytical
reasoning.

## Method

The study separates five stages that are often conflated:

1. metric routing;
2. query construction;
3. static SQL policy validation;
4. execution against tested dbt marts;
5. comparison with separately stored reference results and evidence rows.

It evaluates distinct conditions:

- **Direct Codex:** question text only, without data access; outputs are
  classified as abstentions or unverified answers.
- **Codex-to-SQL:** Codex generates SQL from warehouse schema plus a
  question-specific table allow-list; this is an oracle-table-conditioned pilot,
  not a raw text-to-SQL benchmark.
- **Registry-grounded LLM SQL:** the same schema-plus-allow-list generator, but
  with the oracle metric definitions injected into the prompt. This is the
  grounding ablation that isolates the effect of an explicit metric registry on
  a learned generator; it is defined and wired into the runner and is reported
  under the pinned API rerun (see
  [`evaluation/API_RERUN_RUNBOOK.md`](evaluation/API_RERUN_RUNBOOK.md)).
- **Oracle-routed deterministic compiler:** benchmark metric labels select a
  hand-authored compiler. This is a benchmark-specific upper bound.
- **Lexical predicted routing:** a calibrated word/bigram/character n-gram
  router predicts metric sets before using the same compiler.
- **Codex predicted routing:** a subscription-Codex router predicts metric sets
  in three repeated batches before controlled compilation.

The deterministic compiler never reads `benchmark/gold_sql/` or
`benchmark/gold_answers/` at inference time. Gold rows are joined only after a
system produces its output.

## Dataset

The warehouse uses six official CMS Plan Year 2026 Marketplace public-use
files: Rate, Plan Attributes, Benefits and Cost Sharing, Service Area, Plan ID
Crosswalk, and Quality. The validated local build contains 3,887,640 raw rows,
20 dbt models, and 97 data tests.

The research benchmark contains 30 questions across premiums, issuer
competition, plan availability, benefits, continuity, plan design, and quality.
Two derived evaluation sets are retained as diagnostics:

- 60 close, model-generated paraphrases;
- 30 hash-locked, higher-lexical-shift Codex rewrites.

Neither set is described as independently human-authored. Human semantic
validation remains required before workshop submission.

## Evaluation

Primary reporting now distinguishes:

- **end-to-end strict result match:** successful execution plus identical
  column names, row cardinality, and complete row values; row order is ignored
  because SQL ties can be nondeterministic;
- **conditional strict result match:** strict match among executed runs only;
- **compatible projection match:** the earlier alias/projection-tolerant score,
  retained as a secondary diagnostic;
- **Top-k Jaccard, precision, and recall**;
- **group precision, recall, F1, and Jaccard**;
- **numeric relative error, absolute error, and SMAPE**;
- **numeric-claim evidence presence**, explicitly not a qualitative entailment
  judge;
- execution, static policy validation, abstention, citation, latency, token, and
  failure-class records.

Repeated stochastic runs are averaged within question before the bootstrap.
Confidence intervals resample question IDs, not the 90 repeated records as if
they were independent.

## Key findings

All figures below are development/pilot evidence from saved outputs rescored
with the stricter 2026-07-13 metric contract.

- On the original 30-question benchmark, Codex-to-SQL executed 90/90 queries but
  achieved **3.3% end-to-end strict match**. Its earlier
  alias/projection-compatible score was 18.9%.
- The benchmark-specific oracle compiler achieved **80.0% strict match** and
  100% compatible projection match on the original questions. This is an upper
  bound, not learned generalization.
- On the post-hoc close-paraphrase development set, strict match was 80.0% with
  oracle routing and 73.3% with lexical routing. These are development results
  because compiler repairs used observed paraphrase failures.
- On the locked model-generated challenge, strict match fell to 40.0% for oracle
  routing, 30.0% for lexical routing, and 37.8% end to end for repeated Codex
  routing. Codex-to-SQL achieved 0% strict match and 13.3% end-to-end compatible
  projection match (13.8% among the 87 executed runs).
- The challenge therefore identifies compiler generalization—not routing alone—
  as a major observed error source in this locked diagnostic.

These results support a narrow conclusion: execution success substantially
overstates semantic correctness. Explicit metric/evidence stages expose
intermediate artifacts for post-hoc failure localization; they do not establish
universal superiority or improved human error detection.

## Limitations

- The compiler and benchmark were co-developed; oracle results are
  benchmark-specific.
- The existing evaluation questions were generated or transformed from 30
  source questions and lack independent domain-expert validation.
- Subscription Codex does not expose a stable underlying model snapshot, uses
  system instructions, and reports batch-level latency/usage.
- Codex-to-SQL receives question-specific permitted tables in the pilot.
- The human-review packet is prepared, but two independent reviews have not been
  completed. No qualitative faithfulness claim is made.
- The study covers one public insurance domain and one warehouse schema.
- The project is not medical advice or clinical decision support.

## Reproduction commands

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python scripts/download_cms_pufs.py --force
python scripts/validate_raw_files.py
python scripts/load_to_duckdb.py
(cd dbt_project && dbt build --profiles-dir .)

python research/metric_grounded_llm_agents/benchmark/generate_gold_answers.py
python research/metric_grounded_llm_agents/evaluation/run_eval.py \
  --repeats 3 --experiment-id local_three_system_r3
```

The subscription-backed Codex pilot requires a logged-in Codex CLI:

```bash
PYTHONPATH=research/metric_grounded_llm_agents python \
  research/metric_grounded_llm_agents/evaluation/run_codex_pilot.py \
  --repeats 3 \
  --experiment-id codex_subscription_batched_r3 \
  --output-dir research/metric_grounded_llm_agents/evaluation/results/codex_subscription_batched_r3
```

Router, bootstrap, review, and verification commands are listed with exact
arguments in [`../../docs/REPRODUCIBILITY_CHECKLIST.md`](../../docs/REPRODUCIBILITY_CHECKLIST.md).

## Artifact structure

```text
research/metric_grounded_llm_agents/
├── agent/                    # Distinct runtime systems, registry, router, validator
├── benchmark/
│   ├── questions.yaml       # 30 source questions and oracle metric annotations
│   ├── gold_sql/            # Reference queries; evaluation only
│   ├── gold_answers/        # Locally generated rows; ignored by git
│   ├── paraphrases.json     # Model-generated close robustness set
│   └── routing_challenge_v1.json
├── configs/                 # Metric, model, data-source, and output-schema configs
├── evaluation/              # Runners, strict metrics, bootstrap, review tooling
├── artifacts/               # Compact versioned summaries and provenance manifests
├── paper/                   # Workshop-style manuscript and protocol
└── tests/                   # Leakage, metrics, routing, statistics, and validator tests
```

Large CMS files, DuckDB databases, gold rows, and full per-run outputs remain
local. Compact publication-facing summaries and their hashes are versioned under
`artifacts/` so a reviewer can trace each reported number.

## Claim boundary

See [`../../docs/CLAIM_BOUNDARY.md`](../../docs/CLAIM_BOUNDARY.md) before using
this project in an application, website, CV, or manuscript.
