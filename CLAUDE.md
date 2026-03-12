# WikiTree MCP — Development Reference

## Commands

```bash
make               # show help (default target)
make install       # uv sync --group dev
make test          # coverage run + report (excludes live tests)
make test-live     # pytest -m live --run-live -v (hits real API)
make lint          # ruff check src tests
make format        # ruff format src tests
make type-check    # pyright
make check         # lint + type-check + test
make build         # uv build
```

## Architecture

```
src/wikitree_mcp/
  settings.py      # pydantic-settings; all env vars prefixed WIKITREE_
  client.py        # WikiTreeClient — async HTTP, retry, status-check
  server.py        # FastMCP server, AppContext lifespan
  tools/
    profiles.py    # get_profile, get_person, get_people, search_person
    genealogy.py   # get_ancestors, get_descendants, get_relatives
    content.py     # get_bio, get_photos, get_categories
```

Tools extract the client from MCP lifespan context via `ctx.request_context.lifespan_context.client`.

## Key Settings

| Var | Default | Notes |
|---|---|---|
| `WIKITREE_APP_ID` | `Genealogy-MCP_wikitree-mcp` | Override via env var |
| `WIKITREE_API_BASE_URL` | `https://api.wikitree.com/api.php` | |
| `WIKITREE_HTTP_TIMEOUT` | `10.0` | seconds |
| `WIKITREE_MAX_RETRIES` | `3` | exponential backoff with jitter |

## WikiTree API Quirks

- **`getAncestors` is deprecated** — use `getPeople` with `ancestors=1` instead
- **`getPeople` returns `status: ""`** (empty string) on success — not `0` or `"0"`
- **`getProfile` response shape**: data lives under `result[0]["profile"]`
- **`getPeople` response shape**: data lives under `result[0]["people"]` (dict keyed by Id)
- **`searchPerson` response shape**: results are the top-level list items; `result[0]["status"] == 0` (integer)
- **Status field inconsistency**: `status` can be `0` (int), `"0"` (str), `""` (str), or an error string — `_check_status` treats all three success variants as valid

## Testing

### Mocked tests (default, run in CI)
- `tests/test_client.py` — client unit tests using `respx`
- `tests/test_settings.py` — settings validation
- `tests/test_tools_*.py` — tool tests using `AsyncMock(spec=WikiTreeClient)`

### Live tests (manual, gated)
- `tests/test_live_client.py` — 6 real HTTP tests
- `tests/test_live_tools.py` — 3 tool integration tests
- Gated by `@pytest.mark.live` + `--run-live` CLI flag
- Stable test profiles: `Clemens-1` (Samuel Clemens), `Franklin-10478` (Aretha Franklin)

### Fixtures (conftest.py)
- `settings` — `Settings(app_id="test-app")`
- `mock_api` — `respx.MockRouter`
- `live_settings` — `Settings()` (uses default app_id)
- `live_client` — real `WikiTreeClient` with async cleanup

## CI

GitHub Actions pipeline: install → lint → type-check → test (mocked only).
Live tests never run in CI.
