# Experiment Status — 2026-07-12

> Historical status snapshot. Saved outputs were rescored on 2026-07-13. The
> table below used the legacy compatible-projection metric; the current strict
> oracle result is 0.800 and compatible projection is 1.000. See
> `docs/codex_pilot_results_2026-07-12.md` for corrected reporting.

## Completed

The PY2026 CMS marts and all 30 gold answers were generated from the validated
local DuckDB database. The three-condition runner was executed with three
repeats per question (`cms_py2026_three_system_r3_final`).

The oracle-routed metric-grounded condition completed all 90 runs:

| Metric | Result |
| --- | ---: |
| Execution success | 1.000 |
| SQL validity | 1.000 |
| Compatible-projection match (legacy label corrected) | 1.000 |
| Top-k overlap | 1.000 |
| Group match rate | 1.000 |
| Mean numeric relative error | 0.000 |
| Numeric-claim faithfulness | 1.000 |
| Citation coverage | 1.000 |
| Traceability | 1.000 |

These values characterize the annotated, deterministic oracle-routing upper
bound. They must not be presented as evidence that a learned router generalizes
to unseen questions.

## Blocked conditions

The Direct LLM and LLM-to-SQL conditions each recorded 90
`skipped_missing_api_key` runs because `OPENAI_API_KEY` was unavailable. These
are blocked-run diagnostics, not zero model-performance scores.

Once a credential is available in the local environment, rerun:

```bash
source .venv/bin/activate
make research-eval-r3
```

The runner records exact prompts and instructions, model snapshot, response ID,
request parameters, token usage, estimated cost using the dated configuration
snapshot, latency, SQL, rows, exception class, repeat index, per-question result
metrics, and aggregate reports. Do not place the credential in the repository or
in committed configuration.

## Automated metric boundary

Numeric-claim faithfulness verifies explicit numbers against executed evidence
rows. Qualitative entailment remains marked for blinded human review and is not
silently treated as solved by this automated score.

## No-API Codex pilot

A separate batched Codex subscription pilot was subsequently completed without
an API key. See `docs/codex_pilot_results_2026-07-12.md`. This pilot contains 180
question-level records across Direct Codex and Codex-to-SQL, but remains
methodologically distinct from the pending raw API comparison.
