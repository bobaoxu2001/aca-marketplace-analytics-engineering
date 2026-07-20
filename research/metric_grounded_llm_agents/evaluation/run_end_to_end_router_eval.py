#!/usr/bin/env python3
"""Run held-out paraphrases through oracle and predicted metric routing."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import duckdb
import yaml

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent.metric_registry import MetricRegistry  # noqa: E402
from agent.metric_router import LexicalMetricRouter  # noqa: E402
from agent.metric_sql import generate_metric_sql  # noqa: E402
from agent.paths import DEFAULT_DATABASE, DEFAULT_QUESTIONS, RESEARCH_DIR  # noqa: E402
from agent.validators import validate_sql  # noqa: E402
from evaluation.metrics import summarize  # noqa: E402
from evaluation.result_metrics import compare_result_rows, numeric_claim_faithfulness  # noqa: E402
from evaluation.run_eval import load_gold_answers, write_report  # noqa: E402
from evaluation.run_router_eval import calibrate_threshold  # noqa: E402


def execute(database: Path, sql: str) -> list[dict[str, Any]]:
    with duckdb.connect(str(database), read_only=True) as connection:
        connection.execute("set schema 'main_marts'")
        query = connection.execute(sql)
        columns = [column[0] for column in query.description]
        return [dict(zip(columns, row)) for row in query.fetchall()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--paraphrases", type=Path, default=RESEARCH_DIR / "benchmark" / "paraphrases.json")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--gold-dir", type=Path, default=RESEARCH_DIR / "benchmark" / "gold_answers")
    parser.add_argument(
        "--codex-router-results",
        type=Path,
        help="Optional results.json from run_router_eval.py; adds every saved Codex routing repeat.",
    )
    parser.add_argument("--output-dir", type=Path, default=RESEARCH_DIR / "evaluation" / "results" / "heldout_end_to_end")
    args = parser.parse_args()

    questions = (yaml.safe_load(args.questions.read_text()) or {})["questions"]
    by_id = {question["id"]: question for question in questions}
    paraphrase_payload = json.loads(args.paraphrases.read_text())
    gold = load_gold_answers(args.gold_dir)
    registry = MetricRegistry.from_yaml()
    threshold, calibration = calibrate_threshold(questions, registry)
    router = LexicalMetricRouter.from_questions(questions, registry)
    codex_routes: dict[tuple[str, int], list[str]] = {}
    codex_repeats: list[int] = []
    if args.codex_router_results:
        router_rows = json.loads(args.codex_router_results.read_text())
        codex_rows = [row for row in router_rows if row.get("system") == "codex_metric_router"]
        codex_routes = {
            (row["example_id"], int(row["repeat_index"])): row.get("predicted", [])
            for row in codex_rows
        }
        codex_repeats = sorted({int(row["repeat_index"]) for row in codex_rows})
    results: list[dict[str, Any]] = []

    for record in paraphrase_payload["records"]:
        source = by_id[record["question_id"]]
        for index, text in enumerate(record["paraphrases"], start=1):
            example_id = f"{record['question_id']}_P{index}"
            predicted_metrics = router.predict(text, relative_threshold=threshold)
            routes = [
                ("heldout_oracle_route", record["metrics"]),
                ("heldout_lexical_route", predicted_metrics),
            ]
            routes.extend(
                ("heldout_codex_route", codex_routes[(example_id, repeat_index)], repeat_index)
                for repeat_index in codex_repeats
                if (example_id, repeat_index) in codex_routes
            )
            for route in routes:
                system, routed_metrics = route[:2]
                repeat_index = route[2] if len(route) == 3 else 0
                start = time.perf_counter()
                allowed_tables = registry.allowed_tables_for(routed_metrics)
                question = {
                    **source,
                    "id": example_id,
                    "question": text,
                    "metrics": routed_metrics,
                    "source_tables": sorted(allowed_tables),
                }
                base = {
                    "system": system,
                    "question_id": record["question_id"],
                    "example_id": example_id,
                    "question": text,
                    "expected_metrics": record["metrics"],
                    "routed_metrics": routed_metrics,
                    "route_exact_match": set(routed_metrics) == set(record["metrics"]),
                    "repeat_index": repeat_index,
                    "citations": [],
                }
                sql = None
                try:
                    if not routed_metrics:
                        raise LookupError("Metric router abstained: no metric slug was selected.")
                    sql = generate_metric_sql(question)
                    validation = validate_sql(sql, allowed_tables, source.get("required_terms", []))
                    if not validation.passed:
                        raise ValueError("; ".join(validation.messages) or "SQL validation failed")
                    rows = execute(args.database, sql)
                    answer = f"Top result: {rows[0]}." if rows else "No result rows were returned."
                    result = {
                        **base, "status": "ok", "sql": sql, "rows": rows,
                        "answer": answer, "validation": validation.checks,
                        "support_status": "supported_by_result_rows" if rows else "unsupported_no_rows",
                    }
                except Exception as exc:
                    result = {
                        **base,
                        "status": "router_abstention" if isinstance(exc, LookupError) else "sql_execution_error",
                        "sql": sql,
                        "rows": [], "answer": f"Held-out execution failed: {exc}",
                        "failure_type": "RouterAbstention" if isinstance(exc, LookupError) else type(exc).__name__,
                    }
                gold_rows = (gold.get(record["question_id"]) or {}).get("rows") or []
                result["result_metrics"] = (
                    compare_result_rows(result.get("rows"), gold_rows)
                    if result.get("status") == "ok"
                    else {"status": "not_executed", "execution_result_match": None,
                          "compatible_projection_match": None}
                )
                result["faithfulness_metrics"] = numeric_claim_faithfulness(
                    result.get("answer"), result.get("rows") or []
                )
                result["latency_seconds"] = round(time.perf_counter() - start, 4)
                results.append(result)

    summary = summarize(results)
    for system in summary:
        system_rows = [row for row in results if row["system"] == system]
        summary[system]["route_exact_match_rate"] = round(
            sum(row["route_exact_match"] for row in system_rows) / len(system_rows), 6
        )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "results.json").write_text(json.dumps(results, indent=2, default=str))
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    (args.output_dir / "experiment_manifest.json").write_text(json.dumps({
        "heldout_examples": sum(len(record["paraphrases"]) for record in paraphrase_payload["records"]),
        "systems": ["heldout_oracle_route", "heldout_lexical_route"] + (
            ["heldout_codex_route"] if codex_repeats else []
        ),
        "codex_router_results": str(args.codex_router_results) if args.codex_router_results else None,
        "codex_router_repeats": codex_repeats,
        "lexical_threshold": threshold,
        "leave_one_out_calibration_accuracy": calibration[f"{threshold:.2f}"],
        "interpretation": (
            "Oracle routing isolates compiler generalization; lexical and saved Codex routes add routing error. "
            "All routes use the same deterministic SQL compiler."
        ),
    }, indent=2))
    write_report(args.output_dir / "evaluation_report.md", summary, results)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
