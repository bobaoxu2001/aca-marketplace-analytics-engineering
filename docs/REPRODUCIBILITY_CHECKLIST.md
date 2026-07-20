# Reproducibility Checklist

This checklist maps each reported research artifact to an exact command. Run
from the repository root unless a subshell changes directories.

## 1. Environment setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python --version
dbt --version
```

Publication runs should start from a clean tagged commit:

```bash
git status --short
git rev-parse HEAD
```

Do not treat a run from a dirty working tree as a frozen result.

## 2. Official CMS data and dbt build

```bash
python scripts/download_cms_pufs.py --debug --force
python scripts/validate_raw_files.py
python scripts/profile_raw_data.py
python scripts/load_to_duckdb.py
(cd dbt_project && dbt debug --profiles-dir .)
(cd dbt_project && dbt build --profiles-dir .)
```

Expected validated project size: 20 models, 97 data tests, one seed, and two
no-op exposures: 120 dbt build nodes total. The verified 2026-07-20 result is
`PASS=118 WARN=0 ERROR=0 SKIP=0 NO-OP=2 TOTAL=120`. Raw files and the DuckDB
database are intentionally not committed.

## 3. Gold-answer generation

```bash
python research/metric_grounded_llm_agents/benchmark/generate_gold_answers.py
```

Expected output:

```text
research/metric_grounded_llm_agents/benchmark/gold_answers/Q001.json ... Q030.json
research/metric_grounded_llm_agents/benchmark/gold_answers/manifest.json
```

Gold answers are evaluation-only. Runtime agent modules must not read this
directory.

## 4. Three-system API evaluation

Requires `OPENAI_API_KEY` for Direct LLM and API LLM-to-SQL. Without it, those
conditions are explicitly skipped; the run is not a comparative model result.

```bash
python research/metric_grounded_llm_agents/evaluation/run_eval.py \
  --repeats 3 \
  --experiment-id cms_py2026_three_system_r3 \
  --output-dir research/metric_grounded_llm_agents/evaluation/results/cms_py2026_three_system_r3
```

## 5. Subscription-Codex pilot

Requires an authenticated `codex` CLI. It is not equivalent to a raw model API
condition.

```bash
PYTHONPATH=research/metric_grounded_llm_agents python \
  research/metric_grounded_llm_agents/evaluation/run_codex_pilot.py \
  --repeats 3 \
  --conditions direct_codex_batched,codex_sql_batched \
  --experiment-id codex_subscription_batched_r3 \
  --output-dir research/metric_grounded_llm_agents/evaluation/results/codex_subscription_batched_r3
```

## 6. Router evaluation

Generate the close paraphrase diagnostic once, then freeze and hash it before
evaluation:

```bash
python research/metric_grounded_llm_agents/benchmark/generate_paraphrases_codex.py \
  --output research/metric_grounded_llm_agents/benchmark/paraphrases.json

python research/metric_grounded_llm_agents/evaluation/run_router_eval.py \
  --paraphrases research/metric_grounded_llm_agents/benchmark/paraphrases.json \
  --repeats 3 \
  --output-dir research/metric_grounded_llm_agents/evaluation/results/router_eval_r3
```

End-to-end execution using the saved Codex router predictions:

```bash
python research/metric_grounded_llm_agents/evaluation/run_end_to_end_router_eval.py \
  --paraphrases research/metric_grounded_llm_agents/benchmark/paraphrases.json \
  --codex-router-results research/metric_grounded_llm_agents/evaluation/results/router_eval_r3/results.json \
  --output-dir research/metric_grounded_llm_agents/evaluation/results/heldout_end_to_end_r3
```

High-shift challenge generation and evaluation use the analogous commands:

```bash
python research/metric_grounded_llm_agents/benchmark/generate_challenge_set_codex.py

python research/metric_grounded_llm_agents/evaluation/run_router_eval.py \
  --paraphrases research/metric_grounded_llm_agents/benchmark/routing_challenge_v1.json \
  --repeats 3 \
  --output-dir research/metric_grounded_llm_agents/evaluation/results/router_challenge_v1_r3

python research/metric_grounded_llm_agents/evaluation/run_end_to_end_router_eval.py \
  --paraphrases research/metric_grounded_llm_agents/benchmark/routing_challenge_v1.json \
  --codex-router-results research/metric_grounded_llm_agents/evaluation/results/router_challenge_v1_r3/results.json \
  --output-dir research/metric_grounded_llm_agents/evaluation/results/end_to_end_challenge_v1_r3

PYTHONPATH=research/metric_grounded_llm_agents python \
  research/metric_grounded_llm_agents/evaluation/run_codex_pilot.py \
  --question-overrides research/metric_grounded_llm_agents/benchmark/routing_challenge_v1.json \
  --conditions codex_sql_batched \
  --repeats 3 \
  --experiment-id codex_sql_challenge_v1_r3 \
  --output-dir research/metric_grounded_llm_agents/evaluation/results/codex_sql_challenge_v1_r3
```

These datasets are model-generated diagnostics, not independently human-authored
confirmatory tests.

## 7. Rescore saved model outputs

This applies the current strict result contract without making new model calls:

```bash
PYTHONPATH=research/metric_grounded_llm_agents python \
  research/metric_grounded_llm_agents/evaluation/rescore_results.py \
  research/metric_grounded_llm_agents/evaluation/results/codex_subscription_batched_r3
```

## 8. Question-clustered bootstrap

Original benchmark:

```bash
PYTHONPATH=research/metric_grounded_llm_agents python \
  research/metric_grounded_llm_agents/evaluation/bootstrap_intervals.py \
  --codex-results research/metric_grounded_llm_agents/evaluation/results/codex_subscription_batched_r3 \
  --metric-results research/metric_grounded_llm_agents/evaluation/results/cms_py2026_three_system_r3 \
  --iterations 10000 \
  --output research/metric_grounded_llm_agents/evaluation/results/bootstrap_intervals.json
```

Arbitrary saved systems/challenge comparison:

```bash
PYTHONPATH=research/metric_grounded_llm_agents python \
  research/metric_grounded_llm_agents/evaluation/bootstrap_saved_systems.py \
  --results research/metric_grounded_llm_agents/evaluation/results/end_to_end_challenge_v1_r3/results.json \
  --results research/metric_grounded_llm_agents/evaluation/results/codex_sql_challenge_v1_r3/results.json \
  --systems heldout_oracle_route,heldout_lexical_route,heldout_codex_route,codex_sql_batched \
  --reference heldout_codex_route \
  --iterations 10000 \
  --output research/metric_grounded_llm_agents/evaluation/results/challenge_bootstrap.json
```

The bootstrap first averages repeats within `question_id`, then resamples
questions. Always report the number of question clusters beside each interval.

## 9. Blind-review export and aggregation

```bash
python research/metric_grounded_llm_agents/evaluation/build_human_review_packet.py \
  --codex-results research/metric_grounded_llm_agents/evaluation/results/codex_subscription_batched_r3 \
  --metric-results research/metric_grounded_llm_agents/evaluation/results/cms_py2026_three_system_r3 \
  --gold-dir research/metric_grounded_llm_agents/benchmark/gold_answers \
  --output-dir research/metric_grounded_llm_agents/evaluation/human_review_v1
```

After two independent reviewers complete separate copies:

```bash
python research/metric_grounded_llm_agents/evaluation/aggregate_human_review.py \
  --review-a path/to/reviewer_a.csv \
  --review-b path/to/reviewer_b.csv \
  --key research/metric_grounded_llm_agents/evaluation/human_review_v1/human_review_key.json \
  --output-dir research/metric_grounded_llm_agents/evaluation/human_review_v1/summary
```

Until both files exist, qualitative faithfulness and unsupported-claim
hypotheses remain unevaluated.

## 10. CI checks

```bash
make ci-check
PYTHONPATH=research/metric_grounded_llm_agents \
  pytest research/metric_grounded_llm_agents/tests
```

For the full real-data verification:

```bash
(cd dbt_project && dbt build --profiles-dir .)
```

## 11. Artifact verification

Publication-facing compact artifacts live under:

```text
research/metric_grounded_llm_agents/artifacts/
```

Verify recorded hashes against local files before using any percentage in a
paper, CV, or website:

```bash
python research/metric_grounded_llm_agents/evaluation/verify_provenance_manifest.py \
  --manifest research/metric_grounded_llm_agents/artifacts/2026-07-13/provenance_manifest.json
```

The dated manifest is a historical snapshot. A rebuilt DuckDB file or later
source revision should produce an explicit mismatch rather than being silently
treated as the original frozen artifact.
