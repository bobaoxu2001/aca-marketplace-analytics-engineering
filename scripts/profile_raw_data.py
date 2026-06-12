#!/usr/bin/env python3
"""Profile raw CMS PY2026 PUF CSV files with Polars.

Outputs a machine-readable JSON profile and a compact Markdown summary under
data/processed/. The code uses lazy CSV scanning so it can handle large Rate PUF
files without loading the entire dataset into memory at once.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import polars as pl


DEFAULT_RAW_DIR = Path("data/raw/py2026")
DEFAULT_OUTPUT_DIR = Path("data/processed")


@dataclass(frozen=True)
class DatasetProfileConfig:
    key: str
    filename: str
    duplicate_key_candidates: tuple[tuple[str, ...], ...]


DATASETS: tuple[DatasetProfileConfig, ...] = (
    DatasetProfileConfig(
        key="rate_puf",
        filename="rate_puf_py2026.csv",
        duplicate_key_candidates=(
            (
                "BusinessYear",
                "StateCode",
                "IssuerId",
                "PlanId",
                "RatingAreaId",
                "Tobacco",
                "Age",
                "RateEffectiveDate",
            ),
            ("BusinessYear", "StateCode", "PlanId", "RatingAreaId", "Age", "Tobacco"),
        ),
    ),
    DatasetProfileConfig(
        key="plan_attributes_puf",
        filename="plan_attributes_puf_py2026.csv",
        duplicate_key_candidates=(
            ("BusinessYear", "StateCode", "IssuerId", "PlanId"),
            ("BusinessYear", "StateCode", "StandardComponentId"),
        ),
    ),
    DatasetProfileConfig(
        key="benefits_cost_sharing_puf",
        filename="benefits_cost_sharing_puf_py2026.csv",
        duplicate_key_candidates=(
            ("BusinessYear", "StateCode", "IssuerId", "PlanId", "BenefitName"),
            ("BusinessYear", "StateCode", "StandardComponentId", "BenefitName"),
        ),
    ),
    DatasetProfileConfig(
        key="service_area_puf",
        filename="service_area_puf_py2026.csv",
        duplicate_key_candidates=(
            ("BusinessYear", "StateCode", "IssuerId", "ServiceAreaId", "County"),
            ("BusinessYear", "StateCode", "ServiceAreaId", "County"),
        ),
    ),
)


def scan_csv(path: Path) -> pl.LazyFrame:
    return pl.scan_csv(
        path,
        infer_schema_length=1000,
        ignore_errors=True,
        truncate_ragged_lines=True,
        null_values=["", "NULL", "null", "NA", "N/A", "Not Applicable"],
    )


def collect_streaming(lf: pl.LazyFrame) -> pl.DataFrame:
    return lf.collect(engine="streaming")


def choose_duplicate_key(columns: list[str], candidates: tuple[tuple[str, ...], ...]) -> list[str]:
    column_set = set(columns)
    for candidate in candidates:
        if set(candidate).issubset(column_set):
            return list(candidate)
    return []


def duplicate_profile(lf: pl.LazyFrame, key_columns: list[str]) -> dict[str, Any]:
    if not key_columns:
        return {
            "key_columns": [],
            "duplicate_groups": None,
            "duplicate_rows": None,
            "note": "No configured duplicate key was fully present in this file.",
        }

    result = (
        lf.group_by(key_columns)
        .len("row_count")
        .filter(pl.col("row_count") > 1)
        .select(
            pl.len().alias("duplicate_groups"),
            (pl.col("row_count") - 1).sum().alias("duplicate_rows"),
        )
        .pipe(collect_streaming)
    )
    row = result.row(0, named=True)
    return {
        "key_columns": key_columns,
        "duplicate_groups": int(row["duplicate_groups"] or 0),
        "duplicate_rows": int(row["duplicate_rows"] or 0),
    }


def sample_values(lf: pl.LazyFrame, columns: list[str], max_columns: int = 12) -> dict[str, list[str]]:
    samples: dict[str, list[str]] = {}
    for column in columns[:max_columns]:
        values = (
            lf.select(pl.col(column).cast(pl.Utf8).drop_nulls().unique().head(5))
            .pipe(collect_streaming)
            .to_series()
            .to_list()
        )
        samples[column] = [str(value) for value in values]
    return samples


def profile_dataset(config: DatasetProfileConfig, raw_dir: Path) -> dict[str, Any]:
    path = raw_dir / config.filename
    if not path.exists():
        return {
            "dataset": config.key,
            "filename": config.filename,
            "exists": False,
            "error": f"Missing file: {path}",
        }

    lf = scan_csv(path)
    schema = lf.collect_schema()
    columns = list(schema.names())
    row_count = int(collect_streaming(lf.select(pl.len().alias("row_count"))).item())

    null_counts = (
        lf.select([pl.col(column).null_count().alias(column) for column in columns])
        .pipe(collect_streaming)
        .row(0, named=True)
    )
    null_rates = {
        column: (float(null_counts[column]) / row_count if row_count else None)
        for column in columns
    }
    key_columns = choose_duplicate_key(columns, config.duplicate_key_candidates)

    return {
        "dataset": config.key,
        "filename": config.filename,
        "exists": True,
        "row_count": row_count,
        "column_count": len(columns),
        "columns": columns,
        "null_rates": null_rates,
        "duplicate_check": duplicate_profile(lf, key_columns),
        "sample_values": sample_values(lf, columns),
    }


def write_markdown(profile: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# Raw CMS PY2026 PUF Data Profile",
        "",
        "Generated by `scripts/profile_raw_data.py`.",
        "",
    ]
    for dataset in profile["datasets"]:
        lines.append(f"## {dataset['dataset']}")
        lines.append("")
        if not dataset.get("exists"):
            lines.append(f"- Status: missing ({dataset['filename']})")
            lines.append("")
            continue

        lines.extend(
            [
                f"- File: `{dataset['filename']}`",
                f"- Rows: {dataset['row_count']:,}",
                f"- Columns: {dataset['column_count']:,}",
                f"- Duplicate key: `{', '.join(dataset['duplicate_check']['key_columns'])}`",
                f"- Duplicate groups: {dataset['duplicate_check']['duplicate_groups']}",
                f"- Duplicate rows beyond first occurrence: {dataset['duplicate_check']['duplicate_rows']}",
                "",
                "| Column | Null rate | Sample values |",
                "| --- | ---: | --- |",
            ]
        )
        for column, null_rate in list(dataset["null_rates"].items())[:20]:
            samples = ", ".join(dataset["sample_values"].get(column, []))
            rendered_null_rate = "n/a" if null_rate is None else f"{null_rate:.2%}"
            lines.append(f"| `{column}` | {rendered_null_rate} | {samples} |")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    profile = {"datasets": [profile_dataset(config, args.raw_dir) for config in DATASETS]}
    json_path = args.output_dir / "raw_profile_py2026.json"
    markdown_path = args.output_dir / "raw_profile_py2026.md"
    json_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    write_markdown(profile, markdown_path)

    missing = [dataset["filename"] for dataset in profile["datasets"] if not dataset.get("exists")]
    if missing:
        print("Missing raw files:")
        for filename in missing:
            print(f"  - {filename}")
        print("Run scripts/download_cms_pufs.py or use the README manual fallback instructions.")
        return 2

    print(f"Wrote {json_path}")
    print(f"Wrote {markdown_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
