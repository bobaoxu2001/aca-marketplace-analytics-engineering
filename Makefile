.PHONY: help venv install download validate-raw profile load seed deps build test docs outputs pipeline pipeline-full lint validate ci ci-check clean research-gold research-eval research-eval-r3 research-codex-pilot research-router-eval research-bootstrap research-review-packet research-demo research-test test-research research-full-run research-github-help

PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin
DBT := $(BIN)/dbt
PYTEST := $(BIN)/pytest
RAW_DIR := data/raw/py2026
DB_PATH := data/processed/aca_marketplace_py2026.duckdb
DBT_DIR := dbt_project
RESEARCH_ROOT := research/metric_grounded_llm_agents

help:
	@echo "ACA Marketplace Analytics — common targets"
	@echo ""
	@echo "  make install        Create venv and install Python dependencies"
	@echo "  make download       Download CMS PY2026 PUF files"
	@echo "  make validate-raw   Validate all six local CMS raw files"
	@echo "  make profile        Profile raw CSV files with Polars"
	@echo "  make load           Load raw CSVs into DuckDB"
	@echo "  make deps           Install dbt packages"
	@echo "  make seed           Load dbt seed data (county FIPS reference)"
	@echo "  make build          Run dbt seed + build (models + tests)"
	@echo "  make docs           Generate dbt documentation"
	@echo "  make outputs        Generate insight snapshot and PNG assets"
	@echo "  make test           Run analytics-engineering Python tests"
	@echo "  make research-test  Run metric-grounded-agent tests"
	@echo "  make lint           Run ruff linter"
	@echo "  make ci-check       Run the full offline CI validation gate"
	@echo "  make pipeline       Full end-to-end analytics refresh"
	@echo "  make pipeline-full  Pipeline + dbt docs generation"
	@echo "  make clean          Remove generated build artifacts"

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt

download: install
	$(BIN)/python scripts/download_cms_pufs.py

validate-raw: install
	$(BIN)/python scripts/validate_raw_files.py

profile: install
	$(BIN)/python scripts/profile_raw_data.py

load: install
	$(BIN)/python scripts/load_to_duckdb.py

deps: install
	cd $(DBT_DIR) && ../$(DBT) deps --profiles-dir .

seed: install deps
	cd $(DBT_DIR) && ../$(DBT) seed --profiles-dir .

build: seed
	cd $(DBT_DIR) && ../$(DBT) build --profiles-dir .

docs: install deps
	cd $(DBT_DIR) && ../$(DBT) docs generate --profiles-dir .

outputs: install
	$(BIN)/python scripts/generate_case_study_outputs.py

test: install
	PYTHONPATH=. $(PYTEST) tests/ -q

research-test: install
	PYTHONPATH=$(RESEARCH_ROOT) $(PYTEST) $(RESEARCH_ROOT)/tests -q

test-research: research-test

lint: install
	$(BIN)/ruff check scripts tests

ci-check: install deps
	$(BIN)/python -m compileall -q scripts research tests
	$(BIN)/ruff check scripts tests
	PYTHONPATH=.:$(RESEARCH_ROOT) $(PYTEST) tests $(RESEARCH_ROOT)/tests -q
	$(BIN)/python -c "from pathlib import Path; import yaml; [yaml.safe_load(path.read_text()) for path in list(Path('.github/workflows').glob('*.yml')) + list(Path('research/metric_grounded_llm_agents/configs').glob('*.yaml'))]"
	cd $(DBT_DIR) && ../$(DBT) parse --profiles-dir . --no-partial-parse

validate: ci-check

ci: ci-check

pipeline: download validate-raw profile load build outputs

pipeline-full: pipeline docs

research-gold: install
	$(BIN)/python $(RESEARCH_ROOT)/benchmark/generate_gold_answers.py

research-eval: install
	$(BIN)/python $(RESEARCH_ROOT)/evaluation/run_eval.py

research-eval-r3: install
	$(BIN)/python $(RESEARCH_ROOT)/evaluation/run_eval.py \
		--repeats 3 \
		--experiment-id cms_py2026_three_system_r3 \
		--output-dir $(RESEARCH_ROOT)/evaluation/results/cms_py2026_three_system_r3

research-codex-pilot: install
	PYTHONPATH=$(RESEARCH_ROOT) $(BIN)/python \
		$(RESEARCH_ROOT)/evaluation/run_codex_pilot.py \
		--repeats 3 \
		--experiment-id codex_subscription_batched_r3 \
		--output-dir $(RESEARCH_ROOT)/evaluation/results/codex_subscription_batched_r3

research-router-eval: install
	PYTHONPATH=$(RESEARCH_ROOT) $(BIN)/python \
		$(RESEARCH_ROOT)/evaluation/run_router_eval.py \
		--paraphrases $(RESEARCH_ROOT)/benchmark/paraphrases.json \
		--repeats 3 \
		--output-dir $(RESEARCH_ROOT)/evaluation/results/router_eval_r3

research-bootstrap: install
	PYTHONPATH=$(RESEARCH_ROOT) $(BIN)/python \
		$(RESEARCH_ROOT)/evaluation/bootstrap_intervals.py \
		--codex-results $(RESEARCH_ROOT)/evaluation/results/codex_subscription_batched_r3 \
		--metric-results $(RESEARCH_ROOT)/evaluation/results/cms_py2026_three_system_r3 \
		--iterations 10000 \
		--output $(RESEARCH_ROOT)/evaluation/results/bootstrap_intervals_strict.json

research-review-packet: install
	PYTHONPATH=$(RESEARCH_ROOT) $(BIN)/python \
		$(RESEARCH_ROOT)/evaluation/build_human_review_packet.py \
		--codex-results $(RESEARCH_ROOT)/evaluation/results/codex_subscription_batched_r3 \
		--metric-results $(RESEARCH_ROOT)/evaluation/results/cms_py2026_three_system_r3 \
		--gold-dir $(RESEARCH_ROOT)/benchmark/gold_answers \
		--output-dir $(RESEARCH_ROOT)/evaluation/human_review_v1

research-demo: install
	$(BIN)/python $(RESEARCH_ROOT)/demo/cli.py --question-id Q001

research-full-run: install
	$(BIN)/python scripts/download_cms_pufs.py --debug --force
	$(BIN)/python scripts/validate_raw_files.py
	$(BIN)/python scripts/load_to_duckdb.py
	cd $(DBT_DIR) && ../$(DBT) deps --profiles-dir . && ../$(DBT) build --profiles-dir .
	$(BIN)/python $(RESEARCH_ROOT)/benchmark/generate_gold_answers.py
	$(BIN)/python $(RESEARCH_ROOT)/evaluation/run_eval.py

research-github-help:
	@printf '%s\n' \
		'GitHub Actions research run:' \
		'1. Push this branch to GitHub.' \
		'2. Trigger the workflow with:' \
		'   gh workflow run metric_grounded_research_run.yml --ref main' \
		'3. Or open GitHub > Actions > Metric-Grounded Research Data Run > Run workflow.' \
		'4. Download artifacts from the completed workflow run.'

clean:
	rm -rf $(DBT_DIR)/target $(DBT_DIR)/dbt_packages
	rm -rf .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
