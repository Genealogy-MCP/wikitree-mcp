# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""Tests for the execute meta-tool via FastMCP (backed by mcp-codemode library)."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from mcp_codemode import ExecuteOperationParams

from wikitree_mcp.client import WikiTreeClient
from wikitree_mcp.server import AppContext, create_server
from wikitree_mcp.tools._errors import McpToolError


def _find_tool(mcp: Any, name: str) -> Any:
    """Extract a registered tool from FastMCP by name."""
    for tool in mcp._tool_manager._tools.values():
        if tool.name == name:
            return tool
    raise ValueError(f"Tool {name} not found")


def _make_ctx(mock_client: AsyncMock) -> MagicMock:
    """Build a mock context wrapping a mock WikiTreeClient."""
    ctx = MagicMock()
    ctx.request_context.lifespan_context = AppContext(client=mock_client)
    return ctx


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=WikiTreeClient)


@pytest.fixture
def mcp() -> Any:
    return create_server()


async def test_unknown_operation_raises_error(
    mcp: Any,
    mock_client: AsyncMock,
) -> None:
    ctx = _make_ctx(mock_client)
    tool = _find_tool(mcp, "execute")
    with pytest.raises(McpToolError, match="Unknown operation"):
        await tool.fn(ctx=ctx, arguments=ExecuteOperationParams(operation="nonexistent"))


async def test_unknown_operation_suggests_close_match(
    mcp: Any,
    mock_client: AsyncMock,
) -> None:
    ctx = _make_ctx(mock_client)
    tool = _find_tool(mcp, "execute")
    with pytest.raises(McpToolError, match="Did you mean"):
        await tool.fn(ctx=ctx, arguments=ExecuteOperationParams(operation="get_profil"))


async def test_missing_required_param_raises_error(
    mcp: Any,
    mock_client: AsyncMock,
) -> None:
    ctx = _make_ctx(mock_client)
    tool = _find_tool(mcp, "execute")
    with pytest.raises(McpToolError, match="(?i)key"):
        await tool.fn(
            ctx=ctx,
            arguments=ExecuteOperationParams(operation="get_profile", params={}),
        )


async def test_valid_dispatch(
    mcp: Any,
    mock_client: AsyncMock,
) -> None:
    mock_client.call.return_value = [{"page_name": "Clemens-1"}]
    ctx = _make_ctx(mock_client)
    tool = _find_tool(mcp, "execute")
    result = await tool.fn(
        ctx=ctx,
        arguments=ExecuteOperationParams(
            operation="get_profile",
            params={"key": "Clemens-1"},
        ),
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert json.loads(result[0].text) == [{"page_name": "Clemens-1"}]
    mock_client.call.assert_called_once()


async def test_dispatch_passes_optional_params(
    mcp: Any,
    mock_client: AsyncMock,
) -> None:
    mock_client.call.return_value = [{"status": 0}]
    ctx = _make_ctx(mock_client)
    tool = _find_tool(mcp, "execute")
    await tool.fn(
        ctx=ctx,
        arguments=ExecuteOperationParams(
            operation="get_profile",
            params={"key": "Clemens-1", "fields": "Id,Name"},
        ),
    )
    mock_client.call.assert_called_once_with(
        "getProfile",
        key="Clemens-1",
        fields="Id,Name",
        bioFormat=None,
        resolveRedirect=None,
    )


async def test_default_empty_params(
    mcp: Any,
    mock_client: AsyncMock,
) -> None:
    ctx = _make_ctx(mock_client)
    tool = _find_tool(mcp, "execute")
    with pytest.raises(McpToolError):
        await tool.fn(
            ctx=ctx,
            arguments=ExecuteOperationParams(operation="get_ancestors"),
        )
