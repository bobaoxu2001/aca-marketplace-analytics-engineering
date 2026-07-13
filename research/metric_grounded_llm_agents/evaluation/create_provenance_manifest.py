#!/usr/bin/env python3
"""Create a hash manifest for a local research snapshot without model calls."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def command(*args: str) -> str | None:
    try:
        return subprocess.run(
            args, cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def version(module_name: str) -> str | None:
    try:
        module = __import__(module_name)
    except ImportError:
        return None
    return str(getattr(module, "__version__", "installed-version-unavailable"))


def selected_files(artifact_dir: Path) -> list[Path]:
    patterns = [
        "data/raw/py2026/*.csv",
        "data/processed/*.duckdb",
        "research/metric_grounded_llm_agents/benchmark/questions.yaml",
        "research/metric_grounded_llm_agents/benchmark/paraphrases.json",
        "research/metric_grounded_llm_agents/benchmark/routing_challenge_v1.json",
        "research/metric_grounded_llm_agents/benchmark/gold_sql/*.sql",
        "research/metric_grounded_llm_agents/configs/*.yaml",
        "research/metric_grounded_llm_agents/agent/*.py",
        "research/metric_grounded_llm_agents/evaluation/*.py",
    ]
    paths: set[Path] = set()
    for pattern in patterns:
        paths.update(path for path in ROOT.glob(pattern) if path.is_file())
    paths.update(
        path for path in artifact_dir.glob("*.json")
        if path.name != "provenance_manifest.json"
    )
    return sorted(paths)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    artifact_dir = output.parent
    files = []
    for path in selected_files(artifact_dir):
        files.append({
            "path": str(path.relative_to(ROOT)),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    status = command("git", "status", "--porcelain")
    payload = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "application-package strict rescore provenance; no model calls",
        "git": {
            "commit": command("git", "rev-parse", "HEAD"),
            "branch": command("git", "branch", "--show-current"),
            "dirty": bool(status),
            "status_porcelain": status.splitlines() if status else [],
        },
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "duckdb": version("duckdb"),
            "dbt": command(str(Path(sys.executable).with_name("dbt")), "--version"),
            "codex": command("codex", "--version"),
        },
        "limitations": [
            "Underlying subscription-Codex calls predate this source freeze.",
            "Model-generated challenge questions are not independently human validated.",
            "Gold SQL awaits a second independent reviewer.",
            "Human qualitative review is pending.",
        ],
        "files": files,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Wrote {len(files)} hashes to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
