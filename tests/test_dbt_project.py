from __future__ import annotations

from pathlib import Path

import yaml


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


def test_county_fips_seed_and_model_preserve_leading_zeros() -> None:
    project = yaml.safe_load(Path("dbt_project/dbt_project.yml").read_text())
    column_types = project["seeds"]["aca_marketplace_analytics"][
        "county_fips_reference"
    ]["+column_types"]
    assert column_types == {
        "state_fips": "varchar",
        "county_fips": "varchar",
        "full_fips": "varchar",
    }

    model = Path("dbt_project/models/marts/dim_geography.sql").read_text()
    assert "lpad(trim(cast(full_fips as varchar)), 5, '0')" in model
    assert "coalesce(counties.full_fips, base.county_name) as county_fips" in model
    assert "regexp_full_match(trim(base.county_name), '[0-9]{4,5}')" in model
    assert "regexp_full_match(trim(base.county_name), '[0-9]{1,3}')" in model


def test_dim_geography_matches_full_and_county_fips_without_duplicate_rows() -> None:
    import duckdb

    model_path = Path("dbt_project/models/marts/dim_geography.sql")
    model_sql = model_path.read_text()
    for relation in (
        "county_fips_reference",
        "stg_service_area_puf",
        "stg_rate_puf",
    ):
        model_sql = model_sql.replace(f"{{{{ ref('{relation}') }}}}", relation)

    with duckdb.connect(":memory:") as connection:
        connection.execute(
            """
            create table county_fips_reference (
                state_code varchar,
                state_name varchar,
                state_fips varchar,
                county_fips varchar,
                full_fips varchar,
                county_name varchar,
                county_display_name varchar
            )
            """
        )
        connection.execute(
            """
            insert into county_fips_reference values
                ('IA', 'Iowa', '19', '107', '19107', 'Keokuk County', 'Keokuk'),
                ('IA', 'Iowa', '19', '191', '19191', 'Winneshiek County', 'Winneshiek'),
                ('AL', 'Alabama', '01', '001', '01001', 'Autauga County', 'Autauga')
            """
        )
        connection.execute(
            """
            create table stg_service_area_puf (
                business_year integer,
                state_code varchar,
                service_area_id varchar,
                service_area_name varchar,
                county_name varchar,
                covers_entire_state varchar,
                partial_county varchar,
                zip_codes varchar
            )
            """
        )
        connection.execute(
            """
            insert into stg_service_area_puf values
                (2026, 'IA', 'S1', 'Full FIPS', '19107', 'No', 'No', null),
                (2026, 'IA', 'S2', 'County FIPS', '107', 'No', 'No', null),
                (2026, 'AL', 'S3', 'Leading Zero', '01001', 'No', 'No', null)
            """
        )
        connection.execute(
            """
            create table stg_rate_puf (
                business_year integer,
                state_code varchar,
                rating_area_id varchar
            )
            """
        )
        result = connection.execute(model_sql)
        columns = [column[0] for column in result.description]
        rows = result.fetchall()

    records = [dict(zip(columns, row, strict=True)) for row in rows]
    assert len(records) == 3
    assert {record["county_fips"] for record in records} == {"01001", "19107"}
    assert {record["county_display_name"] for record in records} == {
        "Autauga",
        "Keokuk",
    }
    assert len({record["geography_key"] for record in records}) == 3


def test_exposures_link_dashboard_to_marts() -> None:
    exposures = Path("dbt_project/models/exposures.yml").read_text()
    assert "marketplace_intelligence_dashboard" in exposures
    assert "fact_premium" in exposures
    assert "dim_geography" in exposures
