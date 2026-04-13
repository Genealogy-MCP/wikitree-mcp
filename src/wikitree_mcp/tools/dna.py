# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""DNA operation handlers for WikiTree API.

Each handler takes an MCP context and validated Pydantic params,
performs the API call, and returns a list of TextContent.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from wikitree_mcp.client import WikiTreeApiError

from ._errors import raise_tool_error


async def get_dna_tests_handler(
    ctx: Any,
    params: Any,
) -> list[TextContent]:
    """Get DNA tests taken by a profile.

    Args:
        ctx: MCP request context.
        params: Validated DNAKeyParams (key).

    Returns:
        List of TextContent with JSON-formatted DNA test data.
    """
    client = ctx.request_context.lifespan_context.client
    if client.settings.has_credentials:
        await client.ensure_auth()
    try:
        result = await client.call(
            "getDNATestsByTestTaker",
            key=params.key,
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_dna_tests", identifier=params.key)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_connected_profiles_handler(
    ctx: Any,
    params: Any,
) -> list[TextContent]:
    """Get profiles connected to a test-taker through a DNA test.

    Args:
        ctx: MCP request context.
        params: Validated ConnectedProfilesByDNAParams (key, dna_id).

    Returns:
        List of TextContent with JSON-formatted connection data.
    """
    client = ctx.request_context.lifespan_context.client
    if client.settings.has_credentials:
        await client.ensure_auth()
    try:
        result = await client.call(
            "getConnectedProfilesByDNATest",
            key=params.key,
            dna_id=params.dna_id,
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_connected_profiles", identifier=params.key)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_connected_dna_tests_handler(
    ctx: Any,
    params: Any,
) -> list[TextContent]:
    """Get DNA tests connected to a profile (inverse lookup).

    Args:
        ctx: MCP request context.
        params: Validated DNAKeyParams (key).

    Returns:
        List of TextContent with JSON-formatted DNA test data.
    """
    client = ctx.request_context.lifespan_context.client
    if client.settings.has_credentials:
        await client.ensure_auth()
    try:
        result = await client.call(
            "getConnectedDNATestsByProfile",
            key=params.key,
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_connected_dna_tests", identifier=params.key)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
