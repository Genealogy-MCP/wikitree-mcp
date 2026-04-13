# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from wikitree_mcp.client import WikiTreeApiError, WikiTreeClient
from wikitree_mcp.operations import GetWatchlistParams
from wikitree_mcp.server import AppContext
from wikitree_mcp.tools._errors import McpToolError


def _make_ctx(mock_client: AsyncMock) -> MagicMock:
    """Build a mock context wrapping a mock WikiTreeClient."""
    ctx = MagicMock()
    ctx.request_context.lifespan_context = AppContext(client=mock_client)
    return ctx


@pytest.fixture
def mock_client() -> AsyncMock:
    client = AsyncMock(spec=WikiTreeClient)
    client.ensure_auth = AsyncMock()
    return client


async def test_get_watchlist_success(mock_client: AsyncMock) -> None:
    from wikitree_mcp.tools.watchlist import get_watchlist_handler

    mock_client.call.return_value = [
        {
            "watchlistCount": 2,
            "watchlist": [
                {"Id": 1, "Name": "Clemens-1"},
                {"Id": 2, "Name": "Twain-1"},
            ],
        }
    ]
    ctx = _make_ctx(mock_client)
    result = await get_watchlist_handler(ctx, GetWatchlistParams(limit=10, order="page_touched"))
    mock_client.ensure_auth.assert_awaited_once()
    mock_client.call.assert_called_once_with(
        "getWatchlist",
        limit=10,
        offset=None,
        order="page_touched",
        getPerson=None,
        getSpace=None,
        onlyLiving=None,
        excludeLiving=None,
        fields=None,
        bioFormat=None,
    )
    assert len(result) == 1
    data = json.loads(result[0].text)
    assert data[0]["watchlistCount"] == 2


async def test_get_watchlist_auth_error(mock_client: AsyncMock) -> None:
    from wikitree_mcp.tools.watchlist import get_watchlist_handler

    mock_client.ensure_auth.side_effect = WikiTreeApiError(
        "Authentication required but WIKITREE_EMAIL and WIKITREE_PASSWORD not set."
    )
    ctx = _make_ctx(mock_client)
    with pytest.raises(McpToolError, match="WIKITREE_EMAIL"):
        await get_watchlist_handler(ctx, GetWatchlistParams())
