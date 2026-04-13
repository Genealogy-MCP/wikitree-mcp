# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""Live integration tests against the real WikiTree API.

Gated by @pytest.mark.live -- only run with ``pytest --run-live``.
Uses stable test profiles: Clemens-1 (Samuel Clemens).
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock

import pytest
from mcp_codemode import (
    execute_operation,
    format_search_results,
    search_operations,
)

from wikitree_mcp.client import WikiTreeClient
from wikitree_mcp.operations import OPERATION_REGISTRY
from wikitree_mcp.server import AppContext

pytestmark = pytest.mark.live


def _make_ctx(client: WikiTreeClient) -> MagicMock:
    """Build a mock context wrapping a real WikiTreeClient."""
    ctx = MagicMock()
    ctx.request_context.lifespan_context = AppContext(client=client)
    return ctx


async def test_search_operations() -> None:
    matches = search_operations("profile", OPERATION_REGISTRY)
    text = format_search_results(matches, OPERATION_REGISTRY)
    assert "get_profile" in text


async def test_execute_get_profile(live_client: WikiTreeClient) -> None:
    ctx = _make_ctx(live_client)
    args: dict[str, Any] = {
        "operation": "get_profile",
        "params": {"key": "Clemens-1", "fields": "Id,Name,FirstName"},
    }
    result = await execute_operation(args, OPERATION_REGISTRY, ctx)
    data = json.loads(result[0].text)
    profile = data[0]["profile"]
    assert profile["FirstName"] == "Samuel"


async def test_execute_search_person(live_client: WikiTreeClient) -> None:
    ctx = _make_ctx(live_client)
    args: dict[str, Any] = {
        "operation": "search_person",
        "params": {
            "first_name": "Samuel",
            "last_name": "Clemens",
            "limit": 5,
        },
    }
    result = await execute_operation(args, OPERATION_REGISTRY, ctx)
    data = json.loads(result[0].text)
    assert len(data) >= 1


async def test_execute_get_ancestors(live_client: WikiTreeClient) -> None:
    ctx = _make_ctx(live_client)
    args: dict[str, Any] = {
        "operation": "get_ancestors",
        "params": {"key": "Clemens-1", "depth": 1, "fields": "Id,Name"},
    }
    result = await execute_operation(args, OPERATION_REGISTRY, ctx)
    data = json.loads(result[0].text)
    people = data[0].get("people", {})
    assert len(people) >= 2


async def test_execute_get_people(live_client: WikiTreeClient) -> None:
    ctx = _make_ctx(live_client)
    args: dict[str, Any] = {
        "operation": "get_people",
        "params": {
            "keys": "Clemens-1",
            "fields": "Id,Name",
            "ancestors": 1,
        },
    }
    result = await execute_operation(args, OPERATION_REGISTRY, ctx)
    data = json.loads(result[0].text)
    people = data[0].get("people", {})
    assert len(people) >= 2
