# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Authentication support via `WIKITREE_EMAIL` + `WIKITREE_PASSWORD` env vars (opt-in, lazy)
- `get_watchlist` operation — authenticated user's watchlist with pagination and filtering
- 3 DNA tools: `get_dna_tests`, `get_connected_profiles`, `get_connected_dna_tests`
- Authenticated DNA access — DNA handlers use auth session when credentials are configured
- `/health` endpoint for Docker HEALTHCHECK
- OCI labels, non-root user, EXPOSE 8000 in Dockerfile
- `.only-mr` YAML anchor — lint/test/security jobs run only on MR pipelines

### Fixed

- `get_ancestors` now uses `getPeople` with `ancestors=depth` (deprecated `getAncestors` action)

### Changed

- Operation registry grows from 10 to 14 operations (DNA + watchlist)
- CI: main branch pushes trigger only release detection pipeline

## [2.0.0] - 2026-04-08

### Changed

- **BREAKING:** Replaced 10 individual tools with 2 meta-tools (`search` + `execute`) following the Code Mode architecture (MCP-ORG-1). The 10 operations are still available but are now accessed through the `execute` meta-tool with `{operation: "...", params: {...}}`.
- Added `operations.py` at package root as the single source of truth for all operations (MCP-6)
- Added `tools/_errors.py` with `McpToolError` + `raise_tool_error()` for consistent error handling (MCP-8, MCP-10)
- Added `tools/meta_search.py` for operation discovery with keyword search and category filtering
- Added `tools/meta_execute.py` for validated operation dispatch with close-match suggestions
- Refactored handler modules (`profiles.py`, `genealogy.py`, `content.py`) from closures to standalone async functions
- Added `.pre-commit-config.yaml` with ruff, file-length, emoji, and copyright-header hooks
- Added `scripts/check_file_length.py` and `scripts/check_no_emojis.py` enforcement scripts
- Aligned Makefile targets with org standard (`typecheck`, `ci`, `audit`, `run`, `run-stdio`)

### Migration Guide

If you were calling tools by name (e.g. `get_profile`), you now need to:
1. Call `search` with `{"query": "profile"}` to discover the operation
2. Call `execute` with `{"operation": "get_profile", "params": {"key": "Clemens-1"}}`

## [0.1.0] - 2026-03-19

### Added

- Initial release with 10 WikiTree API tools
- `get_profile` — retrieve person or free-space profile
- `get_person` — retrieve person profile
- `get_people` — fetch multiple profiles by keys
- `search_person` — search profiles by criteria
- `get_ancestors` — get ancestral tree
- `get_descendants` — get descendant tree
- `get_relatives` — get parents, children, siblings, spouses
- `get_bio` — retrieve biography text
- `get_photos` — get photos linked to a profile
- `get_categories` — retrieve associated categories
- HTTP client with retry, timeout, and exponential backoff
- Docker support (multi-stage build)
- GitHub Actions CI pipeline
- `.github/dependabot.yml` — configured Dependabot for three ecosystems (pip, github-actions, docker) with `commit-message.prefix: "chore"` so version-update PRs follow Conventional Commits convention
- `make help` as the default target — running bare `make` now prints a self-documenting list of all targets
- Live API smoke tests (`tests/test_live_client.py`, `tests/test_live_tools.py`) gated behind `@pytest.mark.live` marker and `--run-live` pytest flag; never run in CI
- `make test-live` Makefile target for running live tests manually
- `live_settings` and `live_client` fixtures in `conftest.py` for real HTTP tests
- Default value for `WIKITREE_APP_ID` setting (`Genealogy-MCP_wikitree-mcp`); env var still overrides

### Fixed

- `_check_status` now accepts empty string `""` as a success status — `getPeople` returns `status: ""` on success, which was incorrectly treated as an error

### Changed

- Relicensed from MIT to AGPL-3.0-only — copyleft with network-use share-back requirement (closes SaaS loophole); updated `LICENSE`, `pyproject.toml`, and added SPDX headers to all source files
- `make test` now passes `-m "not live"` to exclude live tests from the default run
- `WIKITREE_APP_ID` is no longer required; falls back to `Genealogy-MCP_wikitree-mcp`

### Deprecated

- `getAncestors` API action is deprecated by WikiTree; live tests now use `getPeople` with `ancestors=1` instead
