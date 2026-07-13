#!/usr/bin/env python3
"""Generate held-out benchmark paraphrases with the logged-in Codex model."""

from __future__ import annotations

import argparse
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
    parser.add_argument("--output", type=Path, default=RESEARCH_DIR / "benchmark" / "paraphrases.json")
    args = parser.parse_args()

    questions = (yaml.safe_load(args.questions.read_text()) or {})["questions"]
    prompt = "\n".join([
        "Create exactly two meaning-preserving paraphrases for every analytics question below.",
        "Do not answer the question. Do not add numbers, filters, assumptions, metrics, or data sources.",
        "Preserve whether the question asks for highest, lowest, difference, distribution, association, or count.",
        "Return every question exactly once using the required JSON schema.",
        "For each output string, encode a JSON array of exactly two paraphrase strings.",
        "",
        *[f"{question['id']}: {question['question']}" for question in questions],
    ])
    outputs, metadata = run_codex_batch(prompt)
    records = []
    for question in questions:
        raw = outputs.get(question["id"])
        if raw is None:
            raise RuntimeError(f"Missing paraphrases for {question['id']}")
        paraphrases = json.loads(raw)
        if not isinstance(paraphrases, list) or len(paraphrases) != 2 or not all(isinstance(item, str) for item in paraphrases):
            raise ValueError(f"Invalid paraphrases for {question['id']}: {raw}")
        records.append({
            "question_id": question["id"],
            "source_question": question["question"],
            "metrics": question.get("metrics", []),
            "paraphrases": paraphrases,
        })
    payload = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "generator": {
            "provider": metadata.get("provider"),
            "model": metadata.get("model"),
            "codex_cli_version": metadata.get("codex_cli_version"),
            "usage": metadata.get("usage"),
            "latency_seconds": metadata.get("latency_seconds"),
        },
        "split_policy": "Original questions are router training prototypes; paraphrases are held-out evaluation only.",
        "records": records,
    }
    args.output.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {len(records) * 2} paraphrases to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
