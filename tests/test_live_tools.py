# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""Live integration tests against the real WikiTree API.

Gated by @pytest.mark.live — only run with ``pytest --run-live``.
Uses stable test profiles: Clemens-1 (Samuel Clemens).
"""

from __future__ import annotations

import json

import pytest

from wikitree_mcp.client import WikiTreeClient
from wikitree_mcp.tools.meta_execute import execute_operation_tool
from wikitree_mcp.tools.meta_search import search_operations_tool

pytestmark = pytest.mark.live


async def test_search_operations() -> None:
    result = await search_operations_tool({"query": "profile"})
    assert len(result) == 1
    assert "get_profile" in result[0].text


async def test_execute_get_profile(live_client: WikiTreeClient) -> None:
    result = await execute_operation_tool(
        {
            "operation": "get_profile",
            "params": {"key": "Clemens-1", "fields": "Id,Name,FirstName"},
        },
        live_client,
    )
    data = json.loads(result[0].text)
    profile = data[0]["profile"]
    assert profile["FirstName"] == "Samuel"


async def test_execute_search_person(live_client: WikiTreeClient) -> None:
    result = await execute_operation_tool(
        {
            "operation": "search_person",
            "params": {
                "first_name": "Samuel",
                "last_name": "Clemens",
                "limit": 5,
            },
        },
        live_client,
    )
    data = json.loads(result[0].text)
    assert len(data) >= 1


async def test_execute_get_people(live_client: WikiTreeClient) -> None:
    result = await execute_operation_tool(
        {
            "operation": "get_people",
            "params": {
                "keys": "Clemens-1",
                "fields": "Id,Name",
                "ancestors": 1,
            },
        },
        live_client,
    )
    data = json.loads(result[0].text)
    people = data[0].get("people", {})
    assert len(people) >= 2
