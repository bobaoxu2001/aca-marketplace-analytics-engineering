# Frozen Routing Challenge Results — 2026-07-12

## Design and scope

A logged-in Codex batch generated one high-lexical-shift rewrite for each of the
30 benchmark questions. The set was frozen before router evaluation with
SHA-256 `c03066e075312aa3be3b9e9b3ddab828217c8e6d8a90a14b4250931600099b1d`.
It is model-generated and not independently human-authored or validated, so it
is a locked diagnostic rather than confirmatory evidence.

## Routing

| Router | Runs | Exact metric set | Top-1 | Precision | Recall |
| --- | ---: | ---: | ---: | ---: | ---: |
| Lexical | 30 | 0.833 | 0.900 | 0.917 | 0.900 |
| Subscription Codex | 90 | 0.811 | 0.844 | 0.844 | 0.828 |

Codex returned an empty metric set in 14/90 runs. The lexical router was
deterministic and exceeded Codex on this small set.

## Corrected end-to-end results

Saved outputs were rescored on 2026-07-13 under the strict complete-result
contract. Earlier 56.7%, 46.7%, 54.4%, and 13.3% values were compatible-
projection scores, not strict scores.

| Route | Execution | End-to-end strict | End-to-end compatible projection | Top-k Jaccard | Group F1 | SMAPE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle metric route | 1.000 | 0.400 | 0.567 | 0.652 | 0.670 | 0.230 |
| Lexical predicted route | 1.000 | 0.300 | 0.467 | 0.574 | 0.607 | 0.288 |
| Codex predicted route | 0.844 | 0.378 | 0.544 | 0.685* | 0.702* | 0.219* |
| Codex-to-SQL | 0.967 | 0.000 | 0.133 | 0.667* | 0.583* | 0.545* |

`*` Conditional diagnostic among executed runs; the end-to-end strict and
projection columns count abstentions or failures as zero.

Question-clustered strict-match bootstrap intervals (10,000 resamples) are
0.233–0.567 for oracle routing, 0.133–0.467 for lexical routing, 0.211–0.556
for Codex routing, and 0.000–0.000 for Codex-to-SQL. Codex routing minus
Codex-to-SQL end-to-end strict agreement is +0.378 (0.211–0.544);
Codex-routed minus lexical-routed end-to-end strict agreement is +0.078
(−0.022–0.200), which does not establish router superiority.

The 40.0% oracle strict result exposes controlled-compiler generalization as a
major remaining error source. No compiler rule was changed after challenge
results were observed.
