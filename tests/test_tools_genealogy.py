# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from wikitree_mcp.client import WikiTreeApiError, WikiTreeClient
from wikitree_mcp.tools._errors import McpToolError
from wikitree_mcp.tools.genealogy import (
    get_ancestors_handler,
    get_descendants_handler,
    get_relatives_handler,
)


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=WikiTreeClient)


async def test_get_ancestors(mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"status": 0}]
    result = await get_ancestors_handler({"key": "Clemens-1", "depth": 3}, mock_client)
    mock_client.call.assert_called_once_with(
        "getAncestors",
        key="Clemens-1",
        depth=3,
        fields=None,
        bioFormat=None,
    )
    assert len(result) == 1
    assert json.loads(result[0].text) == [{"status": 0}]


async def test_get_descendants(mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"status": 0}]
    result = await get_descendants_handler({"key": "Clemens-1", "depth": 2}, mock_client)
    mock_client.call.assert_called_once_with(
        "getDescendants",
        key="Clemens-1",
        depth=2,
        fields=None,
        bioFormat=None,
    )
    assert len(result) == 1


async def test_get_relatives(mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"status": 0}]
    result = await get_relatives_handler({"keys": "Clemens-1", "get_parents": 1}, mock_client)
    mock_client.call.assert_called_once_with(
        "getRelatives",
        keys="Clemens-1",
        fields=None,
        getParents=1,
        getChildren=None,
        getSiblings=None,
        getSpouses=None,
    )
    assert len(result) == 1


async def test_get_ancestors_api_error(mock_client: AsyncMock) -> None:
    mock_client.call.side_effect = WikiTreeApiError("Timeout")
    with pytest.raises(McpToolError, match="Timeout"):
        await get_ancestors_handler({"key": "Bad-1", "depth": 1}, mock_client)
