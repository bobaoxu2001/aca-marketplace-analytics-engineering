"""Small OpenAI Responses API client shared by the live benchmark baselines."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests
import yaml

from .paths import RESEARCH_DIR


def model_config() -> dict[str, Any]:
    path = RESEARCH_DIR / "configs" / "model_config.example.yaml"
    return yaml.safe_load(path.read_text()) or {}


def api_key() -> str | None:
    return os.getenv(str(model_config().get("api_key_env", "OPENAI_API_KEY")))


@dataclass(frozen=True)
class ModelCall:
    text: str
    metadata: dict[str, Any]


def _estimated_cost(usage: dict[str, Any], config: dict[str, Any]) -> float | None:
    pricing = config.get("pricing") or {}
    required = {"input_usd_per_million_tokens", "output_usd_per_million_tokens"}
    if not required.issubset(pricing):
        return None
    input_tokens = int(usage.get("input_tokens") or 0)
    output_tokens = int(usage.get("output_tokens") or 0)
    cached_tokens = int((usage.get("input_tokens_details") or {}).get("cached_tokens") or 0)
    uncached_tokens = max(input_tokens - cached_tokens, 0)
    cached_rate = float(pricing.get("cached_input_usd_per_million_tokens", pricing["input_usd_per_million_tokens"]))
    cost = (
        uncached_tokens * float(pricing["input_usd_per_million_tokens"])
        + cached_tokens * cached_rate
        + output_tokens * float(pricing["output_usd_per_million_tokens"])
    ) / 1_000_000
    return round(cost, 8)


def response_call(prompt: str, *, instructions: str | None = None) -> ModelCall:
    """Return text plus reproducibility and usage metadata from Responses API."""
    config = model_config()
    if config.get("provider", "openai") != "openai":
        raise ValueError("Only the configured OpenAI provider is supported.")
    key = api_key()
    if not key:
        raise RuntimeError("No configured model API key is available.")
    payload: dict[str, Any] = {
        "model": config.get("model_snapshot") or config.get("model", "gpt-4.1-mini"),
        "input": prompt,
        "store": False,
        "max_output_tokens": int(config.get("max_output_tokens", 1200)),
    }
    if config.get("temperature") is not None:
        payload["temperature"] = config["temperature"]
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
    usage = data.get("usage") or {}
    metadata = {
        "response_id": data.get("id"),
        "model": data.get("model") or payload["model"],
        "requested_model": payload["model"],
        "status": data.get("status"),
        "service_tier": data.get("service_tier"),
        "usage": usage,
        "estimated_cost_usd": _estimated_cost(usage, config),
        "pricing_snapshot": config.get("pricing"),
        "request_parameters": {
            "temperature": payload.get("temperature"),
            "max_output_tokens": payload["max_output_tokens"],
            "store": False,
        },
    }
    return ModelCall(text=text, metadata=metadata)


def response_text(prompt: str, *, instructions: str | None = None) -> str:
    """Backward-compatible text-only wrapper."""
    return response_call(prompt, instructions=instructions).text
