# PhD Application Project Summary

**Metric-Grounded LLM Agents for Reliable Domain Analytics** is a research-style
extension of an ACA Marketplace analytics engineering warehouse built on real
CMS public data. The project studies why LLM analytics agents hallucinate or
overstate conclusions when answering natural-language questions over complex
domain datasets.

The system compares direct LLM answering, LLM-generated SQL, and an
oracle-routed metric-grounded upper bound that forces answers through approved
metric definitions, dbt-modeled marts, executable SQL, validation checks, and
citation-backed result rows. The benchmark includes 30 ACA Marketplace analytics questions covering
premiums, issuer competition, service-area availability, plan continuity,
quality ratings, and benefit coverage.

This project is positioned as an applied data-systems and trustworthy-AI
research sample: it combines semantic modeling, public healthcare data,
reproducible evaluation, and unsupported-claim detection. The live LLM adapter,
deterministic metric compiler, reference queries, and failure-aware runner are
implemented. The next research step is a frozen full benchmark run against the
real CMS marts, followed by normalized result comparison and blinded human error
analysis. Comparative results must not be reported before that run completes.
