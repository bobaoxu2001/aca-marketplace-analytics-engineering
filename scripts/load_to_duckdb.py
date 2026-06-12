#!/usr/bin/env python3
"""Load CMS PY2026 Marketplace PUF CSVs into a local DuckDB database."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import duckdb


DEFAULT_RAW_DIR = Path("data/raw/py2026")
DEFAULT_DATABASE_PATH = Path("data/processed/aca_marketplace_py2026.duckdb")


@dataclass(frozen=True)
class RawTable:
    table_name: str
    filename: str
    description: str


RAW_TABLES: tuple[RawTable, ...] = (
    RawTable("rate_puf_py2026", "rate_puf_py2026.csv", "CMS Rate PUF"),
    RawTable(
        "plan_attributes_puf_py2026",
        "plan_attributes_puf_py2026.csv",
        "CMS Plan Attributes PUF",
    ),
    RawTable(
        "benefits_cost_sharing_puf_py2026",
        "benefits_cost_sharing_puf_py2026.csv",
        "CMS Benefits and Cost Sharing PUF",
    ),
    RawTable("service_area_puf_py2026", "service_area_puf_py2026.csv", "CMS Service Area PUF"),
)


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def load_table(connection: duckdb.DuckDBPyConnection, raw_dir: Path, raw_table: RawTable) -> int:
    path = raw_dir / raw_table.filename
    if not path.exists():
        raise FileNotFoundError(f"Missing required raw file: {path}")

    table_identifier = quote_identifier(raw_table.table_name)
    connection.execute(f"drop table if exists {table_identifier}")
    connection.execute(
        f"""
        create table {table_identifier} as
        select *
        from read_csv_auto(
            ?,
            header = true,
            all_varchar = true,
            ignore_errors = true,
            union_by_name = true,
            sample_size = 20000
        )
        """,
        [str(path)],
    )
    row_count = connection.execute(f"select count(*) from {table_identifier}").fetchone()[0]
    connection.execute(
        """
        insert into raw_load_audit (
            table_name,
            source_file,
            description,
            row_count,
            loaded_at_utc
        )
        values (?, ?, ?, ?, current_timestamp)
        """,
        [raw_table.table_name, str(path), raw_table.description, row_count],
    )
    return int(row_count)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.database.parent.mkdir(parents=True, exist_ok=True)
    missing = [table.filename for table in RAW_TABLES if not (args.raw_dir / table.filename).exists()]
    if missing:
        print("Missing raw files:")
        for filename in missing:
            print(f"  - {args.raw_dir / filename}")
        print("Run scripts/download_cms_pufs.py or place files manually before loading.")
        return 2

    with duckdb.connect(str(args.database)) as connection:
        connection.execute(
            """
            create or replace table raw_load_audit (
                table_name varchar,
                source_file varchar,
                description varchar,
                row_count bigint,
                loaded_at_utc timestamp
            )
            """
        )
        for raw_table in RAW_TABLES:
            row_count = load_table(connection, args.raw_dir, raw_table)
            print(f"Loaded {raw_table.table_name}: {row_count:,} rows")

    print(f"DuckDB database ready: {args.database}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
