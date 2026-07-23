# Gold SQL Human Sign-off Checklist (CMS domain)

**Status: signed off.** The automated audit (`gold_sql_audit_v1.md`) confirmed all
30 CMS gold SQL execute and return non-empty results. Five questions made a grain
choice and four committed a vague word to a specific statistic. Decisions below
were applied: Q006 and Q029 were tightened to match the question wording (gold SQL
and gold answers regenerated; audit re-run, all 30 pass); the rest were kept as
documented modeling choices.

## A. Grain decisions (choose Keep or Tighten)

Row counts are the actual current-vs-tightened output sizes against the built
warehouse.

### [x] Q006 — "What is the distribution of public quality rating statuses?"
- Current: groups by `quality_rating_status` **and** `overall_rating_value` → 7 rows
- Tighten: group by `quality_rating_status` only → 3 rows
- **Recommendation: Tighten.** The word is "statuses"; status-only is the literal
  reading. The star value is a different axis.
- Decision: ☐ Keep  ☒ **Tighten (applied — now 3 rows; gold answer regenerated)**

### [x] Q016 — "Which issuers have the highest median silver premiums?"
- Current: groups by `state_code, issuer_name` (Silver, ≥20 rows) → 177 groups
- Tighten: group by `issuer_name` only → 112 groups
- **Recommendation: Keep.** Issuer names recur across states as distinct legal
  entities; collapsing them would merge unrelated issuers. Document as intended.
- Decision: ☒ **Keep (state×issuer retained as intended)**  ☐ Tighten

### [x] Q018 — "Which issuers offer the most distinct plans?"
- Current: groups by `state_code, issuer_name` → 345 groups
- Tighten: group by `issuer_name` only → 161 groups
- **Recommendation: Keep** (same reasoning as Q016).
- Decision: ☒ **Keep (state×issuer retained as intended)**  ☐ Tighten

### [x] Q029 — "Which crosswalk reasons are most common?"
- Current: groups by `representative_reason_for_crosswalk` **and**
  `representative_crosswalk_level` → 15 rows
- Tighten: group by reason only → 9 rows
- **Recommendation: Tighten.** The word is "reasons"; level is a second axis.
- Decision: ☐ Keep  ☒ **Tighten (applied — now 9 rows; gold answer regenerated)**

### [x] Q004 — "Which states have the most issuer competition?"
- Current: state-level `count(distinct issuer_key)`; the metric slug is
  `issuer_count_by_county` but the question asks by state.
- Alternative: compute per-county issuer counts first, then aggregate to state
  (e.g. average or median county competition) — can reorder the states.
- **Recommendation: Keep**, but add a one-line note that this is statewide issuer
  presence, not per-county competition.
- Decision: ☒ **Keep (statewide issuer presence, documented)**  ☐ Tighten

## B. Operationalization notes (no code change; just confirm the wording)

These are defensible; the paper should state the chosen statistic so it is not
read as the only valid one.

- [x] Q010 "unusual premium variation" → sample standard deviation. ☒ Confirmed
- [x] Q025 "widest interquartile premium range" → `quantile_cont(.75) − quantile_cont(.25)`. ☒ Confirmed
- [x] Q007 "largest continuity changes" → counts by state × continuity status. ☒ Confirmed
- [x] Q012 "higher ratings associated with higher premiums" → mean premium by
  rating value (descriptive, no correlation test claimed). ☒ Confirmed

## Outcome

If any row is set to Tighten, edit the corresponding `benchmark/gold_sql/Q0XX.sql`,
regenerate its gold answer, and re-run the audit. If all are Keep/Confirm, record
this file as the sign-off and cite it from the manuscript's human-review note.
