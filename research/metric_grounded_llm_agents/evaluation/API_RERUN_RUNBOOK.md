# API-Model Rerun Runbook

This runbook replaces the non-reproducible subscription-Codex pilot with a
pinned, multi-model API rerun and adds the metric-registry grounding ablation
(`llm_registry_sql`). It exists so the reported numbers can cite a stable model
snapshot instead of an unversioned CLI default.

## Why this matters for the manuscript

The current headline evidence comes from a subscription Codex CLI that does not
expose a stable model snapshot (see the paper's *Model identity* threat). A
pinned API run removes that threat, turns "pilot/diagnostic" language into
citable results, and—by adding `llm_registry_sql`—supplies the one condition the
design was missing: an LLM given the schema **and** the metric registry, which
isolates the causal effect of metric grounding between the schema-only
`llm_sql` baseline and the hand-authored `metric_grounded` compiler.

## Conditions after this change

| System | Grounding supplied to the model | Role |
| --- | --- | --- |
| `direct_llm` | question text only | abstention/hallucination reference |
| `llm_sql` | schema + oracle table allow-list | schema-only text-to-SQL |
| `llm_registry_sql` | schema + oracle table allow-list + **metric registry** | **grounding ablation (new)** |
| `metric_grounded` | oracle metric label → deterministic compiler | benchmark-specific upper bound |

`llm_sql` and `llm_registry_sql` are identical in model, task, schema context,
validation policy, and permitted-table gate. Their only difference is the
injected metric-definition block, so the paired strict-match difference between
them estimates how much an explicit registry changes an LLM's semantic
correctness under a fixed compiler-free generator.

## 0. Fix the local environment first

The committed `.venv` on an Apple-Silicon Mac ships an **x86_64** DuckDB wheel
that cannot load under arm64 (`incompatible architecture ... need 'arm64'`).
Rebuild a native environment before running anything DuckDB-backed:

```bash
python3 -m venv .venv            # use an arm64 python3 (arch -arm64 if needed)
source .venv/bin/activate
python -m pip install -r requirements.txt
python -c "import duckdb; print('duckdb', duckdb.__version__, 'ok')"
```

## 1. Build the warehouse and gold answers

```bash
python scripts/download_cms_pufs.py --force
python scripts/validate_raw_files.py
python scripts/load_to_duckdb.py
(cd dbt_project && dbt build --profiles-dir .)
python research/metric_grounded_llm_agents/benchmark/generate_gold_answers.py
```

## 2. Configure a pinned API model

Copy the example config and pin an explicit, dated snapshot for each model you
run. Never commit a real key; export it in the shell only.

```bash
cp research/metric_grounded_llm_agents/configs/model_config.example.yaml \
   research/metric_grounded_llm_agents/configs/model_config.yaml
# edit model_config.yaml: set model_snapshot to a dated snapshot id
export OPENAI_API_KEY=...        # rotate this key after the run
```

`configs/model_config.example.yaml` already pins `gpt-4.1-mini-2025-04-14` with a
priced snapshot. For a multi-model comparison, run the evaluation once per model
by pointing the config at each snapshot (e.g. a larger OpenAI snapshot, and any
additional providers you add to `model_client.py`).

## 3. Run the four-condition evaluation

```bash
PYTHONPATH=research/metric_grounded_llm_agents python \
  research/metric_grounded_llm_agents/evaluation/run_eval.py \
  --repeats 3 \
  --systems direct_llm,llm_sql,llm_registry_sql,metric_grounded \
  --experiment-id api_gpt41mini_r3 \
  --output-dir research/metric_grounded_llm_agents/evaluation/results/api_gpt41mini_r3
```

Then rerun on the hash-locked challenge set and the paraphrase set using the
same `--systems` list so `llm_registry_sql` is measured under lexical shift too.

## 4. Bootstrap, rescore, and record provenance

Use the existing tooling unchanged; it is condition-agnostic:

```bash
# question-clustered bootstrap over the new results
python research/metric_grounded_llm_agents/evaluation/bootstrap_saved_systems.py \
  --results-dir research/metric_grounded_llm_agents/evaluation/results/api_gpt41mini_r3
# refresh the provenance manifest so every reported number is traceable
python research/metric_grounded_llm_agents/evaluation/create_provenance_manifest.py
python research/metric_grounded_llm_agents/evaluation/verify_provenance_manifest.py
```

## 5. Report

- Add `llm_registry_sql` rows to the paper's Table 1 and Table 2.
- Report the paired `llm_registry_sql` − `llm_sql` strict-match difference with
  its question-clustered interval; this is the grounding-effect estimate.
- Report a stable `model` / `requested_model` from `model_call.metadata` so the
  *Model identity* threat can be retired for the API conditions.

## Cost note

30 questions × 3 repeats × 2 SQL-generating conditions ≈ 180 calls per model per
set, at ~1.2k output tokens each. With the priced `gpt-4.1-mini` snapshot this is
a few cents per set; larger snapshots scale accordingly. `run_eval.py` records
per-call token usage and an estimated cost from the pinned pricing table.
