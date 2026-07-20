# PhD Research Sample — Start Here

## Metric-Grounded Analytics Agents: Measuring Semantic Reliability Beyond Executable SQL

**Applicant role:** independent researcher and project author

**Research area:** trustworthy data agents and semantic grounding under schema shift

**Status:** manuscript in preparation; benchmark-specific pilot and diagnostic evidence

## The question

Natural-language analytics agents can generate SQL that executes successfully
while silently using the wrong measure, grain, grouping, population, or output
contract. This project asks how an evaluation pipeline can make those failures
observable instead of treating execution as correctness.

## What I contributed

I built a reproducible DuckDB/dbt warehouse over six official CMS Plan Year
2026 Marketplace files containing **3,887,640 source rows**, designed a
30-question analytics benchmark, and implemented an evaluation pipeline that
separates:

**metric routing → query compilation → policy validation → execution → strict result comparison → evidence**

During the evaluation audit, I found that the original alias/projection-tolerant
score could count incomplete outputs as exact. I introduced a strict
complete-result contract—matching column names, row count, and every cell—and
rescored the saved runs. This measurement correction changed the headline result
and shifted the focus from aggregate accuracy to validity-aware failure
analysis.

## Observed diagnostic findings

- In an **oracle-table-conditioned subscription-Codex pilot**, all 90 generated
  queries executed, but only **3/90 (3.3%)** reproduced the complete reference
  result. Here, oracle-table-conditioned means the model received the
  question-specific allowed-table list but no gold SQL or gold rows. The
  underlying model snapshot was not exposed, so this is not a model-general
  result.
- A **benchmark-specific, oracle-routed hand-authored compiler** strictly matched
  **24/30** original questions. Oracle-routed means the compiler received the
  correct metric label. This is a co-developed upper bound, not learned
  generalization or a fair superiority claim.
- On a hash-locked but **model-generated lexical-shift diagnostic**, the same
  compiler matched only **12/30** questions even with oracle routing. This makes
  compilation and output-contract generalization a major observed error source
  in this diagnostic.

## What this work does not claim

The benchmark and compiler were co-developed; the derived test questions have
not been independently validated; a second reviewer has not audited every gold
query; and the prepared human-review packet has no completed ratings. The work
does not establish universal hallucination reduction, general healthcare
reasoning, production deployment, or improved human error detection.

## Proposed doctoral agenda

1. Build independently authored and reviewed cross-schema benchmarks with
   explicit output contracts.
2. Learn metric and schema grounding with calibrated abstention under schema
   and language shift.
3. Test whether evidence-first interfaces improve analysts' failure detection
   and calibrated reliance in controlled human studies.

## Reading options

**Three-minute overview**

Read this page. The [concise research brief](research_brief.md) is a
print-friendly alternative with the same core narrative.

**About eight minutes**

1. [Research overview](../../research/metric_grounded_llm_agents/README.md)
2. [Claim boundary](../CLAIM_BOUNDARY.md)

**Twenty- to thirty-minute deep dive**

Read the [manuscript](../../research/metric_grounded_llm_agents/paper/paper.md),
especially the abstract, evaluation, results, and threats to validity.

**Full audit trail**

1. [Reproducibility checklist](../REPRODUCIBILITY_CHECKLIST.md)
2. [Frozen-run protocol](../../research/metric_grounded_llm_agents/paper/experiment_protocol.md)
3. [Claim boundary](../CLAIM_BOUNDARY.md)
4. [Research validity audit](../RESEARCH_VALIDITY_AUDIT_2026-07-13.md)
5. [Versioned research artifacts](../../research/metric_grounded_llm_agents/artifacts/)

## Recommended citation status

Describe the work as an **independent research project** and **manuscript in
preparation**. Do not describe it as published, peer reviewed, externally
replicated, or independently validated.
