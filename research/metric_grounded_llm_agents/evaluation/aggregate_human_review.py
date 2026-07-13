#!/usr/bin/env python3
"""Validate two blinded reviews and compute agreement plus system-level scores."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

RATING_COLUMNS = [
    "metric_correctness_1_to_5", "answer_faithfulness_1_to_5",
    "caveat_quality_1_to_5", "reviewer_confidence_1_to_5",
]
CATEGORICAL_COLUMNS = ["abstention_appropriate_yes_no_na", "unsupported_claim_yes_no"]


def load_review(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"Empty review file: {path}")
    by_id = {row["review_item_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError(f"Duplicate review_item_id in {path}")
    for row in rows:
        for column in RATING_COLUMNS:
            try:
                value = int(row[column])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{path}: {row['review_item_id']} has invalid {column}") from exc
            if value not in range(1, 6):
                raise ValueError(f"{path}: {row['review_item_id']} {column} must be 1..5")
        if row["abstention_appropriate_yes_no_na"].strip().lower() not in {"yes", "no", "na"}:
            raise ValueError(f"{path}: invalid abstention label for {row['review_item_id']}")
        if row["unsupported_claim_yes_no"].strip().lower() not in {"yes", "no"}:
            raise ValueError(f"{path}: invalid unsupported-claim label for {row['review_item_id']}")
    return by_id


def weighted_kappa(a: list[int], b: list[int]) -> float | None:
    n, categories = len(a), range(1, 6)
    if not n:
        return None
    observed = sum(((x - y) / 4) ** 2 for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    expected = sum(
        (ca[x] / n) * (cb[y] / n) * (((x - y) / 4) ** 2)
        for x in categories for y in categories
    )
    return round(1 - observed / expected, 6) if expected else (1.0 if observed == 0 else None)


def categorical_kappa(a: list[str], b: list[str]) -> tuple[float, float | None]:
    n = len(a)
    agreement = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    expected = sum((ca[label] / n) * (cb[label] / n) for label in set(ca) | set(cb))
    kappa = (agreement - expected) / (1 - expected) if expected < 1 else (1.0 if agreement == 1 else None)
    return round(agreement, 6), round(kappa, 6) if kappa is not None else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-a", type=Path, required=True)
    parser.add_argument("--review-b", type=Path, required=True)
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    a, b = load_review(args.review_a), load_review(args.review_b)
    key = json.loads(args.key.read_text())
    if set(a) != set(b) or set(a) != set(key):
        raise ValueError("Review files and hidden key must contain exactly the same item IDs")
    ids = sorted(a)
    agreement = {}
    for column in RATING_COLUMNS:
        av, bv = [int(a[i][column]) for i in ids], [int(b[i][column]) for i in ids]
        agreement[column] = {
            "quadratic_weighted_kappa": weighted_kappa(av, bv),
            "exact_agreement": round(sum(x == y for x, y in zip(av, bv)) / len(ids), 6),
            "within_one_agreement": round(sum(abs(x - y) <= 1 for x, y in zip(av, bv)) / len(ids), 6),
        }
    for column in CATEGORICAL_COLUMNS:
        av = [a[i][column].strip().lower() for i in ids]
        bv = [b[i][column].strip().lower() for i in ids]
        exact, kappa = categorical_kappa(av, bv)
        agreement[column] = {"cohen_kappa": kappa, "exact_agreement": exact}

    system_values: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for item_id in ids:
        system = key[item_id]["system"]
        for column in RATING_COLUMNS:
            system_values[system][column].extend([int(a[item_id][column]), int(b[item_id][column])])
        for column in CATEGORICAL_COLUMNS:
            for review in (a, b):
                value = review[item_id][column].strip().lower()
                if value != "na":
                    system_values[system][f"{column}_yes"].append(float(value == "yes"))
    systems = {
        system: {metric: round(sum(values) / len(values), 6) for metric, values in metrics.items() if values}
        for system, metrics in system_values.items()
    }
    payload = {"items": len(ids), "reviewers": 2, "agreement": agreement, "system_scores": systems}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "human_review_summary.json").write_text(json.dumps(payload, indent=2))
    lines = ["# Human Review Summary", "", f"Items: {len(ids)}; independent reviewers: 2.", "", "## Agreement", ""]
    for metric, values in agreement.items():
        lines.append(f"- {metric}: " + ", ".join(f"{key}={value}" for key, value in values.items()))
    lines.extend(["", "## System scores", "", "```json", json.dumps(systems, indent=2), "```", ""])
    (args.output_dir / "human_review_summary.md").write_text("\n".join(lines))
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
