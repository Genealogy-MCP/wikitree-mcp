# WikiTree MCP — Development Reference

## Commands

```bash
make               # show help (default target)
make install       # uv sync --group dev
make test          # coverage run + report (excludes live tests)
make test-live     # pytest -m live --run-live -v (hits real API)
make lint          # ruff check src tests
make format        # ruff format + ruff check --fix src tests
make typecheck     # pyright src
make check-headers # verify SPDX copyright headers
make audit         # pip-audit
make ci            # lint + typecheck + check-headers + test + audit
make build         # uv build
make run           # streamable-http on port 8000
make run-stdio     # stdio transport
```

## Git Hosting Policy

This repo lives on GitLab. GitHub is a read-only push-mirror.

- All commits, MRs, issues, releases, CI, and container registry operations target
  `gitlab.com/genealogy-mcp/wikitree-mcp` only.
- Never run `gh` write commands against this repo — use `glab` instead. See the
  `gh` → `glab` mapping table in the org root
  [`../CLAUDE.md` — Git Hosting Policy](../CLAUDE.md#git-hosting-policy) for the
  full command reference and the `GH-ORG-1..7` rules.
- If a skill or sub-agent attempts a GitHub write operation, redirect it to the
  `glab` equivalent or stop and ask the user.

## Architecture

This server uses the Code Mode architecture (MCP-ORG-1): exactly 2 meta-tools
(`search` + `execute`) instead of individual per-operation tools. The LLM
discovers operations via `search` and runs them via `execute`.

```
src/wikitree_mcp/
  __init__.py       # main() entry point + create_server()
  __main__.py       # python -m wikitree_mcp
  settings.py       # pydantic-settings; all env vars prefixed WIKITREE_
  client.py         # WikiTreeClient — async HTTP, retry, status-check
  server.py         # FastMCP server, AppContext lifespan, _META_TOOLS registration
  operations.py     # OperationEntry + OPERATION_REGISTRY + search_operations() + summarize_params()
  tools/
    _errors.py      # McpToolError, raise_tool_error (MCP-8, MCP-10)
    meta_search.py  # search meta-tool: operation discovery by keyword
    meta_execute.py # execute meta-tool: validated dispatch to handlers
    profiles.py     # 4 handlers: get_profile, get_person, get_people, search_person
    genealogy.py    # 3 handlers: get_ancestors, get_descendants, get_relatives
    content.py      # 3 handlers: get_bio, get_photos, get_categories
    dna.py          # 3 handlers: get_dna_tests, get_connected_profiles, get_connected_dna_tests
```

### Tools (2 meta-tools, 13 operations)

Tools: `search` (operation discovery), `execute` (operation dispatch)

Operations: `get_profile`, `get_person`, `get_people`, `search_person`,
`get_ancestors`, `get_descendants`, `get_relatives`, `get_bio`, `get_photos`,
`get_categories`, `get_dna_tests`, `get_connected_profiles`,
`get_connected_dna_tests`

### Data Flow

```
LLM -> search(query) -> OPERATION_REGISTRY -> matching operations
LLM -> execute(operation, params) -> validate params -> handler(params, client) -> WikiTree API
```

### Handler Signature

All handlers follow the same pattern:
```python
async def handler(params: dict, client: WikiTreeClient) -> list[TextContent]
```

The `execute` meta-tool extracts the `WikiTreeClient` from the FastMCP lifespan
context and passes it to handlers. Handlers never see `ctx`.

## Key Settings

| Var | Default | Notes |
|---|---|---|
| `WIKITREE_APP_ID` | `Genealogy-MCP_wikitree-mcp` | Override via env var |
| `WIKITREE_API_BASE_URL` | `https://api.wikitree.com/api.php` | |
| `WIKITREE_HTTP_TIMEOUT` | `10.0` | seconds |
| `WIKITREE_MAX_RETRIES` | `3` | exponential backoff with jitter |

## WikiTree API Quirks

- **`getAncestors` is deprecated** — `get_ancestors` handler uses `getPeople` with `ancestors=depth` internally
- **`getPeople` returns `status: ""`** (empty string) on success — not `0` or `"0"`
- **`getProfile` response shape**: data lives under `result[0]["profile"]`
- **`getPeople` response shape**: data lives under `result[0]["people"]` (dict keyed by Id)
- **`searchPerson` response shape**: results are the top-level list items; `result[0]["status"] == 0` (integer)
- **`searchPerson` uses PascalCase params**: `FirstName`, `LastName`, `BirthDate` etc.
- **Status field inconsistency**: `status` can be `0` (int), `"0"` (str), `""` (str), or an error string — `_check_status` treats all three success variants as valid

## Testing

### Mocked tests (default, run in CI)
- `tests/test_client.py` — client unit tests using `respx`
- `tests/test_settings.py` — settings validation
- `tests/test_errors.py` — McpToolError and raise_tool_error
- `tests/test_operations.py` — registry completeness, search scoring, param validation
- `tests/test_meta_search.py` — search meta-tool
- `tests/test_meta_execute.py` — execute meta-tool dispatch, validation, error handling
- `tests/test_tools_*.py` — handler unit tests using `AsyncMock(spec=WikiTreeClient)`

### Live tests (manual, gated)
- `tests/test_live_client.py` — 6 real HTTP tests
- `tests/test_live_tools.py` — 4 tool integration tests via execute meta-tool
- Gated by `@pytest.mark.live` + `--run-live` CLI flag
- Stable test profiles: `Clemens-1` (Samuel Clemens), `Franklin-10478` (Aretha Franklin)

### Fixtures (conftest.py)
- `settings` — `Settings(app_id="test-app")`
- `mock_api` — `respx.MockRouter`
- `live_settings` — `Settings()` (uses default app_id)
- `live_client` — real `WikiTreeClient` with async cleanup

## CI

GitLab CI pipeline (`.gitlab-ci.yml`): lint+typecheck, test matrix (py3.10-3.13), security audit.
Live tests never run in CI.
