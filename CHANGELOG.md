# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `.github/dependabot.yml` — added `docker` ecosystem entry and `commit-message: prefix: "chore"` to all three entries (`pip`, `github-actions`, `docker`) so Dependabot PRs follow Conventional Commits convention

- `tools/_errors.py` — `McpToolError` exception class and `raise_tool_error()` helper; single source of truth for error formatting (MCP-8, MCP-10)
- `TOOL_REGISTRY` dict in `server.py` — derived at runtime from the FastMCP instance after all `register()` calls; satisfies MCP-6 without hardcoding tool counts
- `tests/test_errors.py` — unit tests for `McpToolError` and `raise_tool_error()`
- `tests/test_server.py` — asserts `len(TOOL_REGISTRY) == 10` and all 10 expected tool names present
- CI rewritten to 3-job structure: **lint** (ruff + pyright + copyright headers), **test** (Python 3.10/3.11/3.12/3.13 matrix, `fail-fast: false`), **security** (`pip-audit`); added `concurrency` group to cancel stale runs
- `pip-audit>=2.6.0` dev dependency
- `make typecheck`, `make audit`, `make run`, `make run-stdio` Makefile targets; `make ci` and `make check` as aliases for the full pipeline

### Changed

- All 10 tools now wrap `client.call()` in `try/except WikiTreeApiError` and call `raise_tool_error()` — errors surface as `McpToolError` with actionable messages (MCP-8 compliance)
- All 10 tools annotated with `_READ_ANNOTATIONS = ToolAnnotations(readOnlyHint=True, openWorldHint=True)` (MCP-5)
- `requires-python` lowered from `>=3.12` to `>=3.10`; CI matrix extended to include 3.10 and 3.11
- `pyproject.toml` `ruff target-version` and `pyright pythonVersion` updated from `py312`/`"3.12"` to `py310`/`"3.10"`
- `make type-check` kept as alias for `make typecheck` for backward compatibility

---

### Added (prior)

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

## [0.1.0] - Initial Release

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
