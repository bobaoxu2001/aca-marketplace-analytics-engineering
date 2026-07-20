from __future__ import annotations

from pathlib import Path

from scripts.load_to_duckdb import RAW_TABLES


def test_raw_tables_cover_all_required_cms_files() -> None:
    expected = {
        "rate_puf_py2026.csv",
        "plan_attributes_puf_py2026.csv",
        "benefits_cost_sharing_puf_py2026.csv",
        "service_area_puf_py2026.csv",
        "plan_id_crosswalk_puf_py2025_py2026.csv",
        "quality_puf_py2026.csv",
    }
    assert {table.filename for table in RAW_TABLES} == expected


def test_raw_table_names_match_dbt_sources() -> None:
    sources_path = Path("dbt_project/models/sources.yml")
    text = sources_path.read_text()
    for table in RAW_TABLES:
        assert table.table_name in text
