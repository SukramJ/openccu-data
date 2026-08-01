# Makefile for openccu-data.
#
# Thin wrappers around the existing script/ helpers and the standard dev
# tools. Every target runs through script/run-in-env.sh, which activates the
# project virtualenv (venv/ or .venv/) if one exists — so `make test` works
# without sourcing the environment first.

RUN := script/run-in-env.sh

.DEFAULT_GOAL := help

.PHONY: help setup install test coverage lint format typecheck prek check \
	extract-easymodes extract-translations extract-profiles extract clean

help:  ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make <target>\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup:  ## Install dev dependencies and prek hooks (script/setup)
	script/setup

install:  ## Editable install including test extras
	$(RUN) python -m pip install -e .[test]

test:  ## Run the pytest suite
	$(RUN) pytest tests/

coverage:  ## Run the tests with a coverage report
	$(RUN) pytest tests/ --cov --cov-report=term-missing

lint:  ## Lint with ruff
	$(RUN) ruff check openccu_data/ tests/ script/

format:  ## Auto-format with ruff
	$(RUN) ruff format openccu_data/ tests/ script/

typecheck:  ## Type-check with mypy
	$(RUN) mypy

prek:  ## Run all prek (pre-commit) hooks on the whole tree
	$(RUN) prek run --all-files

check: lint typecheck test  ## lint + typecheck + test

extract-easymodes:  ## Regenerate easymode_extract.json.gz (reads OCCU_PATH/CCU_URL)
	$(RUN) python script/extract_easymodes.py

extract-translations:  ## Regenerate translation_extract.json.gz (reads OCCU_PATH/CCU_URL)
	$(RUN) python script/extract_translations.py

extract-profiles:  ## Regenerate profiles/*.json.gz (reads CCU_URL/OCCU_PATH)
	$(RUN) python script/extract_profiles.py

extract: extract-easymodes extract-translations extract-profiles  ## Run all three extractors

clean:  ## Remove build artifacts and tool caches
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache .coverage
	find openccu_data tests script -name __pycache__ -type d -prune -exec rm -rf {} +
