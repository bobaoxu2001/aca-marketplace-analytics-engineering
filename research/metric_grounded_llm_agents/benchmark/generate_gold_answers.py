#!/usr/bin/env python3
"""Generate structured gold answers from benchmark SQL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import duckdb
import yaml

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent.paths import DEFAULT_DATABASE, DEFAULT_QUESTIONS, RESEARCH_DIR  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--output-dir", type=Path, default=RESEARCH_DIR / "benchmark" / "gold_answers")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    questions = yaml.safe_load(args.questions.read_text())["questions"]
    if args.limit:
        questions = questions[: args.limit]
    if not args.database.exists():
        print(f"Missing DuckDB database: {args.database}")
        print("Run the CMS download, load, and dbt build before generating gold answers.")
        return 2

    manifest = []
    with duckdb.connect(str(args.database), read_only=True) as connection:
        for question in questions:
            sql_path = RESEARCH_DIR / question["gold_sql"]
            result = connection.execute(sql_path.read_text())
            columns = [column[0] for column in result.description]
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            payload = {
                "question_id": question["id"],
                "question": question["question"],
                "gold_sql": question["gold_sql"],
                "row_count": len(rows),
                "rows": rows,
            }
            output_path = args.output_dir / f"{question['id']}.json"
            output_path.write_text(json.dumps(payload, indent=2, default=str))
            manifest.append({"question_id": question["id"], "row_count": len(rows), "path": str(output_path)})
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"Wrote {len(manifest)} gold answer files to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
