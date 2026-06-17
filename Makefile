.PHONY: help venv install download profile load seed build test docs outputs pipeline ci clean

PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin
RAW_DIR := data/raw/py2026
DB_PATH := data/processed/aca_marketplace_py2026.duckdb
DBT_DIR := dbt_project

help:
	@echo "ACA Marketplace Analytics — common targets"
	@echo ""
	@echo "  make install     Create venv and install Python dependencies"
	@echo "  make download    Download CMS PY2026 PUF files"
	@echo "  make profile     Profile raw CSV files with Polars"
	@echo "  make load        Load raw CSVs into DuckDB"
	@echo "  make seed        Load dbt seed data (county FIPS reference)"
	@echo "  make build       Run dbt seed + build (models + tests)"
	@echo "  make docs        Generate dbt documentation"
	@echo "  make outputs     Generate insight snapshot and PNG assets"
	@echo "  make test        Run Python unit tests"
	@echo "  make pipeline    Full end-to-end refresh"
	@echo "  make ci          CI-safe checks (parse + unit tests)"
	@echo "  make clean       Remove build artifacts"

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt

download:
	$(BIN)/python scripts/download_cms_pufs.py

profile:
	$(BIN)/python scripts/profile_raw_data.py

load:
	$(BIN)/python scripts/load_to_duckdb.py

seed:
	cd $(DBT_DIR) && ../$(BIN)/dbt seed --profiles-dir .

build: seed
	cd $(DBT_DIR) && ../$(BIN)/dbt build --profiles-dir .

docs:
	cd $(DBT_DIR) && ../$(BIN)/dbt docs generate --profiles-dir .

outputs:
	$(BIN)/python scripts/generate_case_study_outputs.py

test:
	PYTHONPATH=. $(BIN)/pytest tests/ -q

pipeline: download profile load build outputs

ci:
	cd $(DBT_DIR) && ../$(BIN)/dbt parse --profiles-dir .
	PYTHONPATH=. $(BIN)/pytest tests/ -q

clean:
	rm -rf $(DBT_DIR)/target $(DBT_DIR)/dbt_packages
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
