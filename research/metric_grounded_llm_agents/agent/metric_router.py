"""Non-oracle lexical metric router for held-out paraphrase evaluation."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from typing import Any

from .metric_registry import MetricRegistry


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def features(text: str) -> Counter[str]:
    normalized = " ".join(TOKEN_PATTERN.findall(text.casefold()))
    tokens = normalized.split()
    values: Counter[str] = Counter()
    values.update(f"w:{token}" for token in tokens)
    values.update(f"b:{left}_{right}" for left, right in zip(tokens, tokens[1:]))
    compact = normalized.replace(" ", "_")
    for width in (3, 4, 5):
        values.update(f"c:{compact[index:index + width]}" for index in range(max(len(compact) - width + 1, 0)))
    return values


def cosine(left: Counter[str], right: Counter[str]) -> float:
    numerator = sum(value * right.get(key, 0) for key, value in left.items())
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0


class LexicalMetricRouter:
    def __init__(self, profiles: dict[str, Counter[str]]):
        self.profiles = profiles

    @classmethod
    def from_questions(cls, questions: list[dict[str, Any]], registry: MetricRegistry) -> "LexicalMetricRouter":
        texts: dict[str, list[str]] = defaultdict(list)
        for question in questions:
            for slug in question.get("metrics", []):
                texts[slug].append(question["question"])
        for slug in registry.slugs():
            metric = registry.get(slug)
            texts[slug].append(" ".join([
                metric.name, metric.expression,
                " ".join(metric.allowed_dimensions),
                " ".join(metric.caveats),
            ]))
        profiles = {
            slug: sum((features(text) for text in samples), Counter())
            for slug, samples in texts.items()
        }
        return cls(profiles)

    def rank(self, question: str) -> list[tuple[str, float]]:
        query = features(question)
        return sorted(
            ((slug, cosine(query, profile)) for slug, profile in self.profiles.items()),
            key=lambda item: (-item[1], item[0]),
        )

    def predict(self, question: str, *, relative_threshold: float = 0.72, max_metrics: int = 2) -> list[str]:
        ranked = self.rank(question)
        if not ranked:
            return []
        top_score = ranked[0][1]
        return [
            slug for slug, score in ranked[:max_metrics]
            if score >= top_score * relative_threshold
        ]
