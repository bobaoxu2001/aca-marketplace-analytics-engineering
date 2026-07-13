# Advisor Targeting Notes

Use these frames to connect the same project to a faculty member's research
agenda without changing the evidence or inflating the claims.

## Trustworthy AI agents

**Research fit:** verifiable agent actions, calibrated abstention, tool-use
evaluation, provenance, and failure-aware reporting.

**Lead with:** the separation between metric selection, SQL generation,
execution, evidence, and final claims; the explicit retention of failed and
blocked runs; the gap between tool success and semantic success.

**Possible doctoral extension:** learned abstention policies, claim-to-cell
entailment, uncertainty calibration, adversarial metric ambiguity, and transfer
across regulated domains.

**Do not lead with:** the 80% oracle benchmark result. It is a
benchmark-specific upper bound, not agent generalization.

## Text-to-SQL and semantic parsing

**Research fit:** meaning representation, schema linking, execution-based
evaluation, compositional generalization, and semantic equivalence.

**Lead with:** result-level evaluation instead of SQL-string match; the
distinction between metric routing and compiler generalization; observed
degradation on lexically shifted questions.

**Possible doctoral extension:** schema/metric split evaluation, learned metric
representations, test-suite semantics, constrained decoding, and unseen-intent
generalization.

**Important disclosure:** the subscription Codex-to-SQL pilot receives
question-specific allowed tables and is therefore oracle-table-conditioned.

## Data systems

**Research fit:** semantic layers, trustworthy query interfaces, provenance,
typed contracts, query validation, and reproducible analytical systems.

**Lead with:** the DuckDB/dbt substrate, explicit metric registry, permitted
tables, immutable run records, strict output contracts, and separation of
static policy validation from actual execution.

**Possible doctoral extension:** database-native provenance for LLM agents,
semantic contract enforcement, query-plan-aware validation, and cross-warehouse
portability.

**Avoid:** describing a hand-authored compiler as a learned database interface.

## Health informatics

**Research fit:** reliable analysis of heterogeneous public health/insurance
data, responsible interpretation, data provenance, and domain metric ambiguity.

**Lead with:** six official CMS files at different grains; careful boundaries
around premiums, quality, plans, and issuer competition; no patient-level data;
no causal or clinical claims.

**Possible doctoral extension:** expert-authored benchmark questions, policy
metric validation, cross-year dataset shift, and analyst-in-the-loop evaluation.

**Avoid:** medical decision-support language. The project is insurance-market
analytics, not clinical informatics.

## Human-centered AI

**Research fit:** how analysts assess, contest, and calibrate trust in AI
outputs; explainability through executable evidence; human review of caveats and
abstention.

**Lead with:** the evidence chain and planned system-label-blinded review; the
question of whether answer-first versus evidence-first interfaces change error
detection.

**Possible doctoral extension:** controlled analyst studies, explanation
interfaces, cognitive load, calibrated reliance, disagreement workflows, and
expert/non-expert comparison.

**Current boundary:** the review packet exists, but no human-review result is yet
claimed.

## Analytics engineering

**Research fit:** semantic modeling, metric governance, tested transformations,
data quality, and operational reproducibility.

**Lead with:** converting six raw CMS PUFs into tested marts and then using the
semantic layer as an experimental intervention rather than only as BI plumbing.

**Possible doctoral extension:** empirical study of metric layers as control
mechanisms for AI analytics, automated contract induction, and governance-aware
agent evaluation.

**Avoid:** positioning portability to cloud warehouses as a scientific result;
it is engineering readiness, not research evidence.

## Advisor outreach checklist

- Cite one specific paper or project from the faculty member.
- Connect to one research mechanism, not a broad field label.
- State one negative finding from this project.
- Propose one extension requiring that advisor's expertise.
- Use “manuscript in preparation” and link the claim-boundary document.
- Do not attach a long paper in the first email unless requested; link the
  research README and a one-page summary.
