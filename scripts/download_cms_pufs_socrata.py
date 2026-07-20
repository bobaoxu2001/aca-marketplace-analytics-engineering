#!/usr/bin/env python3
"""Download CMS PY2026 PUFs through official Socrata row APIs when available.

The PY2026 HealthData catalog currently exposes the six required PUFs as
Socrata `href` assets, not tabular SODA datasets. This script still implements a
paginated/resumable SODA downloader and records a machine-readable diagnostic
when a required official view has no row API access.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any

import certifi
import requests
import yaml

CONFIG_PATH = Path("research/metric_grounded_llm_agents/configs/data_sources.yaml")
RESULTS_DIR = Path("research/metric_grounded_llm_agents/evaluation/results")
SOCRATA_REPORT = RESULTS_DIR / "socrata_download_report.json"
FAILURE_REPORT = RESULTS_DIR / "download_failure_report.json"
DEFAULT_LIMIT = 50_000
SOCRATA_DOMAIN = "https://healthdata.gov"
CATALOG_URL = "https://healthdata.gov/data.json"
USER_AGENT = "aca-marketplace-analytics-engineering/1.0 SocrataDownloader"


def load_required_files() -> list[dict[str, Any]]:
    payload = yaml.safe_load(CONFIG_PATH.read_text()) or {}
    return payload.get("required_files", [])


def session() -> requests.Session:
    client = requests.Session()
    client.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "application/json,text/csv,*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    return client


def get_json(client: requests.Session, url: str, params: dict[str, Any] | None = None) -> tuple[dict[str, Any] | list[Any] | None, dict[str, Any]]:
    attempt: dict[str, Any] = {"url": url, "params": params or {}}
    try:
        response = client.get(url, params=params, timeout=(10, 120), verify=certifi.where())
        attempt.update(
            {
                "status_code": response.status_code,
                "final_url": response.url,
                "content_type": response.headers.get("content-type"),
                "content_length": response.headers.get("content-length"),
            }
        )
        if not response.ok:
            attempt["error"] = response.text[:300]
            return None, attempt
        return response.json(), attempt
    except Exception as exc:
        attempt["error"] = repr(exc)
        return None, attempt


def discover_view_id_from_catalog(client: requests.Session, title: str) -> tuple[str | None, dict[str, Any]]:
    payload, attempt = get_json(client, CATALOG_URL)
    if not isinstance(payload, dict):
        return None, attempt
    normalized_title = title.replace("–", "-").lower()
    for dataset in payload.get("dataset", []):
        catalog_title = str(dataset.get("title", "")).replace("–", "-").lower()
        if catalog_title == normalized_title:
            landing = dataset.get("landingPage", "")
            if "/d/" in landing:
                return landing.rstrip("/").split("/")[-1], attempt
    return None, attempt


def metadata_for(client: requests.Session, view_id: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    payload, attempt = get_json(client, f"{SOCRATA_DOMAIN}/api/views/{view_id}")
    return (payload if isinstance(payload, dict) else None), attempt


def count_rows(client: requests.Session, view_id: str) -> tuple[int | None, dict[str, Any]]:
    payload, attempt = get_json(
        client,
        f"{SOCRATA_DOMAIN}/resource/{view_id}.json",
        {"$select": "count(*)"},
    )
    if isinstance(payload, list) and payload:
        first = payload[0]
        for key in ("count", "count_*"):
            if key in first:
                return int(first[key]), attempt
    return None, attempt


def fieldnames_from_metadata(metadata: dict[str, Any]) -> list[str]:
    fields = []
    for column in metadata.get("columns", []):
        field = column.get("fieldName")
        if field and not field.startswith(":"):
            fields.append(field)
    return fields


def progress_path(csv_path: Path) -> Path:
    return csv_path.with_suffix(csv_path.suffix + ".progress.json")


def read_progress(csv_path: Path) -> int:
    path = progress_path(csv_path)
    if not path.exists():
        return 0
    try:
        payload = json.loads(path.read_text())
        return int(payload.get("rows_written", 0))
    except Exception:
        return 0


def write_progress(csv_path: Path, rows_written: int, view_id: str) -> None:
    progress_path(csv_path).write_text(
        json.dumps({"view_id": view_id, "rows_written": rows_written}, indent=2)
    )


def append_rows_to_csv(csv_path: Path, rows: list[dict[str, Any]], fieldnames: list[str], append: bool) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with csv_path.open(mode, newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        if not append:
            writer.writeheader()
        writer.writerows(rows)


def download_tabular_dataset(
    client: requests.Session,
    item: dict[str, Any],
    view_id: str,
    metadata: dict[str, Any],
    limit: int,
    force: bool,
) -> dict[str, Any]:
    csv_path = Path(item["local_filename"])
    if force:
        csv_path.unlink(missing_ok=True)
        progress_path(csv_path).unlink(missing_ok=True)
    fields = fieldnames_from_metadata(metadata)
    if not fields:
        return {"status": "failed", "reason": "metadata_has_no_columns"}
    expected_count, count_attempt = count_rows(client, view_id)
    offset = read_progress(csv_path)
    append = offset > 0 and csv_path.exists()
    attempts = [count_attempt]
    rows_written = offset
    while True:
        payload, attempt = get_json(
            client,
            f"{SOCRATA_DOMAIN}/resource/{view_id}.json",
            {"$limit": limit, "$offset": offset},
        )
        attempts.append(attempt)
        if not isinstance(payload, list):
            return {
                "status": "failed",
                "reason": "page_request_failed",
                "rows_written": rows_written,
                "expected_count": expected_count,
                "attempts": attempts,
            }
        if not payload:
            break
        append_rows_to_csv(csv_path, payload, fields, append=append)
        append = True
        rows_written += len(payload)
        offset += len(payload)
        write_progress(csv_path, rows_written, view_id)
        print(f"  {view_id}: wrote {rows_written:,} rows", flush=True)
        if len(payload) < limit:
            break
        time.sleep(0.2)
    status = "ok" if expected_count is None or rows_written == expected_count else "failed"
    reason = None if status == "ok" else "row_count_mismatch"
    return {
        "status": status,
        "reason": reason,
        "view_id": view_id,
        "rows_written": rows_written,
        "expected_count": expected_count,
        "csv_path": str(csv_path),
        "attempts": attempts,
    }


def run(limit: int, force: bool, only_key: str | None) -> dict[str, Any]:
    client = session()
    results: list[dict[str, Any]] = []
    for item in load_required_files():
        key = Path(item["local_filename"]).stem.replace("_puf_py2026", "")
        if only_key and only_key not in {key, item.get("socrata_view_id")}:
            continue
        title = item["title"]
        view_id = item.get("socrata_view_id")
        catalog_attempt = None
        if not view_id:
            view_id, catalog_attempt = discover_view_id_from_catalog(client, title)
        print(f"\n{title}: Socrata view id {view_id}", flush=True)
        if not view_id:
            results.append(
                {
                    "title": title,
                    "status": "failed",
                    "reason": "no_socrata_view_id_found",
                    "catalog_attempt": catalog_attempt,
                }
            )
            continue
        metadata, metadata_attempt = metadata_for(client, view_id)
        if not metadata:
            results.append(
                {
                    "title": title,
                    "view_id": view_id,
                    "status": "failed",
                    "reason": "metadata_request_failed",
                    "attempts": [metadata_attempt],
                }
            )
            continue
        asset_type = metadata.get("assetType")
        view_type = metadata.get("viewType")
        columns = metadata.get("columns", [])
        if asset_type == "href" or view_type == "href" or not columns:
            probe_payload, probe_attempt = get_json(
                client,
                f"{SOCRATA_DOMAIN}/resource/{view_id}.json",
                {"$limit": 1},
            )
            rows_payload, rows_attempt = get_json(
                client,
                f"{SOCRATA_DOMAIN}/api/views/{view_id}/rows.json",
                {"accessType": "DOWNLOAD", "method": "getByIds", "asHashes": "true", "start": 0, "length": 1},
            )
            results.append(
                {
                    "title": title,
                    "view_id": view_id,
                    "status": "failed",
                    "reason": "official_socrata_view_is_non_tabular_href_asset",
                    "asset_type": asset_type,
                    "view_type": view_type,
                    "column_count": len(columns),
                    "official_csv_url": item.get("official_csv_url"),
                    "attempts": [metadata_attempt, probe_attempt, rows_attempt],
                    "api_probe_payload": probe_payload,
                    "rows_probe_payload": rows_payload,
                }
            )
            continue
        result = download_tabular_dataset(client, item, view_id, metadata, limit, force)
        result.update({"title": title, "view_id": view_id})
        results.append(result)
    status = "ok" if results and all(result["status"] == "ok" for result in results) else "failed"
    return {"status": status, "datasets": results}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--file", help="Optional local stem or Socrata view id to download.")
    parser.add_argument("--report", type=Path, default=SOCRATA_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    report = run(args.limit, args.force, args.file)
    args.report.write_text(json.dumps(report, indent=2))
    if report["status"] != "ok":
        FAILURE_REPORT.write_text(json.dumps(report, indent=2))
        print(f"\nSocrata download failed; report written to {args.report}")
        return 2
    print(f"\nSocrata download completed; report written to {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
