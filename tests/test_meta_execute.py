# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest
from mcp.types import TextContent

from wikitree_mcp.client import WikiTreeClient
from wikitree_mcp.tools._errors import McpToolError
from wikitree_mcp.tools.meta_execute import execute_operation_tool


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=WikiTreeClient)


async def test_unknown_operation_raises_error(
    mock_client: AsyncMock,
) -> None:
    with pytest.raises(McpToolError, match="Unknown operation"):
        await execute_operation_tool({"operation": "nonexistent", "params": {}}, mock_client)


async def test_unknown_operation_suggests_close_match(
    mock_client: AsyncMock,
) -> None:
    with pytest.raises(McpToolError, match="get_profile"):
        await execute_operation_tool({"operation": "get_profil", "params": {}}, mock_client)


async def test_missing_required_param_raises_error(
    mock_client: AsyncMock,
) -> None:
    with pytest.raises(McpToolError, match="Invalid parameters"):
        await execute_operation_tool({"operation": "get_profile", "params": {}}, mock_client)


async def test_valid_dispatch(mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"page_name": "Clemens-1"}]
    result = await execute_operation_tool(
        {
            "operation": "get_profile",
            "params": {"key": "Clemens-1"},
        },
        mock_client,
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert json.loads(result[0].text) == [{"page_name": "Clemens-1"}]
    mock_client.call.assert_called_once()


async def test_dispatch_passes_optional_params(
    mock_client: AsyncMock,
) -> None:
    mock_client.call.return_value = [{"status": 0}]
    await execute_operation_tool(
        {
            "operation": "get_profile",
            "params": {"key": "Clemens-1", "fields": "Id,Name"},
        },
        mock_client,
    )
    mock_client.call.assert_called_once_with(
        "getProfile",
        key="Clemens-1",
        fields="Id,Name",
        bioFormat=None,
        resolveRedirect=None,
    )


async def test_default_empty_params(mock_client: AsyncMock) -> None:
    with pytest.raises(McpToolError, match="Invalid parameters"):
        await execute_operation_tool({"operation": "get_ancestors"}, mock_client)
