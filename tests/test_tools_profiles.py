# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from wikitree_mcp.client import WikiTreeApiError, WikiTreeClient
from wikitree_mcp.server import AppContext, create_server
from wikitree_mcp.tools._errors import McpToolError


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


async def test_get_profile(mcp: Any, mock_ctx: MagicMock, mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"page_name": "Clemens-1", "status": 0}]
    tool = _find_tool(mcp, "get_profile")
    result = await tool.fn(
        ctx=mock_ctx,
        key="Clemens-1",
        fields="Id,Name",
        bio_format=None,
        resolve_redirect=None,
    )
    mock_client.call.assert_called_once_with(
        "getProfile", key="Clemens-1", fields="Id,Name", bioFormat=None, resolveRedirect=None
    )
    assert result == [{"page_name": "Clemens-1", "status": 0}]


async def test_get_person(mcp: Any, mock_ctx: MagicMock, mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"page_name": "Clemens-1", "status": 0}]
    tool = _find_tool(mcp, "get_person")
    result = await tool.fn(
        ctx=mock_ctx,
        key="Clemens-1",
        fields=None,
        bio_format="wiki",
        resolve_redirect=None,
    )
    mock_client.call.assert_called_once_with(
        "getPerson", key="Clemens-1", fields=None, bioFormat="wiki", resolveRedirect=None
    )
    assert result == [{"page_name": "Clemens-1", "status": 0}]


async def test_get_people(mcp: Any, mock_ctx: MagicMock, mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"status": 0}]
    tool = _find_tool(mcp, "get_people")
    result = await tool.fn(
        ctx=mock_ctx,
        keys="Clemens-1,Twain-1",
        fields=None,
        ancestors=2,
        descendants=None,
        siblings=None,
        nuclear=None,
        limit=None,
        start=None,
    )
    mock_client.call.assert_called_once_with(
        "getPeople",
        keys="Clemens-1,Twain-1",
        fields=None,
        ancestors=2,
        descendants=None,
        siblings=None,
        nuclear=None,
        limit=None,
        start=None,
    )
    assert result == [{"status": 0}]


async def test_search_person(mcp: Any, mock_ctx: MagicMock, mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"status": 0}]
    tool = _find_tool(mcp, "search_person")
    result = await tool.fn(
        ctx=mock_ctx,
        first_name="Mark",
        last_name="Twain",
        birth_date=None,
        death_date=None,
        birth_location=None,
        gender=None,
        limit=10,
        start=None,
        fields=None,
    )
    mock_client.call.assert_called_once_with(
        "searchPerson",
        FirstName="Mark",
        LastName="Twain",
        BirthDate=None,
        DeathDate=None,
        BirthLocation=None,
        Gender=None,
        limit=10,
        start=None,
        fields=None,
    )
    assert result == [{"status": 0}]


async def test_get_profile_api_error(
    mcp: Any, mock_ctx: MagicMock, mock_client: AsyncMock
) -> None:
    mock_client.call.side_effect = WikiTreeApiError("Permission Denied")
    tool = _find_tool(mcp, "get_profile")
    with pytest.raises(McpToolError, match="Permission Denied"):
        await tool.fn(ctx=mock_ctx, key="Private-1", fields=None, bio_format=None, resolve_redirect=None)
