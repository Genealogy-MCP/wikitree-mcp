# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from wikitree_mcp.client import WikiTreeApiError, WikiTreeClient
from wikitree_mcp.tools._errors import McpToolError
from wikitree_mcp.tools.content import (
    get_bio_handler,
    get_categories_handler,
    get_photos_handler,
)


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=WikiTreeClient)


async def test_get_bio(mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"bio": "Samuel Clemens...", "status": 0}]
    result = await get_bio_handler({"key": "Clemens-1", "bio_format": "wiki"}, mock_client)
    mock_client.call.assert_called_once_with("getBio", key="Clemens-1", bioFormat="wiki")
    assert len(result) == 1
    assert json.loads(result[0].text) == [{"bio": "Samuel Clemens...", "status": 0}]


async def test_get_photos(mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"photos": [], "status": 0}]
    result = await get_photos_handler({"key": "Clemens-1", "limit": 5}, mock_client)
    mock_client.call.assert_called_once_with(
        "getPhotos",
        key="Clemens-1",
        limit=5,
        start=None,
        order=None,
    )
    assert len(result) == 1


async def test_get_categories(mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"categories": ["Authors"], "status": 0}]
    result = await get_categories_handler({"key": "Clemens-1"}, mock_client)
    mock_client.call.assert_called_once_with("getCategories", key="Clemens-1")
    assert len(result) == 1


async def test_get_bio_api_error(mock_client: AsyncMock) -> None:
    mock_client.call.side_effect = WikiTreeApiError("API error")
    with pytest.raises(McpToolError, match="API error"):
        await get_bio_handler({"key": "Bad-1"}, mock_client)
