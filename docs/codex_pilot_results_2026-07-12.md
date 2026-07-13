# Batched Subscription-Codex Pilot — 2026-07-12

## Status and metric correction

This is a six-call, subscription-backed Codex pilot: 30 questions, two Codex
conditions, and three repeats (180 question-level records). It is not an API
model benchmark because system instructions are present and latency, pricing,
and tokens are available only at batch level.

Results below were rescored on 2026-07-13 without new model calls. The original
report called an alias/projection-compatible comparison “exact” or “strict.”
That label was incorrect. Strict match now requires identical columns, row
count, and complete cell values; row order is reported separately.

## Corrected results

| Condition | Runs | Execution | End-to-end strict | Compatible projection | Top-k Jaccard | Group F1 | SMAPE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct Codex | 90 | response 1.000 | N/A | N/A | N/A | N/A | N/A |
| Codex-to-SQL | 90 | 1.000 | 0.033 | 0.189 | 0.658 | 0.613 | 0.364 |
| Benchmark-specific oracle compiler | 90 | 1.000 | 0.800 | 1.000 | 1.000 | 1.000 | 0.000 |

All Codex-to-SQL queries executed, but only 3.3% met the strict complete-result
contract. The 18.9% value is retained only as a compatible-projection diagnostic.
The oracle compiler's 80.0% strict result is an upper bound on these benchmark
questions, not evidence of learned routing or generalization.

Question-clustered bootstrap intervals (10,000 resamples, repeats averaged
within question) give a strict-match interval of 0.000–0.100 for Codex-to-SQL
and 0.667–0.933 for the oracle compiler. The paired strict difference is 0.767
(95% interval 0.600–0.900). Deterministic oracle repeats are not treated as 90
independent observations.

Direct Codex abstained explicitly in 60/90 runs. The remaining responses are
unverified because this condition had no database access; they are not counted
as correct answers.

## Repeat stability and usage

Only one question produced identical SQL across all three repeats; 27 produced
three distinct queries. The pilot used 36,277/2,477 input/output tokens for
Direct Codex and 41,788/11,113 for Codex-to-SQL. Subscription USD cost and
per-question latency are unavailable and are not estimated.

## Claim boundary

This pilot supports an execution-versus-semantics failure analysis. It does not
support a model-general performance claim, a fully reproducible API comparison,
or a qualitative faithfulness claim. Independent review is still pending.
