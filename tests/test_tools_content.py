# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from wikitree_mcp.client import WikiTreeApiError, WikiTreeClient
from wikitree_mcp.operations import (
    GetBioParams,
    GetCategoriesParams,
    GetPhotosParams,
)
from wikitree_mcp.server import AppContext
from wikitree_mcp.tools._errors import McpToolError
from wikitree_mcp.tools.content import (
    get_bio_handler,
    get_categories_handler,
    get_photos_handler,
)


def _make_ctx(mock_client: AsyncMock) -> MagicMock:
    """Build a mock context wrapping a mock WikiTreeClient."""
    ctx = MagicMock()
    ctx.request_context.lifespan_context = AppContext(client=mock_client)
    return ctx


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=WikiTreeClient)


async def test_get_bio(mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"bio": "Samuel Clemens...", "status": 0}]
    ctx = _make_ctx(mock_client)
    result = await get_bio_handler(ctx, GetBioParams(key="Clemens-1", bio_format="wiki"))
    mock_client.call.assert_called_once_with("getBio", key="Clemens-1", bioFormat="wiki")
    assert len(result) == 1
    assert json.loads(result[0].text) == [{"bio": "Samuel Clemens...", "status": 0}]


async def test_get_photos(mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"photos": [], "status": 0}]
    ctx = _make_ctx(mock_client)
    result = await get_photos_handler(ctx, GetPhotosParams(key="Clemens-1", limit=5))
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
    ctx = _make_ctx(mock_client)
    result = await get_categories_handler(ctx, GetCategoriesParams(key="Clemens-1"))
    mock_client.call.assert_called_once_with("getCategories", key="Clemens-1")
    assert len(result) == 1


async def test_get_bio_api_error(mock_client: AsyncMock) -> None:
    mock_client.call.side_effect = WikiTreeApiError("API error")
    ctx = _make_ctx(mock_client)
    with pytest.raises(McpToolError, match="API error"):
        await get_bio_handler(ctx, GetBioParams(key="Bad-1"))
