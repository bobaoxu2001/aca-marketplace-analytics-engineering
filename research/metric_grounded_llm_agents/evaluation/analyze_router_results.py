#!/usr/bin/env python3
"""Compare lexical and repeated Codex routing, including paired error overlap."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--router-results", type=Path, required=True)
    parser.add_argument("--end-to-end-results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    router_rows = json.loads(args.router_results.read_text())
    end_rows = json.loads(args.end_to_end_results.read_text())
    lexical = {row["example_id"]: row for row in router_rows if row["system"] == "lexical_router"}
    codex = [row for row in router_rows if row["system"] == "codex_metric_router"]
    by_example: dict[str, list[dict]] = defaultdict(list)
    for row in codex:
        by_example[row["example_id"]].append(row)

    repeat_stats = []
    for repeat in sorted({row["repeat_index"] for row in codex}):
        rows = [row for row in codex if row["repeat_index"] == repeat]
        repeat_stats.append({
            "repeat": repeat,
            "exact": sum(row["scores"]["exact_set_match"] for row in rows) / len(rows),
            "abstentions": sum(not row["predicted"] for row in rows),
        })

    unstable = []
    codex_always_wrong = []
    for example_id, rows in sorted(by_example.items()):
        predictions = {tuple(row["predicted"]) for row in rows}
        if len(predictions) > 1:
            unstable.append(example_id)
        if not any(row["scores"]["exact_set_match"] for row in rows):
            codex_always_wrong.append(example_id)

    lexical_wrong = {example_id for example_id, row in lexical.items() if not row["scores"]["exact_set_match"]}
    codex_wrong_any = {
        example_id for example_id, rows in by_example.items()
        if any(not row["scores"]["exact_set_match"] for row in rows)
    }
    codex_e2e = [row for row in end_rows if row["system"] == "heldout_codex_route"]
    failure_counts = Counter(row.get("failure_type", "none") for row in codex_e2e if row["status"] != "ok")

    payload = {
        "lexical_wrong_examples": sorted(lexical_wrong),
        "codex_wrong_in_any_repeat": sorted(codex_wrong_any),
        "shared_wrong_examples": sorted(lexical_wrong & codex_wrong_any),
        "codex_unstable_examples": unstable,
        "codex_always_wrong_examples": codex_always_wrong,
        "codex_repeat_stats": repeat_stats,
        "codex_end_to_end_failure_types": dict(failure_counts),
    }
    lines = [
        "# Router Error and Stability Analysis", "",
        "This report is generated from saved predictions; it makes no additional model calls.", "",
        "## Repeated Codex routing", "",
        "| Repeat | Exact metric-set accuracy | Abstentions |", "| ---: | ---: | ---: |",
    ]
    lines.extend(f"| {row['repeat']} | {row['exact']:.3f} | {row['abstentions']} |" for row in repeat_stats)
    lines.extend([
        "", f"Stable predictions: {len(by_example) - len(unstable)}/{len(by_example)} examples.",
        f"Examples with at least one Codex error: {len(codex_wrong_any)}.",
        f"Examples wrong in all Codex repeats: {len(codex_always_wrong)}.",
        f"Lexical-router errors: {len(lexical_wrong)}; shared with any Codex error: {len(lexical_wrong & codex_wrong_any)}.",
        "", "## Error IDs", "",
        f"- Codex unstable: {', '.join(unstable) or 'none'}",
        f"- Codex always wrong: {', '.join(codex_always_wrong) or 'none'}",
        f"- Lexical wrong: {', '.join(sorted(lexical_wrong)) or 'none'}",
        "", "## End-to-end failure taxonomy", "",
    ])
    lines.extend(f"- {name}: {count}" for name, count in sorted(failure_counts.items()))
    lines.extend([
        "", "## Interpretation", "",
        "The Codex router is a stochastic baseline, not an automatic improvement over the calibrated lexical router. "
        "Empty metric sets are treated as explicit router abstentions. Exact routing and execution-result correctness "
        "are reported separately because an incomplete metric set can occasionally produce the same displayed rows.", "",
        "## Machine-readable appendix", "", "```json", json.dumps(payload, indent=2), "```", "",
    ])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines))
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
