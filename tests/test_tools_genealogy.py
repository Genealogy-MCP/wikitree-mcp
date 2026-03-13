# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from wikitree_mcp.client import WikiTreeClient
from wikitree_mcp.server import AppContext, create_server


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=WikiTreeClient)


@pytest.fixture
def mock_ctx(mock_client: AsyncMock) -> MagicMock:
    ctx = MagicMock()
    ctx.request_context.lifespan_context = AppContext(client=mock_client)
    return ctx


@pytest.fixture
def mcp() -> Any:
    return create_server()


def _find_tool(mcp: Any, name: str) -> Any:
    for tool in mcp._tool_manager._tools.values():
        if tool.name == name:
            return tool
    raise ValueError(f"Tool {name} not found")


async def test_get_ancestors(mcp: Any, mock_ctx: MagicMock, mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"ancestors": [], "status": 0}]
    tool = _find_tool(mcp, "get_ancestors")
    result = await tool.fn(ctx=mock_ctx, key="Clemens-1", depth=3, fields=None, bio_format=None)
    mock_client.call.assert_called_once_with(
        "getAncestors", key="Clemens-1", depth=3, fields=None, bioFormat=None
    )
    assert result == [{"ancestors": [], "status": 0}]


async def test_get_descendants(mcp: Any, mock_ctx: MagicMock, mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"descendants": [], "status": 0}]
    tool = _find_tool(mcp, "get_descendants")
    result = await tool.fn(
        ctx=mock_ctx,
        key="Clemens-1",
        depth=2,
        fields="Id,Name",
        bio_format=None,
    )
    mock_client.call.assert_called_once_with(
        "getDescendants", key="Clemens-1", depth=2, fields="Id,Name", bioFormat=None
    )
    assert result == [{"descendants": [], "status": 0}]


async def test_get_relatives(mcp: Any, mock_ctx: MagicMock, mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"status": 0}]
    tool = _find_tool(mcp, "get_relatives")
    result = await tool.fn(
        ctx=mock_ctx,
        keys="Clemens-1",
        fields=None,
        get_parents=1,
        get_children=1,
        get_siblings=None,
        get_spouses=None,
    )
    mock_client.call.assert_called_once_with(
        "getRelatives",
        keys="Clemens-1",
        fields=None,
        getParents=1,
        getChildren=1,
        getSiblings=None,
        getSpouses=None,
    )
    assert result == [{"status": 0}]
