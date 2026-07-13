#!/usr/bin/env python3
"""Question-clustered bootstrap for arbitrary systems stored in results JSON files."""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

from evaluation.bootstrap_intervals import METRICS, bootstrap, paired_difference, question_means


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, action="append", required=True)
    parser.add_argument("--systems", required=True, help="Comma-separated saved system names")
    parser.add_argument("--reference", required=True, help="System used as left side of paired differences")
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for path in args.results:
        rows.extend(json.loads(path.read_text()))
    systems = [value.strip() for value in args.systems.split(",") if value.strip()]
    if args.reference not in systems:
        raise ValueError("--reference must be included in --systems")
    rng = random.Random(20260712)
    per_system: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    output = {"iterations": args.iterations, "cluster_unit": "question_id", "systems": {}, "paired": {}}
    for system in systems:
        output["systems"][system] = {}
        for metric_name in METRICS:
            values = question_means(rows, system, metric_name)
            per_system[system][metric_name] = values
            output["systems"][system][metric_name] = bootstrap(values, args.iterations, rng)
    for system in systems:
        if system == args.reference:
            continue
        output["paired"][f"{args.reference}_minus_{system}"] = {
            metric_name: paired_difference(
                per_system[args.reference][metric_name], per_system[system][metric_name],
                args.iterations, rng,
            )
            for metric_name in METRICS
        }
    args.output.write_text(json.dumps(output, indent=2))
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
