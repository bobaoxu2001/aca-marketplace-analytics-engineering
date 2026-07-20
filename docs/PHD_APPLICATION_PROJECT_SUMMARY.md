# PhD Application Project Summary

## 150-word research summary

Metric-Grounded Analytics Agents studies a basic reliability gap in
natural-language analytics: a query can execute successfully while computing the
wrong measure, grain, grouping, or population. I built a reproducible DuckDB/dbt
warehouse over six official CMS Plan Year 2026 Marketplace datasets and a
30-question benchmark covering premiums, competition, benefits, continuity,
plan design, and quality. The evaluation separates direct answering,
Codex-generated SQL, oracle metric routing, predicted routing, deterministic
compilation, execution, and evidence citation. It measures strict complete-row
agreement, compatible projection, Top-k and group agreement, numeric error,
abstention, and traceability, with repeated Codex runs and question-clustered
bootstrap intervals. The experiments show that SQL execution is a weak proxy for
semantic correctness and that explicit metric/evidence stages make errors more
inspectable. They also expose the limits of the approach: the compiler is
benchmark-specific, current evaluation questions are model-generated
transformations, and qualitative human review remains pending. The project is a
manuscript-in-preparation research prototype, not medical decision support.

## 250-word research summary

Large language models can produce plausible analytics answers and executable SQL
without respecting the intended metric, grain, filters, or result structure.
Metric-Grounded Analytics Agents investigates whether separating metric
selection, constrained query construction, execution, and evidence reporting
creates a more auditable analytics workflow.

I built the study on six official CMS Plan Year 2026 ACA Marketplace public-use
files. A DuckDB/dbt pipeline models more than 3.8 million source rows into tested
premium, plan, issuer, geography, benefit, continuity, and quality marts. A
30-question benchmark links each question to reference SQL stored outside the
runtime agent path. The systems include a question-only Direct Codex condition,
an oracle-table-conditioned Codex-to-SQL pilot, a benchmark-specific
oracle-routed deterministic compiler, and lexical and Codex metric routers.

The evaluation distinguishes end-to-end strict result agreement from a more
permissive alias/projection-compatible diagnostic. It also reports execution,
static policy validation, Top-k Jaccard, group F1, numeric error, citations,
abstention, latency, token use, and failure causes. Three stochastic repeats are
averaged within question before question-clustered bootstrap resampling.

The main finding is methodological rather than a universal performance claim:
execution success substantially overstates semantic correctness. Controlled
metric compilation improves traceability and outperforms the evaluated
subscription Codex-to-SQL condition on this benchmark, but performance falls
sharply on higher-lexical-shift questions even with oracle metric routing. This
isolates semantic compilation as a major remaining research problem. The
compiler and benchmark were co-developed, test questions are model-generated,
and two-reviewer qualitative evaluation is pending; accordingly, the project is
presented as a transparent research prototype and manuscript in preparation.

## Resume bullet version

- Built a reproducible trustworthy-analytics research platform over six official
  CMS PY2026 datasets, modeling 3.8M+ rows into 20 DuckDB/dbt models validated by
  97 data tests.
- Designed a 30-question benchmark separating Direct Codex, Codex-to-SQL,
  oracle metric compilation, and predicted metric routing; logged SQL, rows,
  failures, latency, tokens, and evidence for repeated experiments.
- Implemented strict result contracts, Top-k/group/numeric diagnostics, and
  question-clustered bootstrap analysis, showing that executable SQL can remain
  semantically wrong and that compiler generalization is a central open problem.

## Statement-of-purpose paragraph

My interest in trustworthy AI grew from a practical failure mode: an analytics
agent can return syntactically valid SQL and a fluent answer while silently using
the wrong metric or grain. To study this problem, I developed Metric-Grounded
Analytics Agents, a reproducible benchmark over official CMS Marketplace data
that separates metric routing, constrained compilation, execution, and evidence
reporting. Rather than optimizing for an impressive single accuracy number, I
designed the project to retain failed runs, compare strict rows rather than SQL
strings, cluster uncertainty by question, and distinguish oracle, predicted,
post-hoc, and model-generated conditions. The resulting negative findings—most
notably the gap between execution and semantic correctness and the compiler's
degradation under lexical shift—motivated the research direction I hope to
pursue in doctoral study: evaluation and learning methods that make data agents
robust across schemas, metrics, and human decision contexts.

## Advisor email paragraph

I am developing an independent research project on trustworthy analytics agents
using official CMS Marketplace data. The project compares direct model answers,
generated SQL, and oracle/predicted metric routing while recording executable
evidence and strict result-level correctness. Its most useful result is a failure
analysis: SQL execution greatly overstates semantic correctness, and even
correct metric routing does not guarantee compiler generalization. I am
presenting it as a manuscript-in-preparation prototype, with model-generated test
sets and pending human review explicitly disclosed. This work is closely aligned
with research on reliable agents, semantic parsing, and evaluation under domain
constraints, and I would value the opportunity to discuss how it could develop
into a more rigorous cross-schema or human-centered doctoral study.

## Website project description

**Metric-Grounded Analytics Agents** is an evidence-first evaluation of
natural-language analytics over official U.S. ACA Marketplace data. The project
combines a reproducible DuckDB/dbt warehouse, a 30-question benchmark, direct and
SQL-generating Codex pilots, oracle and predicted metric routing, strict
result-level scoring, and question-clustered uncertainty analysis. It asks when
explicit metric definitions and executed evidence make analytics-agent errors
easier to detect. The current results demonstrate a large gap between SQL
execution and semantic correctness while identifying compiler generalization as
an open problem. Manuscript in preparation; confirmatory human-authored testing
and qualitative review remain pending.

## Honest limitations paragraph

This is a benchmark-specific research prototype. The deterministic compiler and
30-question benchmark were co-developed, so oracle results are upper bounds
rather than independent evidence of generalization. Current paraphrase and
challenge sets were generated from the source questions by Codex and have not
been independently validated by domain experts. Subscription Codex does not
expose a stable model snapshot, and its SQL condition receives permitted-table
hints. Automated faithfulness covers numeric evidence presence only; two-person
qualitative review is not complete. The data describe public plan offerings and
rates, not enrollment, claims, clinical outcomes, or causal effects.
