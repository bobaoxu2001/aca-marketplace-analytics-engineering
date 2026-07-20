# Router Error and Stability Analysis

This report is generated from saved predictions; it makes no additional model calls.

## Repeated Codex routing

| Repeat | Exact metric-set accuracy | Abstentions |
| ---: | ---: | ---: |
| 0 | 0.867 | 6 |
| 1 | 0.833 | 8 |
| 2 | 0.800 | 10 |

Stable predictions: 54/60 examples.
Examples with at least one Codex error: 12.
Examples wrong in all Codex repeats: 6.
Lexical-router errors: 8; shared with any Codex error: 4.

## Error IDs

- Codex unstable: Q010_P1, Q010_P2, Q027_P1, Q027_P2, Q029_P1, Q029_P2
- Codex always wrong: Q009_P1, Q009_P2, Q025_P1, Q025_P2, Q030_P1, Q030_P2
- Lexical wrong: Q003_P2, Q009_P1, Q009_P2, Q019_P2, Q021_P1, Q026_P1, Q027_P1, Q027_P2

## End-to-end failure taxonomy

- RouterAbstention: 24

## Interpretation

The Codex router is a stochastic baseline, not an automatic improvement over the calibrated lexical router. Empty metric sets are treated as explicit router abstentions. Exact routing and execution-result correctness are reported separately because an incomplete metric set can occasionally produce the same displayed rows.

## Machine-readable appendix

```json
{
  "lexical_wrong_examples": [
    "Q003_P2",
    "Q009_P1",
    "Q009_P2",
    "Q019_P2",
    "Q021_P1",
    "Q026_P1",
    "Q027_P1",
    "Q027_P2"
  ],
  "codex_wrong_in_any_repeat": [
    "Q009_P1",
    "Q009_P2",
    "Q010_P1",
    "Q010_P2",
    "Q025_P1",
    "Q025_P2",
    "Q027_P1",
    "Q027_P2",
    "Q029_P1",
    "Q029_P2",
    "Q030_P1",
    "Q030_P2"
  ],
  "shared_wrong_examples": [
    "Q009_P1",
    "Q009_P2",
    "Q027_P1",
    "Q027_P2"
  ],
  "codex_unstable_examples": [
    "Q010_P1",
    "Q010_P2",
    "Q027_P1",
    "Q027_P2",
    "Q029_P1",
    "Q029_P2"
  ],
  "codex_always_wrong_examples": [
    "Q009_P1",
    "Q009_P2",
    "Q025_P1",
    "Q025_P2",
    "Q030_P1",
    "Q030_P2"
  ],
  "codex_repeat_stats": [
    {
      "repeat": 0,
      "exact": 0.8666666666666667,
      "abstentions": 6
    },
    {
      "repeat": 1,
      "exact": 0.8333333333333334,
      "abstentions": 8
    },
    {
      "repeat": 2,
      "exact": 0.8,
      "abstentions": 10
    }
  ],
  "codex_end_to_end_failure_types": {
    "RouterAbstention": 24
  }
}
```
