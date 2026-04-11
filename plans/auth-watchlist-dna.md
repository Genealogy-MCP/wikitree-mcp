# Plan: Authentication, Watchlist, and DNA Enhancement

> Source PRD: wikitree-mcp#6

## Architectural decisions

Durable decisions that apply across all phases:

- **Auth flow**: WikiTree `clientLogin` — 2-step POST. Step 1 sends credentials with `follow_redirects=False`, extracts `authcode` from `Location` header. Step 2 confirms with `authcode`, setting session cookies via httpx cookie jar.
- **Settings**: `WIKITREE_EMAIL` and `WIKITREE_PASSWORD` env vars (pydantic-settings, optional). `has_credentials` property gates auth behavior.
- **Client surface**: `login()`, `ensure_auth()`, `is_authenticated` property, `settings` property — all on `WikiTreeClient`. No separate auth class.
- **Auth timing**: Lazy — `ensure_auth()` called by handlers, not at startup.
- **Graceful degradation**: Server starts without credentials. Auth-only tools raise `WikiTreeApiError` with actionable message. DNA tools fall back to unauthenticated access.
- **Registry**: 13 → 14 operations. New category `watchlist`.
- **No re-auth in v1**: WikiTree sessions are long-lived. Defer until expiry is observed.

---

## Phase 1: Settings + Client Auth

**User stories**: 2, 3, 4, 6, 9, 10

### What to build

Add optional email/password credentials to Settings with a `has_credentials` property. Extend WikiTreeClient with the full auth lifecycle: `login()` implements the 2-step flow, `ensure_auth()` gates access (lazy login or clear error), `is_authenticated` tracks state, and a `settings` property exposes credentials check to handlers.

This phase proves the auth path works end-to-end against mocked HTTP responses. No new tools or operations yet.

### Acceptance criteria

- [ ] `Settings(email="x", password="y").has_credentials` returns `True`
- [ ] `Settings().has_credentials` returns `False`
- [ ] `login()` succeeds with mocked 302 redirect + confirm response, sets `is_authenticated = True`
- [ ] `login()` raises `WikiTreeApiError` on bad credentials (mocked failure response)
- [ ] `ensure_auth()` with no credentials raises `WikiTreeApiError("Authentication required but WIKITREE_EMAIL and WIKITREE_PASSWORD not set.")`
- [ ] `ensure_auth()` when already authenticated is a no-op (no HTTP calls)
- [ ] `ensure_auth()` with credentials triggers `login()`
- [ ] Credentials never appear in error messages or logs
- [ ] All existing tests still pass

---

## Phase 2: Watchlist Tool

**User stories**: 1, 7, 11

### What to build

Add `get_watchlist` operation: a new handler that calls `ensure_auth()` then `getWatchlist` with pagination and filter parameters. Register in the operation registry with a `GetWatchlistParams` model and `watchlist` category. The operation is discoverable via the `search` meta-tool.

### Acceptance criteria

- [ ] `get_watchlist_handler` calls `ensure_auth()` then `client.call("getWatchlist", ...)`
- [ ] All `GetWatchlistParams` fields are optional (limit, offset, order, get_person, get_space, only_living, exclude_living, fields, bio_format)
- [ ] Handler returns `list[TextContent]` with JSON-formatted watchlist data
- [ ] Handler raises `McpToolError` when auth fails (no credentials)
- [ ] `search("watchlist")` returns the `get_watchlist` operation
- [ ] Registry count is 14, `watchlist` is a valid category

---

## Phase 3: DNA Auth Enhancement

**User stories**: 5, 8

### What to build

Add optional authentication to the 3 existing DNA handlers. Each handler checks `client.settings.has_credentials` before the API call — if True, calls `ensure_auth()` to get an authenticated session (unlocking private profile data). If False, proceeds unauthenticated (existing behavior unchanged).

### Acceptance criteria

- [ ] `get_dna_tests_handler` calls `ensure_auth()` when credentials are present
- [ ] `get_dna_tests_handler` does NOT call `ensure_auth()` when no credentials
- [ ] Same behavior verified for `get_connected_profiles_handler` and `get_connected_dna_tests_handler`
- [ ] All existing DNA tests still pass unchanged

---

## Phase 4: Docs + Verification

**User stories**: 12

### What to build

Update CLAUDE.md with the new operation count (14), watchlist category, auth env vars in the settings table, and auth flow documentation. Bump hardcoded counts in test assertions. Run full CI and verify the pipeline is green.

### Acceptance criteria

- [ ] CLAUDE.md reflects 14 operations, `watchlist.py` in architecture tree, auth settings documented
- [ ] `tests/test_operations.py` count is 14, valid categories include `watchlist`
- [ ] `tests/test_meta_search.py` references "14 operations available"
- [ ] `make ci` passes (all tests, >= 80% branch coverage, lint, typecheck, audit)
- [ ] GitLab CI pipeline is green
- [ ] MR created with `Closes #6` in description
