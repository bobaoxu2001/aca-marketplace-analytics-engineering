#!/usr/bin/env python3
"""Download CMS ACA Marketplace Public Use Files for plan year 2026.

The downloader only uses official CMS, HealthData/Data.HealthCare.gov, and
Data.gov routes. It tries multiple browser-like strategies before failing and
writes a machine-readable diagnostics report for blocked environments.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from urllib.parse import quote_plus

import certifi
import requests
import yaml


DEFAULT_RAW_DIR = Path("data/raw/py2026")
DATA_SOURCE_CONFIG = Path("research/metric_grounded_llm_agents/configs/data_sources.yaml")
FAILURE_REPORT = Path(
    "research/metric_grounded_llm_agents/evaluation/results/download_failure_report.json"
)
TIMEOUT_SECONDS = 90
MAX_ATTEMPTS_PER_FILE = 80
CHROME_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)
LANDING_PAGES = (
    "https://www.cms.gov/marketplace/resources/data/public-use-files",
    "https://www.cms.gov/cciio/resources/data-resources/marketplace-puf",
    "https://healthdata.gov/",
    "https://data.healthcare.gov/",
    "https://catalog.data.gov/",
)


@dataclass(frozen=True)
class PufDataset:
    key: str
    label: str
    filename: str
    cms_zip_url: str
    datafile_url: str
    search_terms: tuple[str, ...]
    landing_urls: tuple[str, ...]


def headers(referer: str | None = None) -> dict[str, str]:
    result = {
        "User-Agent": CHROME_UA,
        "Accept": "text/csv,application/zip,application/octet-stream,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    if referer:
        result["Referer"] = referer
    return result


def safe_preview(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned[:200]


def dataset_key_from_filename(filename: str) -> str:
    if filename.startswith("rate_"):
        return "rate"
    if filename.startswith("plan_attributes"):
        return "plan_attributes"
    if filename.startswith("benefits"):
        return "benefits_cost_sharing"
    if filename.startswith("service_area"):
        return "service_area"
    if filename.startswith("plan_id_crosswalk"):
        return "plan_id_crosswalk"
    if filename.startswith("quality"):
        return "quality"
    return Path(filename).stem


def search_terms_for(key: str, label: str) -> tuple[str, ...]:
    base = ["2026", "puf"]
    if key == "rate":
        base.append("rate")
    elif key == "plan_attributes":
        base.extend(["plan", "attributes"])
    elif key == "benefits_cost_sharing":
        base.extend(["benefits", "cost", "sharing"])
    elif key == "service_area":
        base.extend(["service", "area"])
    elif key == "plan_id_crosswalk":
        base.extend(["plan", "id", "crosswalk"])
    elif key == "quality":
        base.append("quality")
    else:
        base.extend(label.lower().replace("-", " ").split())
    return tuple(dict.fromkeys(base))


def load_datasets() -> list[PufDataset]:
    if not DATA_SOURCE_CONFIG.exists():
        raise FileNotFoundError(f"Missing source config: {DATA_SOURCE_CONFIG}")
    payload = yaml.safe_load(DATA_SOURCE_CONFIG.read_text()) or {}
    datasets: list[PufDataset] = []
    for item in payload.get("required_files", []):
        filename = Path(item["local_filename"]).name
        key = dataset_key_from_filename(filename)
        title = item["title"]
        landing_slug = re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-")
        landing_urls = (
            f"https://healthdata.gov/CMS/{landing_slug}/{item.get('healthdata_view_id', '')}".rstrip("/"),
            str(item.get("landing_url", "")),
        )
        datasets.append(
            PufDataset(
                key=key,
                label=title,
                filename=filename,
                cms_zip_url=item["cms_zip_url"],
                datafile_url=item["official_csv_url"],
                search_terms=search_terms_for(key, title),
                landing_urls=tuple(url for url in landing_urls if url.startswith("http")),
            )
        )
    return datasets


def score_candidate(url: str, dataset: PufDataset) -> int:
    lower_url = url.lower()
    if not lower_url.startswith("https://"):
        return -1
    if not any(domain in lower_url for domain in OFFICIAL_DOMAINS):
        return -1
    if not re.search(r"(\.csv|\.zip|export\.csv|rows\.csv|datafile)", lower_url):
        return -1
    if "2026" not in lower_url and "py2026" not in lower_url:
        return -1
    specific_terms = [term for term in dataset.search_terms if term not in {"2026", "puf"}]
    if specific_terms and not any(term.lower() in lower_url for term in specific_terms):
        return -1
    score = 0
    for term in dataset.search_terms:
        if term.lower() in lower_url:
            score += 3
    if lower_url.endswith(".csv") or "datafile" in lower_url:
        score += 4
    if lower_url.endswith(".zip"):
        score += 2
    if "2026" in lower_url or "py2026" in lower_url:
        score += 5
    if "quality" in lower_url and dataset.key == "quality":
        score += 5
    return score


OFFICIAL_DOMAINS = (
    "cms.gov",
    "download.cms.gov",
    "data.healthcare.gov",
    "healthdata.gov",
    "catalog.data.gov",
)


def extract_urls(text: str) -> set[str]:
    urls: set[str] = set()
    for match in re.findall(r"https?://[^\"'<>\\\s]+", text, flags=re.IGNORECASE):
        url = match.replace("\\/", "/").rstrip(").,;")
        if any(domain in url.lower() for domain in OFFICIAL_DOMAINS):
            urls.add(url)
    return urls


def note_attempt(
    diagnostics: list[dict[str, Any]],
    dataset: PufDataset,
    method: str,
    url: str,
    *,
    status_code: int | None = None,
    final_url: str | None = None,
    content_type: str | None = None,
    content_length: str | int | None = None,
    error: str | None = None,
    preview: str | None = None,
) -> None:
    diagnostics.append(
        {
            "dataset": dataset.key,
            "label": dataset.label,
            "method": method,
            "url": url,
            "status_code": status_code,
            "final_url": final_url,
            "content_type": content_type,
            "content_length": content_length,
            "error": error,
            "preview": preview,
        }
    )


def debug_attempt(entry: dict[str, Any]) -> None:
    parts = [
        f"method={entry['method']}",
        f"status={entry.get('status_code')}",
        f"type={entry.get('content_type')}",
        f"length={entry.get('content_length')}",
        f"final={entry.get('final_url')}",
    ]
    if entry.get("error"):
        parts.append(f"error={entry['error']}")
    print("    " + " | ".join(parts))
    if entry.get("preview"):
        print(f"    preview={entry['preview']}")


def warm_session(session: requests.Session, debug: bool, diagnostics: list[dict[str, Any]]) -> None:
    for page in LANDING_PAGES:
        try:
            response = session.get(page, headers=headers(), timeout=30, allow_redirects=True)
            if debug:
                print(f"  Warmed {page}: {response.status_code}")
            diagnostics.append(
                {
                    "dataset": "_session",
                    "label": "session warmup",
                    "method": "requests_warmup",
                    "url": page,
                    "status_code": response.status_code,
                    "final_url": response.url,
                    "content_type": response.headers.get("content-type"),
                    "content_length": response.headers.get("content-length"),
                    "error": None if response.ok else response.reason,
                    "preview": None if response.ok else safe_preview(response.text),
                }
            )
        except requests.RequestException as exc:
            diagnostics.append(
                {
                    "dataset": "_session",
                    "label": "session warmup",
                    "method": "requests_warmup",
                    "url": page,
                    "status_code": None,
                    "final_url": None,
                    "content_type": None,
                    "content_length": None,
                    "error": repr(exc),
                    "preview": None,
                }
            )


def discover_healthdata_data_json(session: requests.Session) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    try:
        response = session.get(
            "https://healthdata.gov/data.json",
            headers=headers("https://healthdata.gov/"),
            timeout=45,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        return mapping
    for dataset in payload.get("dataset", []):
        title = dataset.get("title", "")
        urls: list[str] = []
        for distribution in dataset.get("distribution", []):
            for field in ("downloadURL", "accessURL"):
                if distribution.get(field):
                    urls.append(distribution[field])
        if title and urls:
            mapping[title.lower()] = urls
    return mapping


def discover_catalog_data_gov(session: requests.Session, dataset: PufDataset) -> set[str]:
    query = quote_plus(" ".join(("CMS", "Marketplace", *dataset.search_terms)))
    urls: set[str] = set()
    endpoints = (
        f"https://catalog.data.gov/api/3/action/package_search?q={query}&rows=20",
        f"https://catalog.data.gov/dataset/?q={query}",
    )
    for endpoint in endpoints:
        try:
            response = session.get(endpoint, headers=headers("https://catalog.data.gov/"), timeout=(8, 10))
            if response.headers.get("content-type", "").startswith("application/json"):
                payload = response.json()
                for package in payload.get("result", {}).get("results", []):
                    for resource in package.get("resources", []):
                        if resource.get("url"):
                            urls.add(resource["url"])
                        if resource.get("downloadURL"):
                            urls.add(resource["downloadURL"])
            else:
                urls.update(extract_urls(response.text))
        except (requests.RequestException, ValueError):
            continue
    return urls


def discover_data_healthcare_api(session: requests.Session, dataset: PufDataset) -> set[str]:
    urls: set[str] = set()
    domains = ("https://healthdata.gov", "https://data.healthcare.gov")
    query = quote_plus(" ".join(dataset.search_terms))
    for domain in domains:
        for endpoint in (
            f"{domain}/api/views.json?search={query}",
            f"{domain}/api/catalog/v1?search_context=healthdata.gov&search={query}&limit=20",
        ):
            try:
                response = session.get(endpoint, headers=headers(domain), timeout=(8, 10))
                if not response.ok:
                    continue
                payload = response.json()
            except (requests.RequestException, ValueError):
                continue
            views = payload if isinstance(payload, list) else payload.get("results", [])
            for result in views:
                view_id = result.get("id") or result.get("resource", {}).get("id")
                if not view_id:
                    continue
                for base in domains:
                    urls.add(f"{base}/resource/{view_id}.csv?$limit=50000000")
                    urls.add(f"{base}/api/v3/views/{view_id}/export.csv")
                    urls.add(f"{base}/api/views/{view_id}/rows.csv?accessType=DOWNLOAD")
                try:
                    metadata = session.get(
                        f"{domain}/api/views/{view_id}",
                        headers=headers(domain),
                        timeout=(8, 10),
                    )
                    if metadata.ok:
                        urls.update(extract_urls(metadata.text))
                except requests.RequestException:
                    pass
    return urls


def discover_page_urls(session: requests.Session, dataset: PufDataset) -> set[str]:
    urls: set[str] = set()
    pages = (*LANDING_PAGES, *dataset.landing_urls)
    for page in pages:
        try:
            response = session.get(page, headers=headers(), timeout=(8, 10))
            if response.ok:
                urls.update(extract_urls(response.text))
        except requests.RequestException:
            continue
    return urls


def candidate_urls(session: requests.Session, dataset: PufDataset) -> list[str]:
    candidates: set[str] = {dataset.datafile_url, dataset.cms_zip_url}
    healthdata_map = discover_healthdata_data_json(session)
    label_lower = dataset.label.lower().replace("–", "-")
    for title, urls in healthdata_map.items():
        title_norm = title.replace("–", "-")
        specific_terms = [term for term in dataset.search_terms if term not in {"2026", "puf"}]
        if label_lower == title_norm or all(term.lower() in title_norm for term in specific_terms):
            candidates.update(urls)
    candidates.update(discover_catalog_data_gov(session, dataset))
    candidates.update(discover_data_healthcare_api(session, dataset))
    candidates.update(discover_page_urls(session, dataset))
    scored = [(score_candidate(url, dataset), url) for url in candidates]
    return [url for score, url in sorted(scored, reverse=True) if score >= 0][:MAX_ATTEMPTS_PER_FILE]


def is_probably_download(response: requests.Response, url: str) -> bool:
    content_type = response.headers.get("content-type", "").lower()
    lowered = url.lower()
    if response.status_code != 200:
        return False
    if "text/html" in content_type:
        return False
    if any(token in content_type for token in ("text/csv", "application/zip", "application/octet-stream", "application/vnd.ms-excel")):
        return True
    return lowered.endswith((".csv", ".zip", ".csv.gz")) or "datafile" in lowered


def extract_or_move_download(path: Path, destination: Path, dataset: PufDataset) -> bool:
    if path.stat().st_size <= 0:
        return False
    head = path.read_bytes()[:4]
    if path.suffix.lower() == ".zip" or head == b"PK\x03\x04":
        with zipfile.ZipFile(path) as archive:
            members = [member for member in archive.namelist() if member.lower().endswith(".csv")]
            if not members:
                return False
            members.sort(key=lambda member: score_candidate(member, dataset), reverse=True)
            with archive.open(members[0]) as source, destination.open("wb") as target:
                shutil.copyfileobj(source, target)
        return destination.exists() and destination.stat().st_size > 0
    destination.write_bytes(path.read_bytes())
    return destination.exists() and destination.stat().st_size > 0


def download_with_requests(
    session: requests.Session,
    dataset: PufDataset,
    url: str,
    destination: Path,
    diagnostics: list[dict[str, Any]],
    *,
    referer: str | None,
    debug: bool,
) -> bool:
    method = "requests_session"
    partial = destination.with_suffix(destination.suffix + ".part")
    request_headers = headers(referer)
    if partial.exists():
        request_headers["Range"] = f"bytes={partial.stat().st_size}-"
    try:
        response = session.get(
            url,
            headers=request_headers,
            stream=True,
            timeout=(15, TIMEOUT_SECONDS),
            allow_redirects=True,
            verify=certifi.where(),
        )
        body_preview = None
        if not is_probably_download(response, url):
            try:
                body_preview = safe_preview(response.text)
            except Exception:
                body_preview = None
            note_attempt(
                diagnostics,
                dataset,
                method,
                url,
                status_code=response.status_code,
                final_url=response.url,
                content_type=response.headers.get("content-type"),
                content_length=response.headers.get("content-length"),
                error=response.reason,
                preview=body_preview,
            )
            if debug:
                debug_attempt(diagnostics[-1])
            return False
        mode = "ab" if request_headers.get("Range") and response.status_code == 206 else "wb"
        with partial.open(mode) as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
        with TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / ("download.zip" if url.lower().endswith(".zip") else "download.csv")
            shutil.copyfile(partial, tmp_path)
            ok = extract_or_move_download(tmp_path, destination, dataset)
        note_attempt(
            diagnostics,
            dataset,
            method,
            url,
            status_code=response.status_code,
            final_url=response.url,
            content_type=response.headers.get("content-type"),
            content_length=response.headers.get("content-length") or destination.stat().st_size,
            error=None if ok else "downloaded payload could not be extracted",
        )
        if ok:
            partial.unlink(missing_ok=True)
        if debug:
            debug_attempt(diagnostics[-1])
        return ok
    except (requests.RequestException, OSError, zipfile.BadZipFile) as exc:
        note_attempt(diagnostics, dataset, method, url, error=repr(exc))
        if debug:
            debug_attempt(diagnostics[-1])
        return False


def curl_headers(referer: str | None) -> list[str]:
    result: list[str] = []
    for key, value in headers(referer).items():
        if key == "Accept-Encoding":
            continue
        result.extend(["-H", f"{key}: {value}"])
    return result


def download_with_curl(
    dataset: PufDataset,
    url: str,
    destination: Path,
    diagnostics: list[dict[str, Any]],
    *,
    referer: str | None,
    debug: bool,
) -> bool:
    if not shutil.which("curl"):
        return False
    method = "curl_fallback"
    with TemporaryDirectory() as tmpdir:
        cookie_jar = Path(tmpdir) / "cookies.txt"
        output = Path(tmpdir) / "download.bin"
        for page in LANDING_PAGES:
            subprocess.run(
                [
                    "curl",
                    "-L",
                    "--compressed",
                    "--max-time",
                    "10",
                    "-A",
                    CHROME_UA,
                    "-c",
                    str(cookie_jar),
                    "-o",
                    os.devnull,
                    page,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        command = [
            "curl",
            "-L",
            "--compressed",
            "--fail-with-body",
            "--retry",
            "2",
            "--retry-delay",
            "2",
            "--connect-timeout",
            "30",
            "--max-time",
            "300",
            "-C",
            "-",
            "-A",
            CHROME_UA,
            "-b",
            str(cookie_jar),
            "-c",
            str(cookie_jar),
            *curl_headers(referer),
            "-D",
            str(Path(tmpdir) / "headers.txt"),
            "-o",
            str(output),
            url,
        ]
        proc = subprocess.run(command, capture_output=True, text=True, check=False)
        header_text = (Path(tmpdir) / "headers.txt").read_text(errors="replace") if (Path(tmpdir) / "headers.txt").exists() else ""
        status_matches = re.findall(r"HTTP/\S+\s+(\d+)", header_text)
        status_code = int(status_matches[-1]) if status_matches else None
        content_type = None
        content_length = None
        final_url = None
        for line in header_text.splitlines():
            if line.lower().startswith("content-type:"):
                content_type = line.split(":", 1)[1].strip()
            if line.lower().startswith("content-length:"):
                content_length = line.split(":", 1)[1].strip()
            if line.lower().startswith("location:"):
                final_url = line.split(":", 1)[1].strip()
        ok = False
        error = None
        preview = None
        if proc.returncode == 0 and output.exists():
            try:
                ok = extract_or_move_download(output, destination, dataset)
                if not ok:
                    error = "downloaded payload could not be extracted"
            except (OSError, zipfile.BadZipFile) as exc:
                error = repr(exc)
        else:
            error = proc.stderr.strip() or proc.stdout.strip() or f"curl exited {proc.returncode}"
            if output.exists():
                preview = safe_preview(output.read_text(errors="replace"))
        note_attempt(
            diagnostics,
            dataset,
            method,
            url,
            status_code=status_code,
            final_url=final_url or url,
            content_type=content_type,
            content_length=content_length or (output.stat().st_size if output.exists() else None),
            error=None if ok else error,
            preview=preview,
        )
        if debug:
            debug_attempt(diagnostics[-1])
        return ok


def download_with_wget(
    dataset: PufDataset,
    url: str,
    destination: Path,
    diagnostics: list[dict[str, Any]],
    *,
    referer: str | None,
    debug: bool,
) -> bool:
    if not shutil.which("wget"):
        return False
    method = "wget_fallback"
    with TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "download.bin"
        command = [
            "wget",
            "--tries=3",
            "--timeout=90",
            "--continue",
            "--server-response",
            "--user-agent",
            CHROME_UA,
            *(["--referer", referer] if referer else []),
            "-O",
            str(output),
            url,
        ]
        proc = subprocess.run(command, capture_output=True, text=True, check=False)
        status_matches = re.findall(r"HTTP/\S+\s+(\d+)", proc.stderr)
        status_code = int(status_matches[-1]) if status_matches else None
        ok = False
        error = None
        if proc.returncode == 0 and output.exists():
            try:
                ok = extract_or_move_download(output, destination, dataset)
            except (OSError, zipfile.BadZipFile) as exc:
                error = repr(exc)
        else:
            error = proc.stderr.strip()[-500:] or f"wget exited {proc.returncode}"
        note_attempt(
            diagnostics,
            dataset,
            method,
            url,
            status_code=status_code,
            final_url=url,
            error=None if ok else error,
        )
        if debug:
            debug_attempt(diagnostics[-1])
        return ok


def referers_for(url: str) -> list[str | None]:
    lowered = url.lower()
    referers: list[str | None] = [None]
    if "data.healthcare.gov" in lowered:
        referers.extend(["https://healthdata.gov/", "https://data.healthcare.gov/"])
    if "healthdata.gov" in lowered:
        referers.append("https://healthdata.gov/")
    if "cms.gov" in lowered:
        referers.append("https://www.cms.gov/marketplace/resources/data/public-use-files")
    if "catalog.data.gov" in lowered:
        referers.append("https://catalog.data.gov/")
    return list(dict.fromkeys(referers))


def download_dataset(
    session: requests.Session,
    dataset: PufDataset,
    raw_dir: Path,
    force: bool,
    file_urls: list[str],
    diagnostics: list[dict[str, Any]],
    debug: bool,
) -> bool:
    destination = raw_dir / dataset.filename
    if destination.exists() and destination.stat().st_size > 0 and not force:
        print(f"Found existing {destination}; skipping download.")
        return True
    if force:
        destination.unlink(missing_ok=True)
        destination.with_suffix(destination.suffix + ".part").unlink(missing_ok=True)

    print(f"\nDownloading {dataset.label} -> {destination}")
    tried = 0
    for url in file_urls:
        print(f"  Trying {url}")
        for referer in referers_for(url):
            tried += 1
            if tried > MAX_ATTEMPTS_PER_FILE:
                break
            if download_with_requests(
                session,
                dataset,
                url,
                destination,
                diagnostics,
                referer=referer,
                debug=debug,
            ):
                print(f"    Saved {destination} ({destination.stat().st_size:,} bytes)")
                return True
            time.sleep(0.4)
            if download_with_curl(
                dataset,
                url,
                destination,
                diagnostics,
                referer=referer,
                debug=debug,
            ):
                print(f"    Saved {destination} ({destination.stat().st_size:,} bytes)")
                return True
            time.sleep(0.4)
            if download_with_wget(
                dataset,
                url,
                destination,
                diagnostics,
                referer=referer,
                debug=debug,
            ):
                print(f"    Saved {destination} ({destination.stat().st_size:,} bytes)")
                return True
        if tried > MAX_ATTEMPTS_PER_FILE:
            break
    print(f"  Failed to download {dataset.label}; attempted {tried} strategies.")
    return False


def write_failure_report(path: Path, diagnostics: list[dict[str, Any]], missing: list[PufDataset]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "failed",
        "missing_files": [
            {"key": dataset.key, "label": dataset.label, "filename": dataset.filename}
            for dataset in missing
        ],
        "attempts": diagnostics,
    }
    path.write_text(json.dumps(payload, indent=2))
    print(f"\nWrote download diagnostics: {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--force", action="store_true", help="Re-download files even if they exist.")
    parser.add_argument("--debug", action="store_true", help="Print HTTP diagnostics for every attempt.")
    parser.add_argument("--file", choices=[dataset.key for dataset in load_datasets()], help="Download one dataset key.")
    parser.add_argument("--failure-report", type=Path, default=FAILURE_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    datasets = load_datasets()
    if args.file:
        datasets = [dataset for dataset in datasets if dataset.key == args.file]
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    diagnostics: list[dict[str, Any]] = []

    session = requests.Session()
    session.headers.update(headers())
    warm_session(session, args.debug, diagnostics)

    missing: list[PufDataset] = []
    for dataset in datasets:
        urls = candidate_urls(session, dataset)
        print(f"\nDiscovered {len(urls)} official candidate URLs for {dataset.key}.")
        if args.debug:
            for url in urls:
                print(f"    candidate={url}")
        if not download_dataset(
            session,
            dataset,
            args.raw_dir,
            args.force,
            urls,
            diagnostics,
            args.debug,
        ):
            missing.append(dataset)

    if missing:
        write_failure_report(args.failure_report, diagnostics, missing)
        print("\nAutomatic official download did not complete for every required file.")
        for dataset in missing:
            print(f"  - {dataset.filename} ({dataset.label})")
        return 2

    print("\nAll required PY2026 PUF files are available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
