"""Metric registry used to constrain analytics answers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .paths import DEFAULT_METRICS_CONFIG


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    slug: str
    expression: str
    primary_tables: tuple[str, ...]
    allowed_dimensions: tuple[str, ...]
    caveats: tuple[str, ...]


class MetricRegistry:
    def __init__(self, metrics: list[MetricDefinition]):
        self._metrics = {metric.slug: metric for metric in metrics}

    @classmethod
    def from_yaml(cls, path: Path = DEFAULT_METRICS_CONFIG) -> "MetricRegistry":
        payload = yaml.safe_load(path.read_text()) or {}
        metrics = [
            MetricDefinition(
                name=item["name"],
                slug=item["slug"],
                expression=item["expression"],
                primary_tables=tuple(item.get("primary_tables", [])),
                allowed_dimensions=tuple(item.get("allowed_dimensions", [])),
                caveats=tuple(item.get("caveats", [])),
            )
            for item in payload.get("metrics", [])
        ]
        return cls(metrics)

    def get(self, slug: str) -> MetricDefinition:
        return self._metrics[slug]

    def select_for_question(self, question: dict[str, Any]) -> list[MetricDefinition]:
        return [self.get(slug) for slug in question.get("metrics", []) if slug in self._metrics]

    def allowed_tables_for(self, metric_slugs: list[str]) -> set[str]:
        tables: set[str] = set()
        for slug in metric_slugs:
            if slug in self._metrics:
                tables.update(self._metrics[slug].primary_tables)
        return tables

    def as_context(self, metric_slugs: list[str]) -> str:
        lines: list[str] = []
        for slug in metric_slugs:
            metric = self._metrics.get(slug)
            if metric:
                lines.append(
                    f"- {metric.name} ({metric.slug}): {metric.expression}; "
                    f"tables={', '.join(metric.primary_tables)}"
                )
        return "\n".join(lines)

