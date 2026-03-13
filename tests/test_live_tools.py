# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from typing import Any
from unittest.mock import MagicMock

import pytest

from wikitree_mcp.client import WikiTreeClient
from wikitree_mcp.server import AppContext, create_server

pytestmark = pytest.mark.live


@pytest.fixture
def mcp() -> Any:
    return create_server()


@pytest.fixture
def live_ctx(live_client: WikiTreeClient) -> MagicMock:
    ctx = MagicMock()
    ctx.request_context.lifespan_context = AppContext(client=live_client)
    return ctx


def _find_tool(mcp: Any, name: str) -> Any:
    for tool in mcp._tool_manager._tools.values():
        if tool.name == name:
            return tool
    raise ValueError(f"Tool {name} not found")


async def test_get_profile_tool(mcp: Any, live_ctx: MagicMock) -> None:
    tool = _find_tool(mcp, "get_profile")
    result = await tool.fn(
        ctx=live_ctx,
        key="Clemens-1",
        fields="Id,Name,FirstName",
        bio_format=None,
        resolve_redirect=None,
    )
    profile = result[0]["profile"]
    assert profile["FirstName"] == "Samuel"


async def test_search_person_tool(mcp: Any, live_ctx: MagicMock) -> None:
    tool = _find_tool(mcp, "search_person")
    result = await tool.fn(
        ctx=live_ctx,
        first_name="Samuel",
        last_name="Clemens",
        birth_date=None,
        death_date=None,
        birth_location=None,
        gender=None,
        limit=5,
        start=None,
        fields=None,
    )
    assert len(result) >= 1
    assert result[0]["status"] == 0


async def test_get_people_ancestors_tool(mcp: Any, live_ctx: MagicMock) -> None:
    tool = _find_tool(mcp, "get_people")
    result = await tool.fn(
        ctx=live_ctx,
        keys="Clemens-1",
        fields="Id,Name",
        ancestors=1,
        descendants=None,
        siblings=None,
        nuclear=None,
        limit=None,
        start=None,
    )
    people = result[0].get("people", {})
    assert len(people) >= 2
