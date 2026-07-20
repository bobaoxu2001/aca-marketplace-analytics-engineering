#!/usr/bin/env python3
"""Build a system-label-blinded review packet from experiment outputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path


def load_repeat(path: Path, system: str, repeat: int = 0) -> dict[str, dict]:
    rows = json.loads((path / "results.json").read_text())
    return {
        row["question_id"]: row for row in rows
        if row["system"] == system and row.get("repeat_index") == repeat
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-results", type=Path, required=True)
    parser.add_argument("--metric-results", type=Path, required=True)
    parser.add_argument("--gold-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    systems = {
        "direct_codex": load_repeat(args.codex_results, "direct_codex_batched"),
        "codex_sql": load_repeat(args.codex_results, "codex_sql_batched"),
        "metric_grounded": load_repeat(args.metric_results, "metric_grounded"),
    }
    gold = {
        path.stem: json.loads(path.read_text())
        for path in args.gold_dir.glob("Q*.json")
    }
    items = []
    key = {}
    for system, by_question in systems.items():
        for question_id, row in by_question.items():
            digest = hashlib.sha256(f"aca-review-v1|{system}|{question_id}".encode()).hexdigest()[:12]
            item_id = f"R-{digest}"
            key[item_id] = {"system": system, "question_id": question_id, "repeat_index": 0}
            items.append({
                "review_item_id": item_id,
                "question_id": question_id,
                "question": row.get("question", ""),
                "answer": row.get("answer", ""),
                "sql": row.get("sql") or "",
                "evidence_rows_json": json.dumps((row.get("rows") or [])[:5], default=str),
                "reference_rows_json": json.dumps((gold.get(question_id) or {}).get("rows", [])[:5], default=str),
                "metric_correctness_1_to_5": "",
                "answer_faithfulness_1_to_5": "",
                "caveat_quality_1_to_5": "",
                "abstention_appropriate_yes_no_na": "",
                "unsupported_claim_yes_no": "",
                "reviewer_confidence_1_to_5": "",
                "reviewer_id": "",
                "notes": "",
            })
    random.Random(20260712).shuffle(items)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    packet = args.output_dir / "human_review_packet.csv"
    with packet.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(items[0]))
        writer.writeheader()
        writer.writerows(items)
    (args.output_dir / "human_review_key.json").write_text(json.dumps(key, indent=2))
    (args.output_dir / "README.md").write_text("""# System-Label-Blinded Human Review Packet

Give each reviewer only `human_review_packet.csv`; keep
`human_review_key.json` hidden until both reviewers finish.

This is not a fully condition-blinded design: SQL, abstentions, and evidence
format may allow a reviewer to infer the system family. Randomized item IDs and
the hidden key prevent direct system labels from being shown.

Rate every item independently:

- Metric correctness: whether the operationalized metric and grain answer the question.
- Answer faithfulness: whether the answer is entailed by the displayed evidence rows.
- Caveat quality: whether material limitations or uncertainty are handled appropriately.
- Abstention: whether refusing to answer is appropriate given the supplied evidence.
- Unsupported claim: mark yes when any substantive claim lacks displayed support.

Use 1 for clearly incorrect/poor and 5 for clearly correct/strong. Review the
displayed item without attempting to identify its system. After both reviews,
join on `review_item_id`, calculate agreement,
and adjudicate disagreements before revealing the key.
""")
    print(f"Wrote {len(items)} system-label-blinded items to {packet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
