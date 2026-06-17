.PHONY: help venv install download profile load seed deps build test docs outputs pipeline pipeline-full lint validate ci clean

PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin
DBT := $(BIN)/dbt
PYTEST := $(BIN)/pytest
RAW_DIR := data/raw/py2026
DB_PATH := data/processed/aca_marketplace_py2026.duckdb
DBT_DIR := dbt_project

help:
	@echo "ACA Marketplace Analytics — common targets"
	@echo ""
	@echo "  make install        Create venv and install Python dependencies"
	@echo "  make download       Download CMS PY2026 PUF files"
	@echo "  make profile        Profile raw CSV files with Polars"
	@echo "  make load           Load raw CSVs into DuckDB"
	@echo "  make deps           Install dbt packages"
	@echo "  make seed           Load dbt seed data (county FIPS reference)"
	@echo "  make build          Run dbt seed + build (models + tests)"
	@echo "  make docs           Generate dbt documentation"
	@echo "  make outputs        Generate insight snapshot and PNG assets"
	@echo "  make test           Run Python unit tests"
	@echo "  make lint           Run ruff linter"
	@echo "  make pipeline       Full end-to-end refresh"
	@echo "  make pipeline-full  Pipeline + dbt docs generation"
	@echo "  make validate       Lint + CI checks"
	@echo "  make ci             CI-safe checks (parse + unit tests)"
	@echo "  make clean          Remove build artifacts"

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt

download: install
	$(BIN)/python scripts/download_cms_pufs.py

profile: install
	$(BIN)/python scripts/profile_raw_data.py

load: install
	$(BIN)/python scripts/load_to_duckdb.py

deps: install
	cd $(DBT_DIR) && ../$(BIN)/dbt deps --profiles-dir .

seed: install deps
	cd $(DBT_DIR) && ../$(BIN)/dbt seed --profiles-dir .

build: seed
	cd $(DBT_DIR) && ../$(BIN)/dbt build --profiles-dir .

docs: install deps
	cd $(DBT_DIR) && ../$(BIN)/dbt docs generate --profiles-dir .

outputs: install
	$(BIN)/python scripts/generate_case_study_outputs.py

test: install
	PYTHONPATH=. $(PYTEST) tests/ -q

lint: install
	$(BIN)/ruff check scripts tests

pipeline: download profile load build outputs

pipeline-full: pipeline docs

validate: lint ci

ci: install deps
	cd $(DBT_DIR) && ../$(BIN)/dbt parse --profiles-dir .
	PYTHONPATH=. $(PYTEST) tests/ -q

clean:
	rm -rf $(DBT_DIR)/target $(DBT_DIR)/dbt_packages
	rm -rf .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
