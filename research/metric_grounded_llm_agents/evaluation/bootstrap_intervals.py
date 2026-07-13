#!/usr/bin/env python3
"""Compute question-clustered bootstrap intervals for experiment metrics."""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean


METRICS = {
    "end_to_end_result_match": lambda row: float(bool(row.get("status") == "ok" and row["result_metrics"].get("execution_result_match"))),
    "execution_result_match": lambda row: row["result_metrics"].get("execution_result_match"),
    "top_k_overlap": lambda row: row["result_metrics"].get("top_k_overlap"),
    "group_match_rate": lambda row: row["result_metrics"].get("group_match_rate"),
    "numeric_smape": lambda row: row["result_metrics"].get("numeric_smape"),
}


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def question_means(rows: list[dict], system: str, metric_name: str) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    getter = METRICS[metric_name]
    for row in rows:
        if row["system"] != system:
            continue
        value = getter(row)
        if value is not None:
            grouped[row["question_id"]].append(float(value))
    return {question_id: mean(values) for question_id, values in grouped.items()}


def bootstrap(values: dict[str, float], iterations: int, rng: random.Random) -> dict[str, float | int]:
    keys = sorted(values)
    observed = mean(values.values())
    samples = [
        mean(values[rng.choice(keys)] for _ in keys)
        for _ in range(iterations)
    ]
    return {
        "question_clusters": len(keys),
        "estimate": round(observed, 6),
        "ci95_low": round(percentile(samples, 0.025), 6),
        "ci95_high": round(percentile(samples, 0.975), 6),
    }


def paired_difference(
    left: dict[str, float], right: dict[str, float], iterations: int, rng: random.Random
) -> dict[str, float | int]:
    keys = sorted(set(left) & set(right))
    differences = {key: left[key] - right[key] for key in keys}
    result = bootstrap(differences, iterations, rng)
    result["comparison"] = "left_minus_right"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-results", type=Path, required=True)
    parser.add_argument("--metric-results", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    codex_rows = json.loads((args.codex_results / "results.json").read_text())
    metric_rows = json.loads((args.metric_results / "results.json").read_text())
    rows = codex_rows + metric_rows
    systems = ["codex_sql_batched", "metric_grounded"]
    rng = random.Random(20260712)
    output = {"iterations": args.iterations, "cluster_unit": "question_id", "systems": {}, "paired": {}}
    per_system: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    for system in systems:
        output["systems"][system] = {}
        for metric_name in METRICS:
            values = question_means(rows, system, metric_name)
            per_system[system][metric_name] = values
            output["systems"][system][metric_name] = bootstrap(values, args.iterations, rng)
    for metric_name in METRICS:
        output["paired"][metric_name] = paired_difference(
            per_system["metric_grounded"][metric_name],
            per_system["codex_sql_batched"][metric_name],
            args.iterations,
            rng,
        )
    args.output.write_text(json.dumps(output, indent=2))
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
