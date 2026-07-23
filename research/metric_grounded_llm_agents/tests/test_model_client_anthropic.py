"""Offline tests for the Anthropic Messages API request style.

These never touch the network: they exercise only the pure request/response
shaping helpers (style resolution, usage normalization, response parsing logic),
so CI can verify the Anthropic branch without a key or spend.
"""

from __future__ import annotations

from agent import model_client as mc


def test_api_style_resolves_to_anthropic():
    cfg = {"provider": "anthropic", "api_style": "anthropic", "base_url": "https://api.anthropic.com"}
    assert mc._api_style(cfg) == "anthropic"
    assert mc._base_url(cfg) == "https://api.anthropic.com"


def test_usage_normalization_folds_cache_tokens_into_total():
    # Anthropic reports input_tokens as the UNcached portion; the normalizer must
    # fold cache reads/writes back so _estimated_cost sees the true total.
    raw = {
        "input_tokens": 1500,
        "output_tokens": 320,
        "cache_read_input_tokens": 200,
        "cache_creation_input_tokens": 0,
    }
    usage = mc._normalize_usage(raw, "anthropic")
    assert usage["input_tokens"] == 1700  # 1500 uncached + 200 cache read
    assert usage["output_tokens"] == 320
    assert usage["cached_input_tokens"] == 200


def test_estimated_cost_uses_cached_and_uncached_rates():
    cfg = {
        "pricing": {
            "input_usd_per_million_tokens": 1.0,
            "cached_input_usd_per_million_tokens": 0.1,
            "output_usd_per_million_tokens": 5.0,
        }
    }
    usage = {"input_tokens": 1700, "output_tokens": 320, "cached_input_tokens": 200}
    # (1500 * 1.0 + 200 * 0.1 + 320 * 5.0) / 1e6
    assert mc._estimated_cost(usage, cfg) == round((1500 * 1.0 + 200 * 0.1 + 320 * 5.0) / 1_000_000, 8)
