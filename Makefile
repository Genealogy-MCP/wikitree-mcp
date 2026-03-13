.PHONY: help install test test-live lint format type-check check-headers check build clean

.DEFAULT_GOAL := help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync --group dev

test: ## Run tests with coverage (excludes live)
	uv run coverage run -m pytest -m "not live"
	uv run coverage report

test-live: ## Run live tests against real WikiTree API
	uv run pytest -m live --run-live -v

lint: ## Lint source and tests
	uv run ruff check src tests

format: ## Auto-format source and tests
	uv run ruff format src tests

type-check: ## Run static type checker
	uv run pyright

check-headers: ## Check AGPL copyright headers
	find src/ scripts/ tests/ -name '*.py' -exec uv run python scripts/check_copyright_header.py {} +

check: lint type-check check-headers test ## Run lint + type-check + headers + test

build: ## Build wheel
	uv build

clean: ## Remove build artifacts and caches
	rm -rf dist build .pytest_cache .ruff_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
