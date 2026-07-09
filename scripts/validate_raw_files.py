#!/usr/bin/env python3
"""Validate required local CMS PY2026 PUF CSV files before DuckDB loading."""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path


RAW_DIR = Path("data/raw/py2026")


@dataclass(frozen=True)
class RequiredFile:
    filename: str
    min_size_bytes: int
    min_columns: int


REQUIRED_FILES = (
    RequiredFile("rate_puf_py2026.csv", 1_000_000, 10),
    RequiredFile("plan_attributes_puf_py2026.csv", 100_000, 20),
    RequiredFile("benefits_cost_sharing_puf_py2026.csv", 1_000_000, 10),
    RequiredFile("service_area_puf_py2026.csv", 10_000, 5),
    RequiredFile("plan_id_crosswalk_puf_py2025_py2026.csv", 100_000, 10),
    RequiredFile("quality_puf_py2026.csv", 10_000, 5),
)


def validate_file(required: RequiredFile) -> dict:
    path = RAW_DIR / required.filename
    result = {
        "filename": required.filename,
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "column_count": 0,
        "status": "ok",
        "errors": [],
    }
    if not path.exists():
        result["status"] = "failed"
        result["errors"].append("missing")
        return result
    if result["size_bytes"] < required.min_size_bytes:
        result["status"] = "failed"
        result["errors"].append(
            f"size below conservative minimum {required.min_size_bytes} bytes"
        )
    with path.open("rb") as handle:
        prefix = handle.read(512)
    if prefix.lstrip().lower().startswith(b"<html"):
        result["status"] = "failed"
        result["errors"].append("file appears to be an HTML error page")
    try:
        with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
            reader = csv.reader(handle)
            header = next(reader)
        result["column_count"] = len(header)
        if len(header) < required.min_columns:
            result["status"] = "failed"
            result["errors"].append(
                f"column count below expected minimum {required.min_columns}"
            )
    except Exception as exc:
        result["status"] = "failed"
        result["errors"].append(f"could not read CSV header: {exc}")
    return result


def main() -> int:
    results = [validate_file(required) for required in REQUIRED_FILES]
    print(json.dumps(results, indent=2))
    failures = [result for result in results if result["status"] != "ok"]
    if failures:
        print(f"Raw file validation failed for {len(failures)} file(s).")
        return 2
    print("All required CMS PY2026 raw files passed lightweight validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

