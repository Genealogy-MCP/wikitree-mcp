# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from wikitree_mcp.client import WikiTreeApiError, WikiTreeClient
from wikitree_mcp.tools._errors import McpToolError


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
    result = await get_watchlist_handler({"limit": 10, "order": "page_touched"}, mock_client)
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
    with pytest.raises(McpToolError, match="WIKITREE_EMAIL"):
        await get_watchlist_handler({}, mock_client)
