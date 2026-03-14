.PHONY: help install test test-live lint format typecheck type-check check-headers audit ci check run run-stdio build clean

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
	uv run ruff format --check src tests

format: ## Auto-format source and tests
	uv run ruff format src tests
	uv run ruff check --fix src tests

typecheck: ## Run static type checker
	uv run pyright src/

type-check: typecheck ## Alias for typecheck

check-headers: ## Check AGPL copyright headers
	find src/ scripts/ tests/ -name '*.py' -exec uv run python scripts/check_copyright_header.py {} +

audit: ## Run dependency security audit
	uv run pip-audit

ci: lint typecheck check-headers test audit ## Run full CI pipeline (lint + typecheck + headers + test + audit)

check: ci ## Alias for ci

run: ## Start server (streamable-HTTP on port 8000)
	uv run wikitree-mcp

run-stdio: ## Start server (stdio transport for Claude Code / Claude Desktop)
	uv run wikitree-mcp --transport stdio

build: ## Build wheel
	uv build

clean: ## Remove build artifacts and caches
	rm -rf dist build .pytest_cache .ruff_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
