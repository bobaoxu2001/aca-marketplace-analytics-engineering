"""LLM + SQL baseline interface."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .metric_grounded_agent import MetricGroundedAgent
from .paths import DEFAULT_DATABASE


class LLMSQLBaseline:
    """Executes benchmark gold SQL as a deterministic stand-in until an LLM is configured."""

    def __init__(self, database: Path = DEFAULT_DATABASE):
        self._agent = MetricGroundedAgent(database=database)

    def answer(self, question: dict[str, Any]) -> dict[str, Any]:
        result = self._agent.answer(question)
        result["system"] = "llm_sql_baseline"
        result["status_note"] = "Uses gold SQL as a deterministic adapter until live LLM SQL generation is configured."
        return result

