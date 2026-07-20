# Codex Session Credit Exhaustion — 2026-07-12

> Historical incident note. The blocked router batch described below was later
> completed in a fresh session; see
> [router evaluation results](router_eval_results_2026-07-12.md) and
> [router error analysis](router_error_analysis_2026-07-12.md). It remains
> excluded from this earlier session's denominators.

The requested no-API research session continued until the logged-in Codex CLI
returned a terminal usage-limit response:

```text
You've hit your usage limit. ... try again at 7:34 AM.
```

The limit was reached after completing:

- the six-call, 180-record Direct Codex and Codex-to-SQL pilot;
- one additional 60-paraphrase generation call;
- supporting smoke tests and structured-output validation calls.

The attempted three-repeat Codex metric-router evaluation could not begin in
this session because the first router batch was rejected before model output.
For this session record it remains marked blocked, not scored as incorrect and
not folded into performance denominators.

Local, non-model work continued to produce the lexical-router baseline and to
preserve the held-out paraphrase dataset. A later session resumed the Codex
router condition without regenerating those paraphrases.

The calibrated lexical router subsequently achieved 0.867 exact metric-set
accuracy and 0.950 Top-1 accuracy on the 60 held-out paraphrases.
