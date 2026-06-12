#!/usr/bin/env python3
"""Download CMS ACA Marketplace Public Use Files for plan year 2026.

The script first searches public CMS/Data.HealthCare.gov metadata endpoints for
CSV or ZIP resources. If discovery cannot find a dependable file URL, it exits
with manual fallback instructions instead of silently creating partial data.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory


DEFAULT_RAW_DIR = Path("data/raw/py2026")
TIMEOUT_SECONDS = 60
USER_AGENT = "aca-marketplace-analytics-engineering/1.0"


@dataclass(frozen=True)
class PufDataset:
    key: str
    label: str
    filename: str
    search_terms: tuple[str, ...]


DATASETS: tuple[PufDataset, ...] = (
    PufDataset(
        key="rate",
        label="Rate PUF - PY2026",
        filename="rate_puf_py2026.csv",
        search_terms=("2026", "rate", "puf"),
    ),
    PufDataset(
        key="plan_attributes",
        label="Plan Attributes PUF - PY2026",
        filename="plan_attributes_puf_py2026.csv",
        search_terms=("2026", "plan", "attributes", "puf"),
    ),
    PufDataset(
        key="benefits_cost_sharing",
        label="Benefits and Cost Sharing PUF - PY2026",
        filename="benefits_cost_sharing_puf_py2026.csv",
        search_terms=("2026", "benefits", "cost", "sharing", "puf"),
    ),
    PufDataset(
        key="service_area",
        label="Service Area PUF - PY2026",
        filename="service_area_puf_py2026.csv",
        search_terms=("2026", "service", "area", "puf"),
    ),
)


def request_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return response.read()


def request_text(url: str) -> str:
    return request_bytes(url).decode("utf-8", errors="replace")


def normalize_url(url: str) -> str:
    return url.replace("\\/", "/")


def score_candidate(url: str, dataset: PufDataset) -> int:
    lower_url = url.lower()
    if not lower_url.endswith((".csv", ".zip", ".csv.gz")):
        return -1

    score = 0
    for term in dataset.search_terms:
        if term.lower() in lower_url:
            score += 3

    # Prefer direct CSVs, but allow ZIP archives because CMS often publishes PUFs
    # that way.
    if lower_url.endswith(".csv"):
        score += 3
    if "public-use-file" in lower_url or "puf" in lower_url:
        score += 2
    if "2026" in lower_url:
        score += 4
    return score


def extract_urls_from_text(text: str) -> set[str]:
    patterns = (
        r"https?://[^\"'<>\\\s]+?\.(?:csv|zip|csv\.gz)",
        r"https?://[^\"'<>\\\s]+?download[^\"'<>\\\s]*",
    )
    urls: set[str] = set()
    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            urls.add(normalize_url(match).rstrip(").,;"))
    return urls


def discover_from_data_healthcare(dataset: PufDataset) -> set[str]:
    query = urllib.parse.quote_plus(" ".join(dataset.search_terms))
    api_url = f"https://data.healthcare.gov/api/views.json?search={query}"
    urls: set[str] = set()
    try:
        payload = json.loads(request_text(api_url))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"  Data.HealthCare.gov search skipped: {exc}")
        return urls

    for result in payload:
        view_id = result.get("id")
        if not view_id:
            continue
        urls.add(f"https://data.healthcare.gov/resource/{view_id}.csv?$limit=50000000")
        urls.add(f"https://data.healthcare.gov/api/views/{view_id}/rows.csv?accessType=DOWNLOAD")
        try:
            metadata = request_text(f"https://data.healthcare.gov/api/views/{view_id}")
        except (urllib.error.URLError, TimeoutError):
            continue
        urls.update(extract_urls_from_text(metadata))
    return urls


def discover_from_catalog_data_gov(dataset: PufDataset) -> set[str]:
    query = urllib.parse.quote_plus(" ".join(("CMS", "Marketplace", *dataset.search_terms)))
    api_url = f"https://catalog.data.gov/api/3/action/package_search?q={query}&rows=10"
    urls: set[str] = set()
    try:
        payload = json.loads(request_text(api_url))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"  catalog.data.gov search skipped: {exc}")
        return urls

    for package in payload.get("result", {}).get("results", []):
        for resource in package.get("resources", []):
            url = resource.get("url")
            if url:
                urls.add(normalize_url(url))
    return urls


def discover_from_cms_pages(dataset: PufDataset) -> set[str]:
    cms_pages = (
        "https://www.cms.gov/marketplace/resources/data/public-use-files",
        "https://www.cms.gov/cciio/resources/data-resources/marketplace-puf",
    )
    urls: set[str] = set()
    for page in cms_pages:
        try:
            html = request_text(page)
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"  CMS page skipped ({page}): {exc}")
            continue
        urls.update(extract_urls_from_text(html))
    return urls


def discover_candidates(dataset: PufDataset) -> list[str]:
    candidates: set[str] = set()
    candidates.update(discover_from_data_healthcare(dataset))
    candidates.update(discover_from_catalog_data_gov(dataset))
    candidates.update(discover_from_cms_pages(dataset))

    scored = [
        (score_candidate(url, dataset), url)
        for url in candidates
        if score_candidate(url, dataset) >= 0
    ]
    scored.sort(key=lambda item: item[0], reverse=True)
    return [url for _, url in scored]


def save_candidate(url: str, destination: Path, dataset: PufDataset) -> bool:
    print(f"  Trying {url}")
    try:
        content = request_bytes(url)
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"    Download failed: {exc}")
        return False

    lower_url = url.lower()
    if lower_url.endswith(".zip") or content[:4] == b"PK\x03\x04":
        with TemporaryDirectory() as tmpdir:
            archive_path = Path(tmpdir) / "download.zip"
            archive_path.write_bytes(content)
            try:
                with zipfile.ZipFile(archive_path) as archive:
                    csv_members = [
                        member
                        for member in archive.namelist()
                        if member.lower().endswith(".csv")
                        and score_candidate(member, dataset) >= 0
                    ]
                    if not csv_members:
                        csv_members = [
                            member
                            for member in archive.namelist()
                            if member.lower().endswith(".csv")
                        ]
                    if not csv_members:
                        print("    ZIP archive did not contain a CSV file.")
                        return False
                    csv_members.sort(key=lambda member: score_candidate(member, dataset), reverse=True)
                    with archive.open(csv_members[0]) as csv_file:
                        destination.write_bytes(csv_file.read())
            except zipfile.BadZipFile:
                print("    Response was not a readable ZIP archive.")
                return False
    else:
        destination.write_bytes(content)

    if destination.stat().st_size == 0:
        destination.unlink(missing_ok=True)
        print("    Download produced an empty file.")
        return False

    print(f"    Saved {destination} ({destination.stat().st_size:,} bytes)")
    return True


def print_manual_fallback(raw_dir: Path, missing: list[PufDataset]) -> None:
    print("\nAutomatic CMS URL discovery did not complete for every required file.")
    print("Manual data download fallback:")
    print("1. Download the Plan Year 2026 Marketplace PUF CSV files from CMS or Data.HealthCare.gov.")
    print(f"2. Place the files in: {raw_dir}")
    print("3. Rename them exactly as follows:")
    for dataset in missing:
        print(f"   - {dataset.filename}  ({dataset.label})")
    print("4. Re-run this script, then run scripts/profile_raw_data.py and scripts/load_to_duckdb.py.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--force", action="store_true", help="Re-download files even if they exist.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw_dir: Path = args.raw_dir
    raw_dir.mkdir(parents=True, exist_ok=True)

    missing: list[PufDataset] = []
    for dataset in DATASETS:
        destination = raw_dir / dataset.filename
        if destination.exists() and not args.force:
            print(f"Found existing {destination}; skipping download.")
            continue

        print(f"\nDiscovering {dataset.label}...")
        downloaded = False
        for url in discover_candidates(dataset)[:10]:
            if save_candidate(url, destination, dataset):
                downloaded = True
                break
        if not downloaded:
            missing.append(dataset)

    if missing:
        print_manual_fallback(raw_dir, missing)
        return 2

    print("\nAll required PY2026 PUF files are available.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
