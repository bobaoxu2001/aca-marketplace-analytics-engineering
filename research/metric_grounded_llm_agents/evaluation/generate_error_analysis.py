#!/usr/bin/env python3
"""Generate a concise, reproducible error-analysis report."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-results", type=Path, required=True)
    parser.add_argument("--heldout-results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    codex_rows = json.loads((args.codex_results / "results.json").read_text())
    heldout_rows = json.loads((args.heldout_results / "results.json").read_text())
    sql_rows = [row for row in codex_rows if row["system"] == "codex_sql_batched"]
    by_question: dict[str, list[dict]] = defaultdict(list)
    for row in sql_rows:
        by_question[row["question_id"]].append(row)

    lines = [
        "# Automated Error Analysis — 2026-07-12", "",
        "## Codex-to-SQL repeat behavior", "",
        "| Question | Exact match rate | Mean Top-k | Mean group match | Mean SMAPE | Distinct SQL / 3 |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for question_id in sorted(by_question):
        rows = by_question[question_id]
        lines.append(
            f"| {question_id} | {sum(row['result_metrics']['execution_result_match'] for row in rows) / len(rows):.3f} | "
            f"{sum(row['result_metrics']['top_k_overlap'] for row in rows) / len(rows):.3f} | "
            f"{sum(row['result_metrics']['group_match_rate'] for row in rows) / len(rows):.3f} | "
            f"{sum((row['result_metrics'].get('numeric_smape') or 0) for row in rows) / len(rows):.3f} | "
            f"{len({row.get('sql') for row in rows})} |"
        )

    lexical = [row for row in heldout_rows if row["system"] == "heldout_lexical_route"]
    route_failures = [row for row in lexical if not row["route_exact_match"]]
    result_failures = [row for row in lexical if not row["result_metrics"]["execution_result_match"]]
    lines.extend([
        "", "## Held-out lexical-route failures", "",
        f"- Route-set mismatches: {len(route_failures)} / {len(lexical)}.",
        f"- End-to-end result mismatches after post-hoc compiler remediation: {len(result_failures)} / {len(lexical)}.",
        "- Every remaining end-to-end mismatch is listed below; no successful cases are sampled into this section.",
        "", "| Example | Expected metrics | Routed metrics | Top-k | Group match | SMAPE |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ])
    for row in result_failures:
        metric = row["result_metrics"]
        lines.append(
            f"| {row['example_id']} | {', '.join(row['expected_metrics'])} | {', '.join(row['routed_metrics'])} | "
            f"{metric.get('top_k_overlap')} | {metric.get('group_match_rate')} | {metric.get('numeric_smape')} |"
        )
    lines.extend([
        "", "## Interpretation", "",
        "The original Codex-to-SQL pilot demonstrates execution-success inflation: every query executed, but strict result agreement was low. "
        "The held-out ablation separates routing from compilation. Before post-hoc remediation, oracle routing still failed frequently because "
        "the compiler depended on exact benchmark wording. After remediation, oracle-route agreement reached 1.000; the remaining lexical-route "
        "errors are attributable to metric-set routing. Because remediation used observed paraphrase failures, the improved result is diagnostic and "
        "must be confirmed on a fresh human-authored test set.",
    ])
    args.output.write_text("\n".join(lines) + "\n")
    print(f"Wrote error analysis to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
