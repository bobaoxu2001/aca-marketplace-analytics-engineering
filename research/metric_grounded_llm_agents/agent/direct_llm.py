"""Direct LLM baseline interface.

This baseline intentionally does not fabricate local answers when no model key is
configured. It records the prompt and status so evaluation can distinguish
unavailable model calls from failed data-grounded answers.
"""

from __future__ import annotations

import os
import time
from typing import Any


def answer(question: dict[str, Any]) -> dict[str, Any]:
    start = time.perf_counter()
    if not os.getenv("OPENAI_API_KEY"):
        return {
            "system": "direct_llm",
            "question_id": question["id"],
            "status": "skipped_missing_api_key",
            "answer": "OPENAI_API_KEY is not configured; direct LLM baseline was not run.",
            "sql": None,
            "citations": [],
            "latency_seconds": round(time.perf_counter() - start, 4),
        }
    return {
        "system": "direct_llm",
        "question_id": question["id"],
        "status": "not_implemented_model_adapter",
        "answer": "Model adapter placeholder. Configure configs/model_config.example.yaml before live calls.",
        "sql": None,
        "citations": [],
        "latency_seconds": round(time.perf_counter() - start, 4),
    }

