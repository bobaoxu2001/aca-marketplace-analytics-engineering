from __future__ import annotations

import json
from pathlib import Path

from scripts.generate_case_study_outputs import dbt_test_pass_label


def test_dbt_test_pass_label_reads_run_results(tmp_path: Path) -> None:
    run_results = {
        "results": [
            {"status": "pass"},
            {"status": "pass"},
            {"status": "error"},
            {"status": "skipped"},
        ]
    }
    path = tmp_path / "run_results.json"
    path.write_text(json.dumps(run_results), encoding="utf-8")
    assert dbt_test_pass_label(path) == "2 passed"


def test_dbt_test_pass_label_missing_file() -> None:
    assert dbt_test_pass_label(Path("missing/run_results.json")) == "run dbt build"
