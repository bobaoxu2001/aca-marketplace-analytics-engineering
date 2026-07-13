#!/usr/bin/env python3
"""Generate a frozen high-lexical-shift routing challenge set with Codex."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent.paths import DEFAULT_QUESTIONS, RESEARCH_DIR  # noqa: E402
from evaluation.run_codex_pilot import run_codex_batch  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--output", type=Path, default=RESEARCH_DIR / "benchmark" / "routing_challenge_v1.json")
    args = parser.parse_args()
    questions = (yaml.safe_load(args.questions.read_text()) or {})["questions"]
    prompt = "\n".join([
        "Create exactly one difficult but meaning-equivalent rewrite for every analytics question below.",
        "The rewrite is for a frozen semantic-routing challenge set, not ordinary paraphrasing.",
        "Do not answer. Preserve every requested comparison, grouping, filter, direction, and measure.",
        "Maximize lexical and syntactic distance: use an analyst scenario, indirect wording, or domain synonym.",
        "Avoid copying any 3-word sequence from the source except unavoidable proper nouns.",
        "Do not introduce new populations, thresholds, numbers, assumptions, or data sources.",
        "Return every ID once. Each output must be a JSON array containing exactly one string.",
        "",
        *[f"{question['id']}: {question['question']}" for question in questions],
    ])
    outputs, metadata = run_codex_batch(prompt)
    records = []
    for question in questions:
        value = json.loads(outputs[question["id"]])
        if not isinstance(value, list) or len(value) != 1 or not isinstance(value[0], str):
            raise ValueError(f"Invalid challenge item for {question['id']}: {value!r}")
        records.append({
            "question_id": question["id"], "source_question": question["question"],
            "metrics": question.get("metrics", []), "paraphrases": value,
        })
    content = json.dumps(records, sort_keys=True, ensure_ascii=False).encode()
    payload = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_sha256": hashlib.sha256(content).hexdigest(),
        "lock_policy": "Frozen before any router evaluation or compiler inspection on this dataset.",
        "split_policy": "High-lexical-shift model-generated challenge; no human authorship claim.",
        "generator": {key: metadata.get(key) for key in (
            "provider", "model", "codex_cli_version", "usage", "latency_seconds"
        )},
        "records": records,
    }
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(json.dumps({"items": len(records), "dataset_sha256": payload["dataset_sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
