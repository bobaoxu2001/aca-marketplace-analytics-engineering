"""Direct LLM baseline interface.

This baseline intentionally does not fabricate local answers when no model key is
configured. It records the prompt and status so evaluation can distinguish
unavailable model calls from failed data-grounded answers.
"""

from __future__ import annotations

import time
from typing import Any

from .model_client import api_key, response_call


def answer(question: dict[str, Any]) -> dict[str, Any]:
    start = time.perf_counter()
    prompt = question["question"]
    instructions = (
        "Answer the analytics question concisely. Do not claim database access, "
        "and explicitly state uncertainty when the supplied question lacks data."
    )
    if not api_key():
        return {
            "system": "direct_llm",
            "question_id": question["id"],
            "status": "skipped_missing_api_key",
            "answer": "OPENAI_API_KEY is not configured; direct LLM baseline was not run.",
            "sql": None,
            "prompt": prompt,
            "instructions": instructions,
            "citations": [],
            "latency_seconds": round(time.perf_counter() - start, 4),
        }
    try:
        call = response_call(prompt, instructions=instructions)
    except Exception as exc:
        return {
            "system": "direct_llm", "question_id": question["id"], "status": "model_api_error",
            "answer": f"Direct model call failed: {exc}", "sql": None, "citations": [],
            "prompt": prompt, "instructions": instructions, "failure_type": type(exc).__name__,
            "latency_seconds": round(time.perf_counter() - start, 4),
        }
    return {
        "system": "direct_llm", "question_id": question["id"], "status": "ok",
        "answer": call.text, "sql": None, "citations": [],
        "prompt": prompt, "instructions": instructions, "model_call": call.metadata,
        "latency_seconds": round(time.perf_counter() - start, 4),
    }
