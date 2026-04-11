# WikiTree Authentication, Watchlist, and DNA Enhancement

## Problem

The MCP implements 13 of 14 WikiTree API actions. The missing action
(`getWatchlist`) requires cookie-based session authentication, which the
client doesn't support. The 3 existing DNA tools work on public profiles
only; authenticated sessions would unlock private profile DNA data.

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Auth mode | Opt-in, graceful | Server works without credentials; auth-only tools return clear errors |
| Auth timing | Lazy (first auth-required call) | No wasted login if only public tools are used |
| Architecture | Auth methods on WikiTreeClient | httpx handles cookies natively; no need for separate class |
| Scope | Auth + watchlist + DNA enhancement | Complete the full auth story in one MR |
| Re-auth on expiry | Not in v1 | WikiTree sessions are long-lived; YAGNI |

## Settings

Add two optional fields to `Settings` (env prefix `WIKITREE_`):

```python
email: str | None = None       # WIKITREE_EMAIL
password: str | None = None    # WIKITREE_PASSWORD
```

A `has_credentials` property returns `True` when both are set.
Credentials never appear in logs or error messages (OB-4).

## WikiTreeClient Auth

Add to `WikiTreeClient`:

- `_authenticated: bool` instance variable, initially `False`
- `is_authenticated` read-only property
- `login()` async method implementing the 2-step WikiTree auth flow:
  1. POST `action=clientLogin&doLogin=1&wpEmail=...&wpPassword=...`
     with `follow_redirects=False`. Extract `authcode` from the
     `Location` header of the 302 response.
  2. POST `action=clientLogin&authcode=...`. Confirm
     `result == "success"`. Session cookies are set automatically by
     httpx's cookie jar.
  3. Set `_authenticated = True`. Raise `WikiTreeApiError` on failure.
- `ensure_auth()` async method:
  - If already authenticated, no-op.
  - If `settings.has_credentials`, call `login()`.
  - If no credentials, raise `WikiTreeApiError` with message:
    `"Authentication required but WIKITREE_EMAIL and WIKITREE_PASSWORD not set."`

The existing `call()` method is unchanged. httpx sends session cookies
automatically once set by `login()`.

## New Operation: get_watchlist

**Handler:** `tools/watchlist.py` -> `get_watchlist_handler`

Calls `client.ensure_auth()` then `client.call("getWatchlist", ...)`.

**Params:** `GetWatchlistParams` (all optional):
- `limit: int | None` (default API: 100)
- `offset: int | None`
- `order: str | None` (`user_id`, `user_name`, `user_last_name_current`,
  `user_birth_date`, `user_death_date`, `page_touched`)
- `get_person: int | None` (1 to include person profiles)
- `get_space: int | None` (1 to include space profiles)
- `only_living: int | None`
- `exclude_living: int | None`
- `fields: str | None`
- `bio_format: str | None`

**Registry:** category `watchlist`, `read_only=True`.

## DNA Handler Enhancement

All 3 DNA handlers (`get_dna_tests_handler`, `get_connected_profiles_handler`,
`get_connected_dna_tests_handler`) gain optional auth:

```python
if client.settings.has_credentials:
    await client.ensure_auth()
```

This is called before the API call. When authenticated, DNA data for
private profiles becomes accessible. When no credentials are configured,
behavior is unchanged (public profiles only).

The `settings` attribute is already available on `WikiTreeClient` as
`self._settings`. Expose it as a read-only `settings` property.

## File Changes

| File | Change |
|---|---|
| `settings.py` | Add `email`, `password`, `has_credentials` |
| `client.py` | Add `login()`, `ensure_auth()`, `is_authenticated`, `settings` property |
| `tools/watchlist.py` | New file: `get_watchlist_handler` |
| `tools/dna.py` | Add `ensure_auth()` call when credentials present |
| `operations.py` | Add `GetWatchlistParams`, `get_watchlist` registry entry |
| `CLAUDE.md` | Update tool count (14 ops), add watchlist category, document auth |
| `tests/test_client.py` | Auth flow tests (success, failure, no creds, already authed) |
| `tests/test_settings.py` | `has_credentials` property tests |
| `tests/test_tools_watchlist.py` | New file: handler tests |
| `tests/test_tools_dna.py` | Add auth call verification test |
| `tests/test_operations.py` | Bump count to 14, add `watchlist` category |
| `tests/test_meta_search.py` | Bump operation count in no-match test |
| `tests/test_live_tools.py` | Add live `get_watchlist` test (gated) |

## Testing Strategy

**Mocked tests:**
- Auth 2-step flow via `respx` (mock redirect + confirm responses)
- `ensure_auth()` error paths (no creds, bad creds)
- `ensure_auth()` no-op when already authenticated
- Watchlist handler happy path and auth error
- DNA handlers call `ensure_auth()` when credentials present

**Live tests (manual, `@pytest.mark.live`):**
- `test_execute_get_watchlist` with real credentials

## Verification

1. `make format` + `make lint` pass
2. `make typecheck` passes
3. `make test` passes with >= 80% branch coverage
4. `make ci` green
5. Push, CI pipeline passes
6. `make test-live` with `WIKITREE_EMAIL`/`WIKITREE_PASSWORD` set (manual)
