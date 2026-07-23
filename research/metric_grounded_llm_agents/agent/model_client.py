"""Small model client shared by the live benchmark baselines.

Supports two request styles so the same evaluation can run against different
providers:

- ``responses``: the OpenAI Responses API (``/v1/responses``).
- ``chat_completions``: the widely used OpenAI-compatible Chat Completions API
  (``/chat/completions``), which also covers DeepSeek and other compatible
  endpoints via a configurable ``base_url``.

The style is taken from ``api_style`` in the model config, or inferred from the
provider (``openai`` → responses, anything else → chat_completions). Token usage
is normalized to ``input_tokens`` / ``output_tokens`` regardless of provider so
downstream cost and reporting code stays unchanged.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

import requests
import yaml

from .paths import RESEARCH_DIR


def model_config() -> dict[str, Any]:
    """Load the model config, preferring a local (gitignored) override."""
    configs = RESEARCH_DIR / "configs"
    for name in ("model_config.yaml", "model_config.example.yaml"):
        path = configs / name
        if path.exists():
            return yaml.safe_load(path.read_text()) or {}
    return {}


def api_key() -> str | None:
    return os.getenv(str(model_config().get("api_key_env", "OPENAI_API_KEY")))


@dataclass(frozen=True)
class ModelCall:
    text: str
    metadata: dict[str, Any]


def _api_style(config: dict[str, Any]) -> str:
    explicit = config.get("api_style")
    if explicit:
        return str(explicit)
    return "responses" if config.get("provider", "openai") == "openai" else "chat_completions"


def _estimated_cost(usage: dict[str, Any], config: dict[str, Any]) -> float | None:
    pricing = config.get("pricing") or {}
    required = {"input_usd_per_million_tokens", "output_usd_per_million_tokens"}
    if not required.issubset(pricing):
        return None
    input_tokens = int(usage.get("input_tokens") or 0)
    output_tokens = int(usage.get("output_tokens") or 0)
    cached_tokens = int(usage.get("cached_input_tokens") or 0)
    uncached_tokens = max(input_tokens - cached_tokens, 0)
    cached_rate = float(pricing.get("cached_input_usd_per_million_tokens", pricing["input_usd_per_million_tokens"]))
    cost = (
        uncached_tokens * float(pricing["input_usd_per_million_tokens"])
        + cached_tokens * cached_rate
        + output_tokens * float(pricing["output_usd_per_million_tokens"])
    ) / 1_000_000
    return round(cost, 8)


def _normalize_usage(raw: dict[str, Any], style: str) -> dict[str, Any]:
    """Return usage with input_tokens/output_tokens keys plus the raw record."""
    if style == "responses":
        input_tokens = int(raw.get("input_tokens") or 0)
        output_tokens = int(raw.get("output_tokens") or 0)
        cached = int((raw.get("input_tokens_details") or {}).get("cached_tokens") or 0)
    elif style == "anthropic":
        # Anthropic Messages API reports input_tokens as the UNcached portion and
        # lists cache reads/writes separately. _estimated_cost treats input_tokens
        # as the total (cached included), so fold cache tokens back into the total.
        cached = int(raw.get("cache_read_input_tokens") or 0)
        cache_write = int(raw.get("cache_creation_input_tokens") or 0)
        input_tokens = int(raw.get("input_tokens") or 0) + cached + cache_write
        output_tokens = int(raw.get("output_tokens") or 0)
    else:  # chat_completions
        input_tokens = int(raw.get("prompt_tokens") or 0)
        output_tokens = int(raw.get("completion_tokens") or 0)
        # DeepSeek and some others expose prompt cache hits.
        cached = int(raw.get("prompt_cache_hit_tokens") or 0)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cached_input_tokens": cached,
        "raw": raw,
    }


def _base_url(config: dict[str, Any]) -> str:
    default = "https://api.openai.com/v1" if _api_style(config) == "responses" else "https://api.openai.com/v1"
    return str(config.get("base_url", default)).rstrip("/")


def response_call(prompt: str, *, instructions: str | None = None) -> ModelCall:
    """Return text plus reproducibility and usage metadata from the model API."""
    config = model_config()
    key = api_key()
    if not key:
        raise RuntimeError("No configured model API key is available.")
    style = _api_style(config)
    model = config.get("model_snapshot") or config.get("model", "gpt-4.1-mini")
    max_output_tokens = int(config.get("max_output_tokens", 1200))
    if style == "anthropic":
        headers = {
            "x-api-key": key,
            "anthropic-version": str(config.get("anthropic_version", "2023-06-01")),
            "Content-Type": "application/json",
        }
    else:
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    if style == "responses":
        url = f"{_base_url(config)}/responses"
        payload: dict[str, Any] = {
            "model": model,
            "input": prompt,
            "store": False,
            "max_output_tokens": max_output_tokens,
        }
        if config.get("temperature") is not None:
            payload["temperature"] = config["temperature"]
        if instructions:
            payload["instructions"] = instructions
    elif style == "anthropic":
        url = f"{_base_url(config)}/v1/messages"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_output_tokens,
        }
        if config.get("temperature") is not None:
            payload["temperature"] = config["temperature"]
        if instructions:
            payload["system"] = instructions
    else:
        url = f"{_base_url(config)}/chat/completions"
        messages: list[dict[str, str]] = []
        if instructions:
            messages.append({"role": "system", "content": instructions})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_output_tokens,
            "stream": False,
        }
        if config.get("temperature") is not None:
            payload["temperature"] = config["temperature"]

    # Retry transient failures (dropped connections, TLS resets, proxy hiccups,
    # rate limiting, and 5xx) with exponential backoff. Client errors other than
    # 429 (bad key, insufficient balance, bad request) fail fast with the body,
    # since retrying cannot fix them.
    max_retries = max(int(config.get("max_retries", 4)), 1)
    backoff = float(config.get("retry_backoff_seconds", 2.0))
    timeout = int(config.get("request_timeout_seconds", 90))
    last_error: Exception | None = None
    response = None
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except requests.exceptions.RequestException as exc:
            last_error = exc
            if attempt < max_retries - 1:
                time.sleep(backoff * (2 ** attempt))
            continue
        if response.status_code == 429 or response.status_code >= 500:
            last_error = RuntimeError(f"HTTP {response.status_code}: {response.text[:300]}")
            if attempt < max_retries - 1:
                time.sleep(backoff * (2 ** attempt))
            continue
        if response.status_code >= 400:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:300]}")
        break
    else:
        raise last_error if last_error else RuntimeError("Model call failed after retries.")
    data = response.json()

    if style == "responses":
        text = "".join(
            item.get("text", "")
            for output in data.get("output", [])
            for item in output.get("content", [])
            if item.get("type") == "output_text"
        ).strip()
    elif style == "anthropic":
        text = "".join(
            block.get("text", "")
            for block in data.get("content", [])
            if block.get("type") == "text"
        ).strip()
    else:
        text = "".join(
            choice.get("message", {}).get("content", "") or ""
            for choice in data.get("choices", [])
        ).strip()
    if not text:
        raise RuntimeError("The model response did not contain output text.")

    usage = _normalize_usage(data.get("usage") or {}, style)
    metadata = {
        "response_id": data.get("id"),
        "model": data.get("model") or model,
        "requested_model": model,
        "provider": config.get("provider", "openai"),
        "api_style": style,
        "base_url": _base_url(config),
        "status": data.get("status"),
        "service_tier": data.get("service_tier"),
        "usage": usage,
        "estimated_cost_usd": _estimated_cost(usage, config),
        "pricing_snapshot": config.get("pricing"),
        "request_parameters": {
            "temperature": payload.get("temperature"),
            "max_output_tokens": max_output_tokens,
            "store": False,
        },
    }
    return ModelCall(text=text, metadata=metadata)


def response_text(prompt: str, *, instructions: str | None = None) -> str:
    """Backward-compatible text-only wrapper."""
    return response_call(prompt, instructions=instructions).text
