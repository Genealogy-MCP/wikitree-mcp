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


async def test_get_bio(mcp: Any, mock_ctx: MagicMock, mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"bio": "Samuel Clemens...", "status": 0}]
    tool = _find_tool(mcp, "get_bio")
    result = await tool.fn(ctx=mock_ctx, key="Clemens-1", bio_format="wiki")
    mock_client.call.assert_called_once_with("getBio", key="Clemens-1", bioFormat="wiki")
    assert result == [{"bio": "Samuel Clemens...", "status": 0}]


async def test_get_photos(mcp: Any, mock_ctx: MagicMock, mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"photos": [], "status": 0}]
    tool = _find_tool(mcp, "get_photos")
    result = await tool.fn(ctx=mock_ctx, key="Clemens-1", limit=5, start=None, order=None)
    mock_client.call.assert_called_once_with(
        "getPhotos", key="Clemens-1", limit=5, start=None, order=None
    )
    assert result == [{"photos": [], "status": 0}]


async def test_get_categories(mcp: Any, mock_ctx: MagicMock, mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"categories": ["Authors"], "status": 0}]
    tool = _find_tool(mcp, "get_categories")
    result = await tool.fn(ctx=mock_ctx, key="Clemens-1")
    mock_client.call.assert_called_once_with("getCategories", key="Clemens-1")
    assert result == [{"categories": ["Authors"], "status": 0}]
