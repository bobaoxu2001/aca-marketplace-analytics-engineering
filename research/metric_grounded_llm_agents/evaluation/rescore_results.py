#!/usr/bin/env python3
"""Recompute evaluation metrics from saved results without new model calls."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent.paths import RESEARCH_DIR  # noqa: E402
from evaluation.metrics import summarize  # noqa: E402
from evaluation.result_metrics import compare_result_rows, numeric_claim_faithfulness  # noqa: E402
from evaluation.run_codex_pilot import is_abstention  # noqa: E402
from evaluation.run_eval import load_gold_answers, write_report  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_dir", type=Path)
    parser.add_argument("--gold-dir", type=Path, default=RESEARCH_DIR / "benchmark" / "gold_answers")
    args = parser.parse_args()

    results_path = args.results_dir / "results.json"
    results = json.loads(results_path.read_text())
    gold = load_gold_answers(args.gold_dir)
    for result in results:
        gold_rows = (gold.get(result["question_id"]) or {}).get("rows") or []
        result["result_metrics"] = (
            compare_result_rows(result.get("rows"), gold_rows)
            if result.get("status") == "ok" and result.get("system") != "direct_codex_batched"
            else {"status": "not_evaluable", "execution_result_match": None,
                  "compatible_projection_match": None}
        )
        result["faithfulness_metrics"] = numeric_claim_faithfulness(
            result.get("answer"), result.get("rows") or []
        )
        if result.get("system") == "direct_codex_batched" and result.get("status") == "ok":
            result["support_status"] = (
                "unsupported_claim_marked" if is_abstention(result.get("answer", ""))
                else "unsupported_unverified_answer"
            )
    summary = summarize(results)
    results_path.write_text(json.dumps(results, indent=2, default=str))
    (args.results_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    write_report(args.results_dir / "evaluation_report.md", summary, results)
    with (args.results_dir / "results.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "experiment_id", "repeat_index", "system", "question_id", "status",
            "support_status", "latency_seconds", "answer",
        ], extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
