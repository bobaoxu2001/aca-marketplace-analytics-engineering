# Gold SQL Audit v1 — First-Pass Reference Verification

**Purpose.** Independent verification that each benchmark reference query (gold
SQL) executes against the built warehouse and computes what the corresponding
natural-language question asks. This is the automated first pass that precedes
human sign-off; it is the evidence for the reviewer question "are your reference
answers themselves correct?"

**Method.** All 30 gold SQL files were executed against
`data/processed/aca_marketplace_py2026.duckdb` (schema `main_marts`). For each
question we checked three things: (1) the query executes without error, (2) it
returns a non-empty result table, and (3) the projected columns, grain, filter,
and aggregation match the intent of the question and the referenced metric slug
in `configs/metrics.yaml`.

**Result summary.** 30/30 execute and return rows. No broken references, no
empty results, no schema mismatches. Column grains match the metric registry.
A small number of questions use a finer output grain than the question names
literally; these are flagged below as *documented design choices*, not errors,
so a human reviewer can confirm or tighten them.

## Execution status (all 30)

All queries returned non-empty results (row counts in parentheses): Q001 (10),
Q002 (10), Q003 (8), Q004 (10), Q005 (8), Q006 (7), Q007 (20), Q008 (20),
Q009 (25), Q010 (10), Q011 (5), Q012 (5), Q013 (5), Q014 (6), Q015 (6),
Q016 (20), Q017 (22), Q018 (20), Q019 (30), Q020 (20), Q021 (20), Q022 (20),
Q023 (20), Q024 (20), Q025 (8), Q026 (20), Q027 (3), Q028 (4), Q029 (15),
Q030 (20).

## Items flagged for human confirmation (design-choice, not defects)

These are cases where the gold SQL is defensible but makes a modeling choice a
human reviewer should explicitly ratify:

| Q | Question (verbatim) | Gold grain | Note for reviewer |
| --- | --- | --- | --- |
| Q006 | "distribution of public quality rating statuses" | groups by `quality_rating_status` **and** `overall_rating_value` | Finer than the literal "statuses". Confirm whether the intended distribution is over status only, or status × rating value. |
| Q016 | "which issuers have the highest median silver premiums" | groups by `state_code, issuer_name` | Issuer names are not unique across states, so state is added for disambiguation. Confirm this is the intended reading of "which issuers." |
| Q018 | "which issuers offer the most distinct plans" | groups by `state_code, issuer_name` | Same state-disambiguation choice as Q016. |
| Q029 | "which crosswalk reasons are most common" | groups by `representative_reason_for_crosswalk` **and** `representative_crosswalk_level` | Adds crosswalk level. Confirm whether "reasons" should collapse across level. |
| Q004 | "which states have the most issuer competition" | state-level `count(distinct issuer_key)` | Metric slug is `issuer_count_by_county` but the question asks by state, so the gold aggregates to state. Confirm state-level aggregation is intended. |

## Operationalization choices worth a sentence in the paper

Several questions contain a vague quantitative word that the gold SQL commits to
a specific statistic. These are legitimate but should be stated so they are not
mistaken for the only valid reading:

- Q010 "unusual premium variation" → sample standard deviation of premium.
- Q025 "widest interquartile premium range" → `quantile_cont(.75) - quantile_cont(.25)`.
- Q007 "largest ... plan continuity changes" → counts by state × continuity status.
- Q012 "higher quality ratings associated with higher premiums" → mean premium by
  rating value (descriptive association, no correlation test claimed).

## Caveats already carried from the metric registry

Premium metrics are **not enrollment-weighted** and are published rates, not
subsidy-adjusted consumer prices (per `average_monthly_premium` /
`median_silver_premium` caveats). Issuer/plan counts measure presence, not
enrollment share. These are inherited from `configs/metrics.yaml` and hold for
every premium/competition question above.

## Reviewer sign-off

The five flagged items and four operationalization choices are the only points
requiring a human decision. Everything else is a mechanical pass. A domain
reviewer should initial each flagged row as *accept as-is* or *tighten*, and the
outcome recorded in `evaluation/human_review_v1/`.

_Generated as the automated first pass; execution verified against the built
DuckDB warehouse._
