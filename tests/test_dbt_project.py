from __future__ import annotations

from pathlib import Path


def test_dbt_project_parses() -> None:
    project_file = Path("dbt_project/dbt_project.yml")
    assert project_file.exists()
    text = project_file.read_text()
    assert "aca_marketplace_analytics" in text
    assert "seed-paths" in text


def test_county_fips_seed_is_present() -> None:
    seed_path = Path("dbt_project/seeds/county_fips_reference.csv")
    assert seed_path.exists()
    lines = seed_path.read_text().splitlines()
    assert len(lines) > 3000
    header = lines[0]
    assert "full_fips" in header
    assert "county_display_name" in header


def test_exposures_link_dashboard_to_marts() -> None:
    exposures = Path("dbt_project/models/exposures.yml").read_text()
    assert "marketplace_intelligence_dashboard" in exposures
    assert "fact_premium" in exposures
    assert "dim_geography" in exposures
