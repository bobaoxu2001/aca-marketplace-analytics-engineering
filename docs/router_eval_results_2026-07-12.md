# Held-Out Metric Router Evaluation — 2026-07-12

## Dataset

The logged-in Codex model generated two meaning-preserving paraphrases for each
of the 30 benchmark questions. The 60 paraphrases contain no answers and retain
the original metric labels. Original questions are training prototypes; all
paraphrases are held out for router evaluation.

Because the paraphrases are model-generated rather than independently authored,
this is a controlled robustness set, not a substitute for human-written or
cross-domain test data.

## Lexical router

The non-oracle router combines word, word-bigram, and character n-gram cosine
similarity over original questions plus the metric registry. Its multi-label
relative threshold is selected using leave-one-original-question-out
calibration. Held-out paraphrases are never used for threshold selection.

| Metric | Result |
| --- | ---: |
| Held-out examples | 60 |
| Exact metric-set accuracy | 0.867 |
| Top-1 accuracy | 0.950 |
| Macro precision | 0.950 |
| Macro recall | 0.908 |
| Selected relative threshold | 0.94 |

Leave-one-original-question-out exact-set accuracy was 0.533, while paraphrase
accuracy was higher. This suggests the paraphrases remain lexically close to the
original benchmark and should not be described as evidence of broad
generalization.

## Codex metric router

After the subscription credit window refreshed, the saved evaluation resumed
without regenerating the held-out dataset. Three independent batched calls
produced all 180 expected predictions (60 paraphrases × 3 repeats).

| Metric | Result |
| --- | ---: |
| Exact metric-set accuracy | 0.833 |
| Top-1 accuracy | 0.867 |
| Macro precision | 0.867 |
| Macro recall | 0.850 |
| Stable examples across all repeats | 54 / 60 |

Per-repeat exact accuracy declined from 0.867 to 0.833 and 0.800, with 6, 8,
and 10 explicit empty-route abstentions. This stochastic Codex router had lower
observed exact agreement than the deterministic lexical baseline on this
benchmark-specific close robustness set.

## Research implication

The routing experiment removes one form of oracle dependency and demonstrates
that a stronger language model is not automatically the stronger router. Both
predicted routes are carried into the same deterministic compiler and scored on
rows, not just labels.

## End-to-end execution ablation

**2026-07-13 correction:** saved outputs were rescored under the strict
complete-result contract. Values previously labeled “result match” were
compatible-projection scores.

The first paraphrase execution run confirmed that routing accuracy alone was
insufficient:

| Condition | Execution | Strict match | Compatible projection |
| --- | ---: | ---: | ---: |
| Oracle route, pre-remediation | 0.967 | not retained as a main result | 0.517 |
| Lexical route, pre-remediation | 0.967 | not retained as a main result | 0.450 |

Inspection showed that the SQL compiler depended on exact source-question
phrases, and the metric registry omitted some dimension tables permitted by its
own definitions. Post-hoc remediation produced:

| Condition | Execution | End-to-end strict | Compatible projection |
| --- | ---: | ---: | ---: |
| Oracle route, post-hoc | 1.000 | 0.800 | 1.000 |
| Lexical route, post-hoc | 1.000 | 0.733 | 0.917 |
| Codex route, post-hoc (180 runs) | 0.867 | 0.667 | 0.867 |

The post-hoc values are development diagnostics, not an unbiased held-out
estimate. Five lexical-route paraphrases still failed end to end, all because of
incorrect metric routing under the compatible-projection diagnostic; strict
schema/value mismatches remain more frequent. A fresh locked human-authored set is required before
claiming generalization.

The Codex route abstained 24/180 times. Its six non-exact, non-empty routes all
selected only issuer count for two questions that required both issuer and plan
counts; those incomplete routes happened to reproduce the displayed reference
rows under the compatible-projection metric, so that diagnostic (0.867) is
higher than exact route accuracy (0.833).
This is why both semantic-route correctness and row agreement remain necessary.
