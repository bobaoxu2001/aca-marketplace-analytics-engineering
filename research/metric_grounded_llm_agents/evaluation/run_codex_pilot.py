#!/usr/bin/env python3
"""Run a no-API-key, batched Codex subscription pilot.

This is intentionally a separate experimental condition from raw API baselines.
Codex system instructions and batching can affect behavior, and the runner labels
the results accordingly.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import yaml

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent.paths import DEFAULT_DATABASE, DEFAULT_QUESTIONS, RESEARCH_DIR  # noqa: E402
from agent.validators import validate_sql  # noqa: E402
from evaluation.metrics import summarize  # noqa: E402
from evaluation.result_metrics import compare_result_rows, numeric_claim_faithfulness  # noqa: E402
from evaluation.run_eval import file_sha256, git_sha, load_gold_answers, write_report  # noqa: E402


SCHEMA_PATH = RESEARCH_DIR / "configs" / "codex_batch_output.schema.json"


def codex_version() -> str:
    return subprocess.check_output(["codex", "--version"], text=True).strip()


def run_codex_batch(prompt: str) -> tuple[dict[str, str], dict[str, Any]]:
    start = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="aca-codex-pilot-") as workdir:
        process = subprocess.run(
            [
                "codex", "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
                "--skip-git-repo-check", "--sandbox", "read-only", "-C", workdir,
                "--output-schema", str(SCHEMA_PATH), "--json", "-",
            ],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=900,
            check=False,
        )
    events: list[dict[str, Any]] = []
    for line in process.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    messages = [
        event["item"]["text"] for event in events
        if event.get("type") == "item.completed"
        and (event.get("item") or {}).get("type") == "agent_message"
    ]
    usage_events = [event.get("usage") or {} for event in events if event.get("type") == "turn.completed"]
    metadata = {
        "provider": "codex_subscription",
        "model": "codex_default_logged_in_model",
        "codex_cli_version": codex_version(),
        "return_code": process.returncode,
        "latency_seconds": round(time.perf_counter() - start, 4),
        "usage": usage_events[-1] if usage_events else {},
        "estimated_cost_usd": None,
        "stderr_tail": process.stderr[-2000:],
        "stdout_tail": process.stdout[-4000:],
        "event_errors": [
            event for event in events
            if event.get("type") in {"turn.failed", "error"}
        ],
    }
    if process.returncode != 0 or not messages:
        raise RuntimeError(json.dumps(metadata, default=str))
    payload = json.loads(messages[-1])
    return {item["question_id"]: item["output"] for item in payload["results"]}, metadata


def direct_prompt(questions: list[dict[str, Any]]) -> str:
    lines = [
        "This is a controlled Direct Codex analytics baseline.",
        "Do not use tools, files, databases, code execution, or internet access.",
        "Answer each question using only the question text. Do not invent numbers.",
        "Return every question exactly once using the required JSON schema.",
        "For each item, question_id is the supplied ID and output is the concise answer.",
        "",
    ]
    lines.extend(f"{question['id']}: {question['question']}" for question in questions)
    return "\n".join(lines)


def schema_context(database: Path) -> str:
    with duckdb.connect(str(database), read_only=True) as connection:
        rows = connection.execute(
            "select table_name, column_name, data_type from information_schema.columns "
            "where table_schema = 'main_marts' order by table_name, ordinal_position"
        ).fetchall()
    return "\n".join(f"{table}.{column} {data_type}" for table, column, data_type in rows)


def sql_prompt(questions: list[dict[str, Any]], database: Path) -> str:
    lines = [
        "This is a controlled Codex-to-SQL baseline.",
        "Do not use tools, files, databases, code execution, or internet access.",
        "Generate one read-only DuckDB SELECT query for every question.",
        "Use only the allowed tables listed for that question and no schema prefixes.",
        "Return every question exactly once using the required JSON schema.",
        "For each item, output must be SQL only with no Markdown fences.",
        "",
        "WAREHOUSE SCHEMA:",
        schema_context(database),
        "",
        "QUESTIONS:",
    ]
    for question in questions:
        lines.append(
            f"{question['id']}: {question['question']} | "
            f"allowed_tables={','.join(question.get('source_tables', []))} | "
            f"required_terms={','.join(question.get('required_terms', []))}"
        )
    return "\n".join(lines)


def shared_model_call(metadata: dict[str, Any], batch_id: str, first: bool) -> dict[str, Any]:
    copied = dict(metadata)
    copied["batch_id"] = batch_id
    copied["usage_shared_across_batch"] = True
    if not first:
        copied["usage"] = {}
    return copied


def enrich(result: dict[str, Any], gold: dict[str, Any] | None) -> dict[str, Any]:
    gold_rows = (gold or {}).get("rows") or []
    result["gold_available"] = bool(gold)
    result["gold_sql"] = (gold or {}).get("gold_sql")
    result["result_metrics"] = (
        compare_result_rows(result.get("rows"), gold_rows)
        if result.get("status") == "ok" and result.get("system") != "direct_codex_batched"
        else {"status": "not_evaluable", "execution_result_match": None,
              "compatible_projection_match": None}
    )
    result["faithfulness_metrics"] = numeric_claim_faithfulness(
        result.get("answer"), result.get("rows") or []
    )
    return result


def is_abstention(answer: str) -> bool:
    lowered = answer.casefold()
    return any(phrase in lowered for phrase in (
        "cannot determine", "can't determine", "insufficient data", "not enough data",
        "no data", "data is not provided", "data are not provided",
    ))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--gold-dir", type=Path, default=RESEARCH_DIR / "benchmark" / "gold_answers")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--question-overrides", type=Path,
        help="Optional paraphrase/challenge JSON; replaces question text by question_id while retaining contracts.",
    )
    parser.add_argument("--conditions", default="direct_codex_batched,codex_sql_batched")
    parser.add_argument("--experiment-id", default="codex_subscription_batched_r3")
    parser.add_argument("--output-dir", type=Path, default=RESEARCH_DIR / "evaluation" / "results" / "codex_subscription_batched_r3")
    args = parser.parse_args()

    questions = (yaml.safe_load(args.questions.read_text()) or {}).get("questions", [])
    if args.question_overrides:
        override_payload = json.loads(args.question_overrides.read_text())
        overrides = {
            record["question_id"]: record["paraphrases"][0]
            for record in override_payload["records"]
        }
        questions = [{**question, "question": overrides.get(question["id"], question["question"])} for question in questions]
    if args.limit:
        questions = questions[:args.limit]
    gold = load_gold_answers(args.gold_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    started = datetime.now(timezone.utc).isoformat()

    selected_conditions = {value.strip() for value in args.conditions.split(",") if value.strip()}
    condition_prompts = [item for item in (
            ("direct_codex_batched", direct_prompt(questions)),
            ("codex_sql_batched", sql_prompt(questions, args.database)),
        ) if item[0] in selected_conditions]
    for repeat_index in range(args.repeats):
        for condition, prompt in condition_prompts:
            batch_id = f"{condition}_r{repeat_index}"
            try:
                outputs, metadata = run_codex_batch(prompt)
                batch_error = None
            except Exception as exc:
                outputs, metadata, batch_error = {}, {}, exc
            for index, question in enumerate(questions):
                output = outputs.get(question["id"])
                base = {
                    "experiment_id": args.experiment_id,
                    "repeat_index": repeat_index,
                    "system": condition,
                    "question_id": question["id"],
                    "question": question["question"],
                    "difficulty": question.get("difficulty"),
                    "category": question.get("category"),
                    "prompt": prompt,
                    "instructions": "Embedded in batched prompt; tools and external data prohibited.",
                    "model_call": shared_model_call(metadata, batch_id, index == 0) if metadata else None,
                    "latency_seconds": metadata.get("latency_seconds", 0.0),
                    "batch_latency_not_per_question": True,
                    "citations": [],
                }
                if batch_error or output is None:
                    result = {
                        **base, "status": "model_api_error", "sql": None,
                        "answer": f"Codex batch failed: {batch_error or 'missing question output'}",
                        "failure_type": type(batch_error).__name__ if batch_error else "MissingBatchOutput",
                    }
                elif condition == "direct_codex_batched":
                    result = {
                        **base, "status": "ok", "answer": output, "sql": None, "rows": [],
                        "support_status": "unsupported_claim_marked" if is_abstention(output) else "unsupported_unverified_answer",
                    }
                else:
                    sql = output.strip().removeprefix("```sql").removesuffix("```").strip()
                    validation = validate_sql(sql, question.get("source_tables", []), question.get("required_terms", []))
                    try:
                        if not validation.passed:
                            raise ValueError("; ".join(validation.messages) or "SQL validation failed")
                        with duckdb.connect(str(args.database), read_only=True) as connection:
                            connection.execute("set schema 'main_marts'")
                            query = connection.execute(sql)
                            columns = [column[0] for column in query.description]
                            rows = [dict(zip(columns, row)) for row in query.fetchall()]
                        result = {
                            **base, "status": "ok", "sql": sql, "rows": rows,
                            "answer": f"Top result: {rows[0]}." if rows else "No result rows were returned.",
                            "validation": validation.checks,
                            "support_status": "supported_by_result_rows" if rows else "unsupported_no_rows",
                        }
                    except Exception as exc:
                        result = {
                            **base, "status": "sql_execution_error", "sql": sql,
                            "answer": f"Generated SQL could not execute: {exc}",
                            "validation": validation.checks, "failure_type": type(exc).__name__,
                        }
                results.append(enrich(result, gold.get(question["id"])))

    summary = summarize(results)
    (args.output_dir / "results.json").write_text(json.dumps(results, indent=2, default=str))
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    manifest = {
        "experiment_id": args.experiment_id,
        "experimental_condition": "batched_codex_subscription_pilot_not_raw_api",
        "started_at_utc": started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": git_sha(),
        "codex_cli_version": codex_version(),
        "database_sha256": file_sha256(args.database),
        "questions_sha256": file_sha256(args.questions),
        "question_overrides": str(args.question_overrides) if args.question_overrides else None,
        "question_overrides_sha256": file_sha256(args.question_overrides) if args.question_overrides else None,
        "question_count": len(questions),
        "repeats": args.repeats,
        "batch_count": args.repeats * len(condition_prompts),
        "conditions": sorted(selected_conditions),
        "result_count": len(results),
        "limitations": [
            "Codex system instructions are present and not equivalent to a raw model API call.",
            "Questions are batched, so latency and usage are batch-level, not per-question.",
            "Subscription cost in USD is unavailable; token usage is recorded.",
        ],
    }
    (args.output_dir / "experiment_manifest.json").write_text(json.dumps(manifest, indent=2))
    with (args.output_dir / "results.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "experiment_id", "repeat_index", "system", "question_id", "status",
            "support_status", "latency_seconds", "answer",
        ], extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    write_report(args.output_dir / "evaluation_report.md", summary, results)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
