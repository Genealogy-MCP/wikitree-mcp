# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from wikitree_mcp.client import WikiTreeApiError, WikiTreeClient
from wikitree_mcp.operations import ConnectedProfilesByDNAParams, DNAKeyParams
from wikitree_mcp.server import AppContext
from wikitree_mcp.tools._errors import McpToolError


def _make_ctx(mock_client: AsyncMock) -> MagicMock:
    """Build a mock context wrapping a mock WikiTreeClient."""
    ctx = MagicMock()
    ctx.request_context.lifespan_context = AppContext(client=mock_client)
    return ctx


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=WikiTreeClient)


async def test_get_dna_tests_by_test_taker(
    mock_client: AsyncMock,
) -> None:
    from wikitree_mcp.tools.dna import get_dna_tests_handler

    mock_client.call.return_value = [
        {
            "page_name": "Whitten-1",
            "status": 0,
            "dnaTests": [{"dna_id": "1", "dna_slug": "23andme_audna"}],
        }
    ]
    ctx = _make_ctx(mock_client)
    result = await get_dna_tests_handler(ctx, DNAKeyParams(key="Whitten-1"))
    mock_client.call.assert_called_once_with(
        "getDNATestsByTestTaker",
        key="Whitten-1",
    )
    assert len(result) == 1
    data = json.loads(result[0].text)
    assert data[0]["dnaTests"][0]["dna_id"] == "1"


async def test_get_connected_profiles_by_dna_test(
    mock_client: AsyncMock,
) -> None:
    from wikitree_mcp.tools.dna import get_connected_profiles_handler

    mock_client.call.return_value = [
        {
            "page_name": "Whitten-1",
            "status": 0,
            "connections": [{"Id": "13654071", "Name": "Whitten-1205"}],
        }
    ]
    ctx = _make_ctx(mock_client)
    result = await get_connected_profiles_handler(
        ctx, ConnectedProfilesByDNAParams(key="Whitten-1", dna_id=1)
    )
    mock_client.call.assert_called_once_with(
        "getConnectedProfilesByDNATest",
        key="Whitten-1",
        dna_id=1,
    )
    assert len(result) == 1
    data = json.loads(result[0].text)
    assert data[0]["connections"][0]["Name"] == "Whitten-1205"


async def test_get_connected_dna_tests_by_profile(
    mock_client: AsyncMock,
) -> None:
    from wikitree_mcp.tools.dna import get_connected_dna_tests_handler

    mock_client.call.return_value = [
        {
            "page_name": "Whitten-1",
            "status": 0,
            "dnaTests": [{"dna_id": "1", "taker": {"Name": "Whitten-1"}}],
        }
    ]
    ctx = _make_ctx(mock_client)
    result = await get_connected_dna_tests_handler(ctx, DNAKeyParams(key="Whitten-1"))
    mock_client.call.assert_called_once_with(
        "getConnectedDNATestsByProfile",
        key="Whitten-1",
    )
    assert len(result) == 1


async def test_get_dna_tests_with_auth() -> None:
    from wikitree_mcp.tools.dna import get_dna_tests_handler

    client = AsyncMock(spec=WikiTreeClient)
    client.call.return_value = [{"status": 0, "dnaTests": []}]
    type(client).settings = PropertyMock(return_value=type("S", (), {"has_credentials": True})())
    client.ensure_auth = AsyncMock()
    ctx = _make_ctx(client)
    await get_dna_tests_handler(ctx, DNAKeyParams(key="X-1"))
    client.ensure_auth.assert_awaited_once()


async def test_get_dna_tests_without_auth() -> None:
    from wikitree_mcp.tools.dna import get_dna_tests_handler

    client = AsyncMock(spec=WikiTreeClient)
    client.call.return_value = [{"status": 0, "dnaTests": []}]
    type(client).settings = PropertyMock(return_value=type("S", (), {"has_credentials": False})())
    client.ensure_auth = AsyncMock()
    ctx = _make_ctx(client)
    await get_dna_tests_handler(ctx, DNAKeyParams(key="X-1"))
    client.ensure_auth.assert_not_awaited()


async def test_get_dna_tests_api_error(
    mock_client: AsyncMock,
) -> None:
    from wikitree_mcp.tools.dna import get_dna_tests_handler

    mock_client.call.side_effect = WikiTreeApiError("Timeout")
    ctx = _make_ctx(mock_client)
    with pytest.raises(McpToolError, match="Timeout"):
        await get_dna_tests_handler(ctx, DNAKeyParams(key="Bad-1"))
