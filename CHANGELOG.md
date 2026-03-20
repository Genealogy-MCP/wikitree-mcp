# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
