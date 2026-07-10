"""Small OpenAI Responses API client shared by the live benchmark baselines."""

from __future__ import annotations

import os
from typing import Any

import requests
import yaml

from .paths import RESEARCH_DIR


def model_config() -> dict[str, Any]:
    path = RESEARCH_DIR / "configs" / "model_config.example.yaml"
    return yaml.safe_load(path.read_text()) or {}


def api_key() -> str | None:
    return os.getenv(str(model_config().get("api_key_env", "OPENAI_API_KEY")))


def response_text(prompt: str, *, instructions: str | None = None) -> str:
    """Return text from a non-persistent OpenAI Responses API call."""
    config = model_config()
    if config.get("provider", "openai") != "openai":
        raise ValueError("Only the configured OpenAI provider is supported.")
    key = api_key()
    if not key:
        raise RuntimeError("No configured model API key is available.")
    payload: dict[str, Any] = {
        "model": config.get("model", "gpt-4.1-mini"),
        "input": prompt,
        "store": False,
    }
    if instructions:
        payload["instructions"] = instructions
    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=payload,
        timeout=90,
    )
    response.raise_for_status()
    data = response.json()
    text = "".join(
        item.get("text", "")
        for output in data.get("output", [])
        for item in output.get("content", [])
        if item.get("type") == "output_text"
    ).strip()
    if not text:
        raise RuntimeError("The model response did not contain output text.")
    return text
