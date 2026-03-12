.PHONY: install test lint format type-check check build clean

install:
	uv sync

test:
	uv run coverage run -m pytest
	uv run coverage report

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests

type-check:
	uv run pyright

check: lint type-check test

build:
	uv build

clean:
	rm -rf dist build .pytest_cache .ruff_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
