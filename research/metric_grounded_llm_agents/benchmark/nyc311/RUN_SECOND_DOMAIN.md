# Running the NYC 311 second-domain benchmark

The evaluation harness is domain-parameterized. The `llm_sql` and
`llm_registry_sql` conditions run on NYC 311 with no code changes — only flags.
(`metric_grounded` is the CMS-specific deterministic compiler and is not wired
for this domain; it is intentionally omitted here.)

## One-time setup

1. Build the warehouse (needs the downloaded CSVs; see `benchmark/nyc311/README.md`):

   ```bash
   python research/metric_grounded_llm_agents/benchmark/build_nyc311_warehouse.py
   ```

2. Point the model client at a provider and set the key in the shell only.
   Either DeepSeek or Qwen works (both OpenAI-compatible, reachable from China):

   ```bash
   cp research/metric_grounded_llm_agents/configs/model_config.deepseek.yaml \
      research/metric_grounded_llm_agents/configs/model_config.yaml
   export DEEPSEEK_API_KEY=sk-...        # or DASHSCOPE_API_KEY with the qwen config
   ```

## Run the two LLM conditions

From `research/metric_grounded_llm_agents/`:

```bash
python evaluation/run_eval.py \
  --database ../../data/processed/nyc311_2024.duckdb \
  --schema marts \
  --metrics configs/metrics.nyc311.yaml \
  --questions benchmark/nyc311/questions.yaml \
  --gold-dir benchmark/nyc311/gold_answers \
  --systems llm_sql,llm_registry_sql \
  --repeats 3 \
  --experiment-id nyc311_deepseek_r3 \
  --output-dir evaluation/results/nyc311_deepseek_r3
```

`--repeats 3` gives 30 questions x 2 systems x 3 = 180 calls (a few cents on
DeepSeek). Output lands in `evaluation/results/nyc311_deepseek_r3/`
(`summary.json`, `results.json`, `experiment_manifest.json`, report).

## Confidence intervals (question-clustered bootstrap)

Same procedure as the CMS rerun:

```bash
PYTHONPATH=. python evaluation/bootstrap_saved_systems.py \
  --results evaluation/results/nyc311_deepseek_r3/results.json \
  --systems llm_sql_baseline,llm_registry_sql \
  --reference llm_registry_sql \
  --iterations 10000 \
  --output evaluation/results/nyc311_deepseek_r3/bootstrap_nyc311_10000.json
```

## What to read off

The paper's claim reproduces here if, on a second independent domain, executable
SQL again overstates strict correctness and the registry block raises
executability / lowers numeric error without reaching strict correctness. Compare
`execution_success_rate`, `end_to_end_result_match_rate`, and `numeric_smape`
across `llm_sql` vs `llm_registry_sql`, with the bootstrap CIs.

The harness verifies (dry run, no key) that the schema context is read from the
`marts` schema and the grounding block renders the NYC registry — so a keyed run
differs only by the real model call.
```
