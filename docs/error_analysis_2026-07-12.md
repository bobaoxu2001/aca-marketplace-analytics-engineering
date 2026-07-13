# Automated Error Analysis — 2026-07-12

> Metric note (2026-07-13): this generated report predates the strict metric
> correction. Its “Exact match” column is the legacy compatible-projection
> diagnostic. Current strict aggregate results are reported in
> `docs/codex_pilot_results_2026-07-12.md` and
> `docs/routing_challenge_results_2026-07-12.md`; this file is retained only for
> per-question development error inspection.

## Codex-to-SQL repeat behavior

| Question | Exact match rate | Mean Top-k | Mean group match | Mean SMAPE | Distinct SQL / 3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Q001 | 0.000 | 1.000 | 1.000 | 0.000 | 2 |
| Q002 | 0.000 | 1.000 | 1.000 | 0.000 | 3 |
| Q003 | 1.000 | 1.000 | 1.000 | 0.000 | 3 |
| Q004 | 0.000 | 1.000 | 1.000 | 0.000 | 1 |
| Q005 | 1.000 | 1.000 | 1.000 | 0.000 | 3 |
| Q006 | 0.000 | 0.667 | 1.000 | 0.649 | 3 |
| Q007 | 0.000 | 0.533 | 0.944 | 0.382 | 3 |
| Q008 | 0.000 | 0.100 | 0.133 | 0.000 | 3 |
| Q009 | 0.000 | 0.000 | 0.333 | 0.000 | 3 |
| Q010 | 0.000 | 0.400 | 1.000 | 0.955 | 3 |
| Q011 | 0.667 | 0.733 | 1.000 | 0.631 | 3 |
| Q012 | 0.000 | 0.467 | 1.000 | 0.798 | 3 |
| Q013 | 1.000 | 1.000 | 1.000 | 0.000 | 3 |
| Q014 | 0.000 | 1.000 | 1.000 | 0.315 | 3 |
| Q015 | 0.000 | 1.000 | 1.000 | 0.287 | 3 |
| Q016 | 0.000 | 0.333 | 0.333 | 0.000 | 3 |
| Q017 | 0.000 | 0.000 | 1.000 | 1.260 | 3 |
| Q018 | 0.000 | 0.333 | 0.333 | 0.000 | 3 |
| Q019 | 1.000 | 1.000 | 1.000 | 0.000 | 2 |
| Q020 | 0.000 | 0.967 | 1.000 | 0.000 | 3 |
| Q021 | 0.000 | 1.000 | 1.000 | 0.000 | 3 |
| Q022 | 0.000 | 1.000 | 1.000 | 1.550 | 3 |
| Q023 | 0.000 | 0.067 | 0.333 | 0.000 | 3 |
| Q024 | 0.000 | 1.000 | 1.000 | 0.885 | 3 |
| Q025 | 1.000 | 1.000 | 1.000 | 0.000 | 3 |
| Q026 | 0.000 | 0.000 | 0.000 | 0.000 | 3 |
| Q027 | 0.000 | 0.500 | 0.333 | 0.203 | 3 |
| Q028 | 0.000 | 1.000 | 1.000 | 0.448 | 3 |
| Q029 | 0.000 | 0.622 | 1.000 | 0.790 | 3 |
| Q030 | 0.000 | 0.500 | 1.000 | 0.062 | 3 |

## Held-out lexical-route failures

- Route-set mismatches: 8 / 60.
- End-to-end result mismatches after post-hoc compiler remediation: 5 / 60.
- Every remaining end-to-end mismatch is listed below; no successful cases are sampled into this section.

| Example | Expected metrics | Routed metrics | Top-k | Group match | SMAPE |
| --- | --- | --- | ---: | ---: | ---: |
| Q003_P2 | average_monthly_premium | premium_difference_by_metal | 0.0 | 0.0 | None |
| Q019_P2 | plan_count_by_county | plan_continuity_status | 0.8 | 0.566667 | 0.44671265 |
| Q021_P1 | premium_difference_by_metal | average_monthly_premium, median_silver_premium | 0.5 | 0.35 | 0.32013464 |
| Q027_P1 | quality_rating_distribution, average_deductible | average_deductible | 0.0 | 0.0 | None |
| Q027_P2 | quality_rating_distribution, average_deductible | average_deductible | 0.0 | 0.0 | None |

## Interpretation

The original Codex-to-SQL pilot demonstrates execution-success inflation: every
query executed, but strict result agreement was low. The held-out ablation
separates routing from compilation. Before post-hoc remediation, oracle routing
still failed frequently because the compiler depended on exact benchmark
wording. After remediation, oracle-route compatible-projection agreement reached
1.000; strict agreement was 0.800. Remaining lexical-route errors include both
metric-set and strict output-contract mismatches. Because remediation used
observed paraphrase failures, the result is diagnostic and must be confirmed on
a fresh human-authored test set.
