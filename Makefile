.PHONY: research-gold research-eval research-demo research-test test-research ci-check research-full-run research-github-help

research-gold:
	python3 research/metric_grounded_llm_agents/benchmark/generate_gold_answers.py

research-eval:
	python3 research/metric_grounded_llm_agents/evaluation/run_eval.py

research-demo:
	python3 research/metric_grounded_llm_agents/demo/cli.py --question-id Q001

research-test:
	PYTHONPATH=research/metric_grounded_llm_agents pytest research/metric_grounded_llm_agents/tests

test-research: research-test

ci-check:
	python3 -m compileall -q research scripts
	PYTHONPATH=research/metric_grounded_llm_agents pytest research/metric_grounded_llm_agents/tests
	python3 -c "from pathlib import Path; import yaml; [yaml.safe_load(path.read_text()) for path in list(Path('.github/workflows').glob('*.yml')) + list(Path('research/metric_grounded_llm_agents/configs').glob('*.yaml'))]"
	@if command -v dbt >/dev/null 2>&1; then cd dbt_project && dbt parse --profiles-dir .; else echo 'dbt not installed; skipping optional dbt parse.'; fi

research-full-run:
	python3 scripts/download_cms_pufs.py --debug --force
	python3 scripts/validate_raw_files.py
	python3 scripts/load_to_duckdb.py
	cd dbt_project && dbt build --profiles-dir . && cd ..
	python3 research/metric_grounded_llm_agents/benchmark/generate_gold_answers.py
	python3 research/metric_grounded_llm_agents/evaluation/run_eval.py

research-github-help:
	@printf '%s\n' \
		'GitHub Actions research run:' \
		'1. Push this branch to GitHub.' \
		'2. Trigger the workflow with:' \
		'   gh workflow run metric_grounded_research_run.yml --ref research/github-actions-data-run' \
		'3. Or open GitHub > Actions > Metric-Grounded Research Data Run > Run workflow.' \
		'4. Download artifacts from the completed workflow run.'
