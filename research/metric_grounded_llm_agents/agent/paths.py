"""Shared paths for the research benchmark."""

from __future__ import annotations

from pathlib import Path


RESEARCH_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = RESEARCH_DIR.parents[1]
DEFAULT_DATABASE = REPO_ROOT / "data" / "processed" / "aca_marketplace_py2026.duckdb"
DEFAULT_METRICS_CONFIG = RESEARCH_DIR / "configs" / "metrics.yaml"
DEFAULT_QUESTIONS = RESEARCH_DIR / "benchmark" / "questions.yaml"
