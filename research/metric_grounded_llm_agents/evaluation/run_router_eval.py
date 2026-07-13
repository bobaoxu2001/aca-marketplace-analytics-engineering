#!/usr/bin/env python3
"""Evaluate lexical and Codex metric routing on held-out paraphrases."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent.metric_registry import MetricRegistry  # noqa: E402
from agent.metric_router import LexicalMetricRouter  # noqa: E402
from agent.paths import DEFAULT_QUESTIONS, RESEARCH_DIR  # noqa: E402
from evaluation.run_codex_pilot import run_codex_batch  # noqa: E402


def score(predicted: list[str], expected: list[str]) -> dict[str, float | bool]:
    predicted_set, expected_set = set(predicted), set(expected)
    intersection = predicted_set & expected_set
    return {
        "exact_set_match": predicted_set == expected_set,
        "precision": len(intersection) / len(predicted_set) if predicted_set else 0.0,
        "recall": len(intersection) / len(expected_set) if expected_set else 1.0,
        "top1_correct": bool(predicted and predicted[0] in expected_set),
    }


def aggregate(rows: list[dict]) -> dict:
    return {
        "examples": len(rows),
        "exact_set_accuracy": round(sum(row["scores"]["exact_set_match"] for row in rows) / len(rows), 6),
        "top1_accuracy": round(sum(row["scores"]["top1_correct"] for row in rows) / len(rows), 6),
        "macro_precision": round(sum(row["scores"]["precision"] for row in rows) / len(rows), 6),
        "macro_recall": round(sum(row["scores"]["recall"] for row in rows) / len(rows), 6),
    }


def codex_prompt(examples: list[dict], registry: MetricRegistry) -> str:
    lines = [
        "Route each held-out analytics question to the smallest correct set of metric slugs.",
        "Do not use tools, files, databases, code execution, or internet access.",
        "Return every example exactly once using the required JSON schema.",
        "For each output string, encode a JSON array containing only valid metric slugs.",
        "Use multiple slugs only when the question truly requires multiple metrics.",
        "",
        "METRICS:",
    ]
    for slug in registry.slugs():
        metric = registry.get(slug)
        lines.append(
            f"{slug}: {metric.name}; expression={metric.expression}; "
            f"dimensions={','.join(metric.allowed_dimensions)}; caveats={','.join(metric.caveats)}"
        )
    lines.append("\nHELD-OUT QUESTIONS:")
    lines.extend(f"{example['example_id']}: {example['question']}" for example in examples)
    return "\n".join(lines)


def calibrate_threshold(questions: list[dict], registry: MetricRegistry) -> tuple[float, dict[str, float]]:
    candidates = [round(value / 100, 2) for value in range(50, 96, 2)]
    scores: dict[str, float] = {}
    for threshold in candidates:
        correct = 0
        for index, question in enumerate(questions):
            training = questions[:index] + questions[index + 1:]
            router = LexicalMetricRouter.from_questions(training, registry)
            predicted = router.predict(question["question"], relative_threshold=threshold)
            correct += set(predicted) == set(question.get("metrics", []))
        scores[f"{threshold:.2f}"] = correct / len(questions)
    best = max(candidates, key=lambda value: (scores[f"{value:.2f}"], value))
    return best, scores


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--paraphrases", type=Path, default=RESEARCH_DIR / "benchmark" / "paraphrases.json")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, default=RESEARCH_DIR / "evaluation" / "results" / "router_eval_r3")
    args = parser.parse_args()

    questions = (yaml.safe_load(args.questions.read_text()) or {})["questions"]
    payload = json.loads(args.paraphrases.read_text())
    examples = [
        {
            "example_id": f"{record['question_id']}_P{index}",
            "question_id": record["question_id"],
            "question": paraphrase,
            "expected": record["metrics"],
        }
        for record in payload["records"]
        for index, paraphrase in enumerate(record["paraphrases"], start=1)
    ]
    registry = MetricRegistry.from_yaml()
    threshold, calibration_scores = calibrate_threshold(questions, registry)
    router = LexicalMetricRouter.from_questions(questions, registry)
    rows: list[dict] = []
    for example in examples:
        predicted = router.predict(example["question"], relative_threshold=threshold)
        rows.append({
            **example, "system": "lexical_router", "repeat_index": 0,
            "predicted": predicted, "ranking": router.rank(example["question"]),
            "scores": score(predicted, example["expected"]),
        })

    prompt = codex_prompt(examples, registry)
    batch_metadata = []
    valid_slugs = set(registry.slugs())
    for repeat_index in range(args.repeats):
        last_error = None
        for attempt in range(1, 4):
            try:
                outputs, metadata = run_codex_batch(prompt)
                metadata["attempt"] = attempt
                break
            except RuntimeError as exc:
                last_error = exc
                if attempt == 3:
                    raise
                time.sleep(5 * attempt)
        batch_metadata.append({"repeat_index": repeat_index, **metadata})
        for example in examples:
            raw = outputs.get(example["example_id"], "[]")
            try:
                predicted = json.loads(raw)
            except json.JSONDecodeError:
                predicted = []
            predicted = [slug for slug in predicted if slug in valid_slugs]
            rows.append({
                **example, "system": "codex_metric_router", "repeat_index": repeat_index,
                "raw_output": raw, "predicted": predicted,
                "scores": score(predicted, example["expected"]),
            })

    by_system: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_system[row["system"]].append(row)
    summary = {system: aggregate(system_rows) for system, system_rows in by_system.items()}
    summary["lexical_router"]["calibrated_relative_threshold"] = threshold
    summary["lexical_router"]["leave_one_out_calibration_accuracy"] = calibration_scores[f"{threshold:.2f}"]
    codex_rows = by_system.get("codex_metric_router", [])
    if codex_rows:
        stability: dict[str, set[tuple[str, ...]]] = defaultdict(set)
        for row in codex_rows:
            stability[row["example_id"]].add(tuple(row["predicted"]))
        summary["codex_metric_router"]["stable_examples"] = sum(len(values) == 1 for values in stability.values())
        summary["codex_metric_router"]["total_unique_examples"] = len(stability)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "results.json").write_text(json.dumps(rows, indent=2))
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    (args.output_dir / "experiment_manifest.json").write_text(json.dumps({
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "training_examples": len(questions),
        "held_out_paraphrases": len(examples),
        "codex_repeats": args.repeats,
        "split_policy": payload.get("split_policy"),
        "lexical_threshold_calibration": {
            "method": "leave-one-original-question-out; held-out paraphrases are not used",
            "selected_threshold": threshold,
            "candidate_scores": calibration_scores,
        },
        "codex_batches": batch_metadata,
    }, indent=2, default=str))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
