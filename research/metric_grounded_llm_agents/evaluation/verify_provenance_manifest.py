#!/usr/bin/env python3
"""Verify every file recorded in a research provenance manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_entries(manifest: dict[str, Any], root: Path) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for entry in manifest.get("files", []):
        relative_path = str(entry["path"])
        path = root / relative_path
        if not path.is_file():
            results.append({"path": relative_path, "status": "missing"})
            continue

        expected_bytes = int(entry["bytes"])
        if path.stat().st_size != expected_bytes:
            results.append({"path": relative_path, "status": "size-mismatch"})
            continue

        if sha256_file(path) != entry["sha256"]:
            results.append({"path": relative_path, "status": "sha256-mismatch"})
            continue

        results.append({"path": relative_path, "status": "ok"})
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root used to resolve paths in the manifest.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    results = verify_entries(manifest, args.root)

    failures = [result for result in results if result["status"] != "ok"]
    for result in failures:
        print(f"{result['status']}: {result['path']}")
    print(
        f"Checked {len(results)} files: "
        f"{len(results) - len(failures)} ok, {len(failures)} mismatch or missing."
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
