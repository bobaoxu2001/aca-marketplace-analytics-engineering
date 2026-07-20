#!/usr/bin/env python3
"""CLI demo for benchmark questions."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent.metric_grounded_agent import MetricGroundedAgent  # noqa: E402
from agent.paths import DEFAULT_DATABASE, DEFAULT_QUESTIONS  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question-id", default="Q001")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    args = parser.parse_args()
    questions = yaml.safe_load(DEFAULT_QUESTIONS.read_text())["questions"]
    lookup = {question["id"]: question for question in questions}
    if args.question_id not in lookup:
        print(f"Unknown question id: {args.question_id}")
        print("Available examples:", ", ".join(sorted(lookup)[:10]))
        return 2
    agent = MetricGroundedAgent(database=args.database)
    print(agent.answer_json(lookup[args.question_id]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
