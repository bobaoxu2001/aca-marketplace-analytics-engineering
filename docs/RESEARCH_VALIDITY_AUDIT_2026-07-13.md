# Internal Research-Validity Audit — 2026-07-13

## Executive verdict

**PASS WITH FIXES** as a PhD-application research sample.

### Consolidated-repository verification — 2026-07-20

The verdict remains **PASS WITH FIXES** after consolidating the engineering and
research histories. This update is an internal, Codex-assisted validity check;
it is not the pending independent human review.

- The six local CMS files passed structural validation and a strict full load:
  2,235,761 Rate rows, 22,059 Plan Attributes rows, 1,457,952 Benefits rows,
  8,820 Service Area rows, 158,746 Crosswalk rows, and 4,302 Quality rows.
- A fresh dbt dependency install, non-partial parse, and real-data build found
  20 models, 97 data tests, one seed, and two exposures. The exact result was
  `PASS=118 WARN=0 ERROR=0 SKIP=0 NO-OP=2 TOTAL=120`.
- The repository's `make ci-check` target passed on its declared Python 3.12
  baseline: Ruff, compilation, five YAML files, all 42 Python tests, and a clean
  non-partial dbt parse. The split suites were 11 analytics tests and 31
  research tests.
- The runtime leakage guard checks both `gold_sql` and `gold_answers` across all
  agent modules; its four focused tests passed. Direct inspection found gold
  rows loaded only by benchmark generation and evaluation code after system
  output, not by inference paths.
- Current strict result matching requires identical column names, row count,
  and normalized cell values. Compatible projection remains a separately named
  diagnostic. Skipped/non-OK records stay in end-to-end denominators, although
  future reports should expose `blocked_validation_failed` as its own count.
- Offline router analysis plus both 10,000-iteration, question-clustered
  bootstrap commands reproduced the committed report and compact bootstrap
  artifacts byte-for-byte without model calls.
- The dated provenance manifest contains 76 file entries. Current verification
  found zero missing files and two expected historical-snapshot mismatches: the
  freshly rebuilt DuckDB file and the corrected error-analysis generator. The
  manifest does not hash the ignored full question-level outputs or generated
  gold-answer JSON, so it is not a complete publication archive.

The unresolved workshop gates are unchanged: independently authored or
validated confirmatory questions, a second gold-SQL audit, two completed human
reviews, a clean model-specific API rerun, and a newly frozen publication
manifest that binds the exact inputs and outputs.

### Resolution status — 2026-07-13

The application package now resolves the software and reporting blockers that
can be resolved without inventing new evidence:

- **B2 resolved:** the primary result metric now requires identical columns,
  row count, and complete cell values. Alias/projection compatibility, rank
  order, Top-k precision/recall/Jaccard, and group precision/recall/F1/Jaccard
  are separate diagnostics. Saved outputs were rescored without new model calls.
- **B3 resolved for application use:** oracle, predicted-routing, post-hoc, and
  locked diagnostics are separated in the paper and application materials; no
  100% value is presented as held-out or general performance.
- **B4 claim-block resolved, evidence gap retained:** model-generated questions
  are explicitly development/locked diagnostics. No confirmatory or broad-
  generalization claim is made. Independent validation remains a workshop gate.
- **B5 claim-block resolved, evidence gap retained:** the packet is described as
  system-label blinded, qualitative findings are not claimed, and two genuine
  independent reviews remain a workshop gate.
- **B1 repository fix:** source, protocols, locked data, tests, compact rescored
  artifacts, and reproduction instructions are versioned in the application
  branch. The original model calls remain legacy pre-freeze pilot calls, so the
  package does not relabel them as a clean preregistered rerun.

**Updated use decision:** safe as a conservative PhD-application research
sample and manuscript in preparation. **Still not safe to submit as a workshop
paper** until the external validation, second gold-SQL review, independent human
review, and clean model/API rerun gates are completed.

The project is credible as evidence of research engineering, careful failure
analysis, and an evolving trustworthy-analytics research agenda. I found no
runtime path that directly reads reference SQL or gold-answer rows during
inference, and the manuscript is explicit about oracle routing, post-hoc
repair, model-generated paraphrases, subscription-Codex limitations, and
pending human review.

It is **not currently safe to submit as a workshop paper**. The strict metric
and claim-labeling defects identified in the original audit were repaired, but
the remaining evidence is still benchmark-specific development evidence. The
confirmatory set, independent review, clean model-specific rerun, and complete
frozen provenance package remain unfinished.

### Use decision

| Intended use | Verdict | Boundary |
| --- | --- | --- |
| PhD application, described as an independent research prototype or manuscript in preparation | **Safe with conservative wording** | Do not describe the reported percentages as independently validated generalization or peer-reviewed findings. Commit/version the current source before sharing a repository link. |
| PhD application, described as a completed paper with a proven accuracy improvement | **Not safe** | The oracle compiler, projected result metric, and model-generated test questions do not support that claim. |
| Workshop submission in the present state | **Not safe** | Re-freeze the code/data, repair the primary metric, rerun all results, validate the test set independently, and complete human review first. |

## Original blocking issues (2026-07-13 baseline)

The sections below preserve the audit-time evidence and repair requirements for
traceability. The resolution banners and the 2026-07-20 consolidated update
above are authoritative for current status; resolved descriptions below should
not be read as claims about the current code.

### B1. The reported experiment snapshot is not reproducible from the recorded commit

**Severity:** blocking for paper submission; blocking before sharing the GitHub
repository as evidence for the current numerical results.

The working tree contains extensive modified and untracked research code,
documents, challenge data, and tests. The experiment manifests record commit
`280b2bc1f4ac284cae1499c46eae38f775ea2eac`, but that commit does not contain
most of the code that produced the reported results. Generated gold answers and
evaluation results are ignored by git (`.gitignore:20-28`), and the local
results README confirms that policy
(`research/metric_grounded_llm_agents/evaluation/results/README.md:3-11`). The
high-shift challenge file is also presently untracked. A hash in an uncommitted
file is evidence of content identity, but not evidence that the file was frozen
before model or compiler inspection.

The publication protocol requires a release tag, commit SHA, source hashes,
software versions, and frozen prompts before running
(`research/metric_grounded_llm_agents/paper/experiment_protocol.md:3-9`). Current
manifests record a database hash and question hash, but the data-validation log
records URLs and row counts without per-file hashes
(`docs/real_data_validation_results.md:17-24`). The end-to-end router manifest
does not record a git SHA, database hash, paraphrase hash, gold hash, compiler
hash, or completion timestamp
(`research/metric_grounded_llm_agents/evaluation/run_end_to_end_router_eval.py:144-160`).

**Exact fix required:**

1. Commit all source, protocol, benchmark, and locked-test files before rerunning.
2. Add a dirty-working-tree flag and hashes for the compiler, registry, prompts,
   gold SQL, gold-answer manifest, raw source files, database, questions, and
   test set to every experiment manifest.
3. Rerun from a clean tagged commit and publish immutable, machine-readable
   results in a release, archival repository, or committed compact artifact.
4. Generate manuscript tables from that archived JSON; do not rely only on
   manually transcribed Markdown percentages.

### B2. “Strict complete-result agreement” is not a strict complete-result metric

**Severity:** blocking for all quantitative paper claims; requires rescoring and
updated confidence intervals.

`compare_result_rows` maps unmatched columns by inferred type and positional
order (`evaluation/result_metrics.py:71-85`). It then compares only mapped
numeric columns and initializes equality from row-count equality
(`evaluation/result_metrics.py:128-176`). Missing gold columns and extra or
semantically different output columns therefore do not necessarily make the
result incorrect. The test suite explicitly requires a prediction that omits
the gold `premium_rows` column to count as an exact match
(`tests/test_result_metrics.py:4-19`).

This behavior is acceptable for a named **compatible projection agreement**
metric, but the paper and result documents call it “strict complete-result
agreement” (`paper/paper.md:196-200` and
`docs/codex_pilot_results_2026-07-12.md:21-25`). In the saved artifacts, 2 of 17
matching original Codex-to-SQL runs and 15 of 90 matching deterministic
metric-grounded runs omit at least one gold column. More importantly, positional
mapping can accept a wrong measure when its values happen to equal the gold
measure.

The related metrics are also lenient:

- `group_match_rate` is gold-group recall, not symmetric group-set agreement;
  extra predicted groups are not penalized (`evaluation/result_metrics.py:119-123`).
- Top-k overlap divides by the smaller returned list, allowing a one-row answer
  to receive full overlap against a ten-row gold list
  (`evaluation/result_metrics.py:123-126`).
- Numeric errors cover only successfully mapped, numeric cells; missing
  measures disappear from the error calculation
  (`evaluation/result_metrics.py:128-182`).

**Exact fix required:**

1. Define per-question required output dimensions and measures independently of
   generated SQL aliases.
2. Make primary exact agreement require the required schema, group set, row
   cardinality, ordering where ranking is requested, and numeric equality within
   a declared tolerance.
3. Replace group recall with separately named precision, recall, and F1/Jaccard.
4. Define Top-k recall with a fixed denominator based on the requested/gold k;
   report rank-sensitive NDCG or rank correlation where appropriate.
5. Treat missing required cells as errors rather than dropping them.
6. Retain the current projection score only as a secondary, clearly renamed
   diagnostic, then rerun all summaries and 10,000-sample bootstrap intervals.

### B3. The original 100% metric-grounded result is a benchmark-specific oracle/development result

**Severity:** blocking only if used as evidence of generalization or fair model
superiority; acceptable if retained strictly as an upper bound.

The runtime does not read gold files, but the deterministic compiler contains
question-specific lexical branches for the benchmark's exact analytical intents
(`agent/metric_sql.py:13-39`, `64-109`, and `118-203`). Benchmark metadata also
supplies oracle metrics and question-approved tables
(`benchmark/questions.yaml:2-16`; `agent/metric_registry.py:50-58`). A normalized
audit comparison found no byte-for-byte SQL duplicates, but 7 of 30 generated
templates had string similarity above 0.90 to their reference SQL, and the mean
similarity across all 30 was 0.706. This is structural benchmark co-development,
even though it is not runtime file leakage.

The paper generally labels this correctly as an annotated upper bound
(`paper/paper.md:44-53`, `114-121`, and `137-147`). It also labels the later 100%
paraphrase result as post-hoc development evidence
(`paper/paper.md:237-260`). Therefore, **the 100% value is neither a legitimate
unbiased held-out result nor evidence of learned routing**. It is a post-hoc
compiler-development result under oracle routing.

**Exact fix required:**

1. Never use the original or post-hoc 100% values as the main evidence of
   improvement.
2. Describe the condition as “benchmark-specific oracle-routed deterministic
   compiler upper bound.”
3. For publication, freeze the compiler before creating an independently
   authored test set, or evaluate on held-out intents/metrics for which no
   question-specific branch was written.
4. Report compiler-only oracle routing, predicted routing, and free text-to-SQL
   as separate ablations with the same locked questions and corrected metrics.

### B4. The held-out and challenge questions are not independently validated test data

**Severity:** blocking for generalization claims and confirmatory-paper language.

The 60 paraphrases are very close rewrites of the 30 training prototypes; the
project itself correctly notes that leave-one-original-question-out accuracy is
0.533 while paraphrase accuracy is 0.867
(`docs/router_eval_results_2026-07-12.md:30-33`). They measure paraphrase
robustness, not unseen-intent or cross-domain generalization.

The challenge set is more lexically diverse, but it was generated by the same
subscription-Codex interface later used as a router and Codex-to-SQL baseline
(`benchmark/generate_challenge_set_codex.py:27-59`). Its metric labels and gold
rows are inherited from each source question without independent human
verification of semantic equivalence. The manuscript discloses that the set is
model-generated (`paper/paper.md:262-285`), which is good, but “frozen” is not
independently auditable while the file and producing code are uncommitted.

**Exact fix required:**

1. Obtain a locked set written or independently validated by domain-competent
   humans who did not edit the compiler.
2. Record dual labels for intended metric set, grain, filters, output columns,
   and ranking behavior; adjudicate disagreements before evaluation.
3. Keep the existing paraphrases and Codex challenge as development diagnostics,
   not confirmatory test sets.

### B5. Human-review evidence is pending and only label-blinded in practice

**Severity:** blocking for unsupported-claim, qualitative-faithfulness, and H3
claims in a paper.

The 90-item packet exists and is structurally complete, but all rating fields are
blank: zero reviewed items were found. The protocol correctly says two reviewers
are required (`paper/experiment_protocol.md:38-48`). The packet hides the key,
but 30 entries have no SQL/evidence while 60 show SQL and result rows, so system
family is readily inferable. The instruction “Do not infer system identity”
cannot create actual condition blinding
(`evaluation/human_review_v1/README.md:3-16`; packet construction at
`evaluation/build_human_review_packet.py:46-63`).

Automated unsupported-claim status is not a substitute. Any nonempty executed
row is labeled supported without checking prose entailment
(`agent/validators.py:51-55`), while numeric faithfulness checks only whether
numbers occur somewhere in evidence rows and explicitly defers qualitative
entailment (`evaluation/result_metrics.py:186-220`).

**Exact fix required:**

1. Complete two independent reviews and report agreement, adjudication, and
   reviewer qualifications.
2. Call the present design **system-label blinded**, not fully blinded, or
   normalize answer/evidence presentation so system condition is less obvious.
3. Predefine the primary human outcome and handling of `N/A` abstention items.
4. Do not claim lower unsupported-claim rates from the automated status alone.

## Original non-blocking issues (2026-07-13 baseline)

### N1. Codex-to-SQL is not merely schema-conditioned

The API implementation receives the full schema and uses question-specific
source tables only as a validation allow-list (`agent/llm_sql.py:20-49`). The
subscription Codex pilot additionally puts `allowed_tables` and
`required_terms` into the model prompt (`evaluation/run_codex_pilot.py:111-130`).
The paper says the model receives the question and live schema and does not
receive metric annotations (`paper/paper.md:131-135`), but it omits this oracle
table/term guidance. This guidance favors Codex-to-SQL, so it does not explain
the grounded system's advantage, but the condition must be renamed and
disclosed precisely.

**Fix:** report the API and subscription baselines separately as
schema-conditioned and schema-plus-oracle-table-conditioned, respectively.

### N2. Skipped-run denominators are only partly correct

Skipped and failed runs are correctly excluded from unsupported-claim rates
(`evaluation/metrics.py:31-35`, `60-85`), and missing API key/database counts are
reported separately (`evaluation/metrics.py:88-93`). They correctly remain in
the execution-success denominator, as specified by the manuscript
(`paper/paper.md:164-170`).

However, evaluation enriches skipped runs with an empty prediction, which becomes
`execution_result_match=False` (`evaluation/run_eval.py:57-64` and
`evaluation/result_metrics.py:102-112`). That conflicts with RQ2's “when a system
executes” wording (`paper/paper.md:103-104`).

**Fix:** report both end-to-end success (all attempted runs) and conditional
semantic accuracy (executed runs with gold), with explicit numerators and
denominators. Do not silently treat unavailable model calls as wrong answers.

### N3. SQL validity is policy validation, not executable SQL validity

`validate_sql` checks statement shape, forbidden tokens, tables, and required
substrings with regular expressions (`agent/validators.py:10-48`). It does not
parse SQL or prove DuckDB binding/type correctness. The challenge document itself
records three queries that passed this check and then raised binding errors
(`docs/routing_challenge_results_2026-07-12.md:40-43`).

**Fix:** rename the metric `static_policy_validation_rate`; keep execution success
as the executable-SQL measure.

### N4. Repeated deterministic runs are transparent but unnecessary

The metric-grounded compiler is deterministic, yet the main three-system runner
duplicates it three times (`evaluation/run_eval.py:121-138`). The bootstrap
correctly averages repeats within question before sampling questions
(`evaluation/bootstrap_intervals.py:31-49`), so the confidence interval is not
inflated to 90 independent units. Still, summary tables that say 90 runs can
suggest more independent evidence than exists.

**Fix:** execute deterministic systems once, or label 90 records as 30 unique
question clusters with three identical technical replicates.

### N5. Bootstrap implementation is acceptable, with scope limitations

The primary bootstrap clusters by `question_id`, averages repeats within each
question, and samples 30 question clusters with replacement
(`evaluation/bootstrap_intervals.py:31-65`). Paired differences use shared
question IDs. This is the correct unit for the current repeated design and the
documents accurately say repeats were averaged before resampling
(`docs/codex_pilot_results_2026-07-12.md:27-32`).

The intervals are simple percentile intervals over only 30 benchmark questions;
they quantify uncertainty over this question set, not schemas, domains, model
versions, or human-authored intents. Numeric metrics can use fewer question
clusters when no comparable numeric cells exist.

**Fix:** always print the cluster count beside every interval and avoid broad
population-generalization language.

### N6. Paper and README states are internally inconsistent

The abstract and main results table say comparative results remain blank/pending
(`paper/paper.md:17-20`, `172-186`), while Sections 7.1–7.4 report several
comparative experiments. The conclusion says learned routing is a future
milestone even though lexical and Codex routing experiments are now reported
(`paper/paper.md:318-326`). The research README still says downloads returned 403
and gold answers could not be generated
(`research/metric_grounded_llm_agents/README.md:158-173`), contradicting the
validated local build and completed gold generation.

**Fix:** choose one manuscript state: either a protocol/pilot paper with clearly
identified development results, or a completed frozen experiment. Remove stale
environment statements and distinguish “publication run pending” from “pilot
completed.”

### N7. Reproduction documentation is incomplete for the reported experiments

The project documents dbt build, gold generation, and basic evaluation
(`research/metric_grounded_llm_agents/README.md:37-85`). The Makefile provides
targets for gold, the main evaluation, the Codex pilot, tests, and the full data
pipeline (`Makefile:3-42`). It does not document or expose exact commands for:

- paraphrase/challenge generation and locking;
- lexical and Codex router evaluation;
- end-to-end router evaluation;
- rescoring;
- either bootstrap program;
- blind-review packet construction and aggregation.

The manual GitHub workflow runs only the default one-repeat `run_eval.py`, and
without an API key its model baselines will be skipped
(`.github/workflows/metric_grounded_research_run.yml:67-75`). It does not
reproduce subscription-Codex, router, challenge, bootstrap, or review artifacts.
Workflow artifacts expire after 14 days (`.github/workflows/metric_grounded_research_run.yml:93-103`).

**Fix:** add a single versioned runbook that maps each manuscript table to an
exact command, inputs, expected output files, and hashes. Archive publication
artifacts permanently.

### N8. Raw-data provenance is adequate for a portfolio, incomplete for a paper

Official URLs, retrieval date, row counts, and schemas are documented
(`docs/real_data_validation_results.md:1-24`), and raw data is correctly excluded
from source control. Per-file byte sizes and hashes required by the protocol are
not present in the committed validation log.

**Fix:** publish a small raw-source manifest containing URL, retrieval timestamp,
byte size, SHA-256, extracted filename, and row/column counts for all six files.

### N9. Test coverage is useful but does not protect the primary validity risks

Fast CI exists and runs compilation, 26 tests, YAML validation, and dbt parsing
(`.github/workflows/ci.yml:1-28`). A live `make ci-check` on 2026-07-13 passed all
26 tests and dbt parsing with dbt 1.11.12 / duckdb adapter 1.10.1.

Existing tests cover runtime string separation, template compilation, a minimal
DuckDB execution, metric aggregation, basic bootstrap behavior, basic routing,
human-review agreement helpers, and SQL validation. Important gaps remain:

- the leakage test searches only for the string `gold_sql`, not `gold_answers`
  or indirect imports (`tests/test_agent_separation.py:12-15`);
- no tests reject missing required result columns, extra groups, short Top-k
  outputs, positional mapping of a wrong measure, or duplicate groups;
- no test checks skipped-run conditional-accuracy denominators;
- no test proves threshold calibration excludes evaluation paraphrases;
- no end-to-end test regenerates manuscript tables from a frozen manifest.

**Fix:** add adversarial metric tests and manifest-integrity tests before the
publication rerun.

## Audit answers by requested area

### 1. Data leakage

- **Direct runtime reading of gold SQL/answers:** no evidence found. Agent modules
  do not import benchmark paths; gold is loaded only by evaluation and joined
  after system output (`evaluation/run_eval.py:109-138`).
- **Gold used only for evaluation:** yes in the implemented execution flow.
- **Templates accidentally equivalent to gold:** not text-identical, but several
  are near-equivalent and the compiler is clearly benchmark-specific. Treat this
  as structural benchmark co-development, not file leakage.
- **Post-hoc separation:** clearly disclosed in the router report and manuscript
  (`docs/router_eval_results_2026-07-12.md:62-83`;
  `paper/paper.md:243-260`).

### 2. Baseline validity

- Direct Codex, Codex-to-SQL, and metric-grounded are distinct execution paths.
- Codex-to-SQL executes generated SQL, not gold SQL
  (`evaluation/run_codex_pilot.py:234-257`).
- Direct Codex is appropriately reported as 60 abstentions plus 30 unverified
  outputs (`docs/codex_pilot_results_2026-07-12.md:34-36`).
- The subscription SQL baseline receives oracle table/term hints and must be
  labeled accordingly.
- Skips are correct for execution/unsupported-claim reporting, but incorrectly
  become false semantic matches.

### 3. Metric-grounded claims

- The original 100% is an oracle upper bound on a benchmark-specific compiler.
- The paraphrase 100% is explicitly post-hoc development performance.
- The frozen challenge's 56.7% oracle-route result is the most informative
  compiler-generalization diagnostic, but still uses model-generated,
  unvalidated questions and the permissive result metric.
- Claims of traceability are defensible; claims of general accuracy improvement
  are not yet publication-grade.

### 4. Router validity

- Ordinary paraphrases are too close for broad generalization claims.
- Leave-one-question-out calibration uses only original questions and is
  separated in code from paraphrase evaluation
  (`evaluation/run_router_eval.py:66-78`, `89-110`).
- No test-set threshold leakage was found.
- Router label accuracy and end-to-end row accuracy are both reported.
- Same-model generation/evaluation and absent human equivalence checks limit both
  test sets.

### 5. Statistical validity

- Bootstrap unit is question, not repeated run.
- Repeats are averaged before question resampling.
- Deterministic repeats do not mathematically inflate the bootstrap, although
  run-count presentation should be clearer.
- Percentile intervals are implemented correctly for the supplied cluster
  values, but inherit all bias from the permissive primary metric and narrow
  benchmark.

### 6. Evaluation metrics

- Numeric conversion/tolerance and bounded SMAPE are implemented coherently;
  unbounded relative error becomes unstable near zero.
- Exact result, group match, and Top-k metrics are too permissive for their names.
- Numeric claim faithfulness is only number-presence support, not claim-to-result
  entailment; this is disclosed in code.
- Unsupported claims are counted only for `status=ok` records.
- Missing API key and missing database are reported separately.

### 7. Paper integrity

- The manuscript is skeptical and mostly avoids overclaiming.
- Pilot, model-identity, batching, subscription cost, oracle, and post-hoc
  limitations are disclosed.
- Subscription Codex is clearly separated from the planned raw API condition.
- The main integrity weaknesses are inconsistent manuscript state, use of
  “strict complete-result” for a projection metric, and an under-described
  oracle-table-conditioned Codex baseline.
- The narrow defensible contribution is a transparent experimental scaffold and
  failure taxonomy for evidence-first ACA analytics agents—not demonstrated
  general superiority of metric grounding.

### 8. Reproducibility

- dbt, gold generation, and basic evaluation are reproducible from documented
  commands when CMS downloads succeed.
- Router, bootstrap, challenge, and review workflows are not fully documented as
  a single frozen pipeline.
- Raw files and DuckDB are appropriately ignored; small manifests and
  publication result artifacts should be versioned or archived.
- Database/question hashes exist in some manifests, but source-file, compiler,
  prompt, gold, and clean-commit integrity are incomplete.

### 9. CI and quality

- Fast CI exists and passed locally during this audit.
- Tests cover several important components but not the primary construct-validity
  and artifact-integrity risks.
- Generated outputs are directory-separated from source, but ignored results
  currently leave reported claims without reviewable machine-readable evidence
  in source control.

## Minimum repair sequence

1. **Freeze and commit:** commit current source and locked datasets; create a
   clean tagged release and complete provenance manifest.
2. **Repair measurement:** define required output contracts and correct exact,
   Top-k, group, missing-value, and conditional-denominator metrics.
3. **Rescore before rerunning models:** quantify how existing conclusions change;
   then rerun only if stored outputs are insufficient.
4. **Independent test validation:** have human/domain reviewers validate or write
   a locked confirmatory set before any compiler change.
5. **Complete blind review:** two independent reviewers, agreement, adjudication,
   and clearly stated blinding limitations.
6. **Rerun from the clean tag:** regenerate gold, all systems, routers,
   end-to-end ablations, bootstrap, and manuscript tables.
7. **Archive artifacts:** retain machine-readable results beyond a 14-day CI
   artifact window.

## Final recommended claim language

> Developed a reproducible research prototype for evaluating evidence-first
> analytics agents over six official CMS Marketplace datasets. The project
> separates direct answering, generated SQL, oracle metric routing, predicted
> routing, execution, and result evidence; it includes repeated Codex pilots,
> question-clustered uncertainty estimates, and explicit post-hoc versus locked
> diagnostics. Current results show that executable SQL is often semantically
> wrong and that a benchmark-specific metric compiler improves traceability, but
> they do not yet establish general superiority: the oracle compiler is an upper
> bound, test questions are model-generated, qualitative review is pending, and
> publication metrics require a clean frozen rerun with stricter result contracts.

### Language to avoid

- “Metric grounding achieved 100% held-out accuracy.”
- “The grounded agent is proven to outperform LLM-to-SQL.”
- “The challenge set is independently validated.”
- “Claim faithfulness is solved automatically.”
- “Published” or “accepted.”

### Safe CV shorthand

> Built an evidence-first CMS analytics-agent benchmark and reproducible
> DuckDB/dbt evaluation pipeline; conducted oracle, lexical-routing, Codex
> routing, and Codex-to-SQL diagnostics with repeated runs and
> question-clustered bootstrap analysis. Manuscript in preparation; confirmatory
> human-authored evaluation pending.
