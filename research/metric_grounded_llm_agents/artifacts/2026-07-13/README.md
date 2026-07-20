# Strict Rescore Artifact — 2026-07-13

This compact, versioned artifact contains aggregate summaries and
question-clustered bootstrap intervals produced by rescoring saved pilot outputs
under the corrected strict metric contract. No model was called during the
rescore.

The underlying subscription-Codex calls were made during development on
2026-07-12, before this application branch was frozen. Therefore these files
are transparent pilot/development evidence, not a preregistered or clean-tag
model rerun. Full question-level outputs remain local because the general
results directory is generated and ignored; they should be archived with a
future public release.

Files:

- `original_codex_pilot_summary.json`: Direct Codex and Codex-to-SQL pilot.
- `original_three_system_summary.json`: original three-system aggregates.
- `posthoc_paraphrase_summary.json`: explicitly post-hoc close-paraphrase run.
- `challenge_codex_sql_summary.json`: locked challenge Codex-to-SQL run.
- `challenge_routing_summary.json`: locked challenge oracle/lexical/Codex routes.
- `original_bootstrap_strict.json`: original-question strict intervals.
- `challenge_bootstrap_strict.json`: challenge strict intervals.
- `provenance_manifest.json`: hashes and local runtime/version information,
  generated after the source commit.

The manuscript tables are transcribed from these JSON summaries. Use
`evaluation/rescore_results.py` and `evaluation/bootstrap_saved_systems.py` to
regenerate them from archived question-level outputs.
