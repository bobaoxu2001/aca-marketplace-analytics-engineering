.PHONY: research-gold research-eval research-eval-r3 research-codex-pilot research-router-eval research-bootstrap research-review-packet research-demo research-test test-research ci-check research-full-run research-github-help

research-gold:
	python3 research/metric_grounded_llm_agents/benchmark/generate_gold_answers.py

research-eval:
	python3 research/metric_grounded_llm_agents/evaluation/run_eval.py

research-eval-r3:
	python3 research/metric_grounded_llm_agents/evaluation/run_eval.py \
		--repeats 3 \
		--experiment-id cms_py2026_three_system_r3 \
		--output-dir research/metric_grounded_llm_agents/evaluation/results/cms_py2026_three_system_r3

research-codex-pilot:
	PYTHONPATH=research/metric_grounded_llm_agents python3 \
		research/metric_grounded_llm_agents/evaluation/run_codex_pilot.py \
		--repeats 3 \
		--experiment-id codex_subscription_batched_r3 \
		--output-dir research/metric_grounded_llm_agents/evaluation/results/codex_subscription_batched_r3

research-router-eval:
	PYTHONPATH=research/metric_grounded_llm_agents python3 \
		research/metric_grounded_llm_agents/evaluation/run_router_eval.py \
		--paraphrases research/metric_grounded_llm_agents/benchmark/paraphrases.json \
		--repeats 3 \
		--output-dir research/metric_grounded_llm_agents/evaluation/results/router_eval_r3

research-bootstrap:
	PYTHONPATH=research/metric_grounded_llm_agents python3 \
		research/metric_grounded_llm_agents/evaluation/bootstrap_intervals.py \
		--codex-results research/metric_grounded_llm_agents/evaluation/results/codex_subscription_batched_r3_final \
		--metric-results research/metric_grounded_llm_agents/evaluation/results/cms_py2026_three_system_r3_final \
		--iterations 10000 \
		--output research/metric_grounded_llm_agents/evaluation/results/bootstrap_intervals_strict.json

research-review-packet:
	PYTHONPATH=research/metric_grounded_llm_agents python3 \
		research/metric_grounded_llm_agents/evaluation/build_human_review_packet.py \
		--codex-results research/metric_grounded_llm_agents/evaluation/results/codex_subscription_batched_r3_final \
		--metric-results research/metric_grounded_llm_agents/evaluation/results/cms_py2026_three_system_r3_final \
		--gold-dir research/metric_grounded_llm_agents/benchmark/gold_answers \
		--output-dir research/metric_grounded_llm_agents/evaluation/human_review_v1

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
		'   gh workflow run metric_grounded_research_run.yml --ref main' \
		'3. Or open GitHub > Actions > Metric-Grounded Research Data Run > Run workflow.' \
		'4. Download artifacts from the completed workflow run.'
