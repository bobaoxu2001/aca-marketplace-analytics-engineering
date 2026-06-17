from __future__ import annotations

import json
from pathlib import Path

from scripts.load_to_duckdb import load_profile_row_counts


def test_load_profile_row_counts_reads_dataset_keys(tmp_path: Path) -> None:
    profile = {
        "datasets": [
            {"dataset": "rate_puf", "exists": True, "row_count": 10},
            {"dataset": "quality_puf", "exists": False, "row_count": 0},
        ]
    }
    path = tmp_path / "profile.json"
    path.write_text(json.dumps(profile), encoding="utf-8")
    assert load_profile_row_counts(path) == {"rate_puf": 10}
