"""Build the NYC 311 second-domain warehouse from downloaded monthly CSVs.

Reproducible companion to the CMS marts. Reads data/raw/nyc311/monthly/*.csv
(download with data/raw/nyc311/download_paginated.sh) and writes a DuckDB file
with a `marts` schema mirroring the CMS fact/dim layout:

  marts.fact_service_request  one row per 311 request, cleaned timestamps,
                              derived response_hours and is_closed
  marts.dim_agency            15 agencies
  marts.dim_complaint         197 complaint types
  marts.dim_borough           5 boroughs with 2020 Census population

Run:  python benchmark/build_nyc311_warehouse.py
"""

from __future__ import annotations

from pathlib import Path

import duckdb

REPO = Path(__file__).resolve().parents[3]
RAW_GLOB = str(REPO / "data/raw/nyc311/monthly/sr_2024_*.csv")
DB_PATH = str(REPO / "data/processed/nyc311_2024.duckdb")

# 2020 US Census resident population by NYC borough (county).
BOROUGH_POPULATION = [
    ("BRONX", 1472654),
    ("BROOKLYN", 2736074),
    ("MANHATTAN", 1694251),
    ("QUEENS", 2405464),
    ("STATEN ISLAND", 495747),
]


def build() -> None:
    con = duckdb.connect(DB_PATH)
    con.execute(
        f"""
        create or replace table raw_service_requests as
        select * from read_csv_auto('{RAW_GLOB}', header=true,
                                     sample_size=-1, union_by_name=true)
        """
    )
    con.execute("create schema if not exists marts")

    con.execute(
        """
        create or replace table marts.fact_service_request as
        select
          unique_key,
          try_cast(created_date as timestamp) as created_at,
          try_cast(closed_date as timestamp)  as closed_at,
          agency, agency_name, complaint_type, descriptor, status,
          upper(trim(borough))                as borough,
          incident_zip, incident_address, open_data_channel_type,
          case when try_cast(closed_date as timestamp) is not null
                 and try_cast(closed_date as timestamp) >= try_cast(created_date as timestamp)
               then date_diff('hour', try_cast(created_date as timestamp),
                                       try_cast(closed_date as timestamp))
          end                                 as response_hours,
          (status = 'Closed')                 as is_closed
        from raw_service_requests
        """
    )
    con.execute(
        """
        create or replace table marts.dim_agency as
        select agency, any_value(agency_name) as agency_name, count(*) as request_rows
        from raw_service_requests group by agency
        """
    )
    con.execute(
        """
        create or replace table marts.dim_complaint as
        select complaint_type, count(distinct descriptor) as descriptor_count,
               count(*) as request_rows
        from raw_service_requests group by complaint_type
        """
    )
    values = ", ".join(f"('{b}', {p})" for b, p in BOROUGH_POPULATION)
    con.execute(
        f"""
        create or replace table marts.dim_borough as
        select * from (values {values}) as t(borough, population_2020)
        """
    )

    for table in ["fact_service_request", "dim_agency", "dim_complaint", "dim_borough"]:
        n = con.execute(f"select count(*) from marts.{table}").fetchone()[0]
        print(f"marts.{table}: {n:,} rows")
    con.close()


if __name__ == "__main__":
    build()
