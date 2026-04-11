# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""DNA operation handlers for WikiTree API.

Each handler takes a validated params dict and a WikiTreeClient,
performs the API call, and returns a list of TextContent.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from wikitree_mcp.client import WikiTreeApiError, WikiTreeClient

from ._errors import raise_tool_error


async def get_dna_tests_handler(
    params: dict[str, Any],
    client: WikiTreeClient,
) -> list[TextContent]:
    """Get DNA tests taken by a profile.

    Args:
        params: Validated parameters (key).
        client: WikiTree API client.

    Returns:
        List of TextContent with JSON-formatted DNA test data.
    """
    if client.settings.has_credentials:
        await client.ensure_auth()
    try:
        result = await client.call(
            "getDNATestsByTestTaker",
            key=params["key"],
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_dna_tests", identifier=params["key"])
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_connected_profiles_handler(
    params: dict[str, Any],
    client: WikiTreeClient,
) -> list[TextContent]:
    """Get profiles connected to a test-taker through a DNA test.

    Args:
        params: Validated parameters (key, dna_id).
        client: WikiTree API client.

    Returns:
        List of TextContent with JSON-formatted connection data.
    """
    if client.settings.has_credentials:
        await client.ensure_auth()
    try:
        result = await client.call(
            "getConnectedProfilesByDNATest",
            key=params["key"],
            dna_id=params["dna_id"],
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_connected_profiles", identifier=params["key"])
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_connected_dna_tests_handler(
    params: dict[str, Any],
    client: WikiTreeClient,
) -> list[TextContent]:
    """Get DNA tests connected to a profile (inverse lookup).

    Args:
        params: Validated parameters (key).
        client: WikiTree API client.

    Returns:
        List of TextContent with JSON-formatted DNA test data.
    """
    if client.settings.has_credentials:
        await client.ensure_auth()
    try:
        result = await client.call(
            "getConnectedDNATestsByProfile",
            key=params["key"],
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_connected_dna_tests", identifier=params["key"])
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
