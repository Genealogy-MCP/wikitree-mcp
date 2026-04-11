# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""Genealogy operation handlers for WikiTree API.

Each handler takes a validated params dict and a WikiTreeClient,
performs the API call, and returns a list of TextContent.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from wikitree_mcp.client import WikiTreeApiError, WikiTreeClient

from ._errors import raise_tool_error


async def get_ancestors_handler(
    params: dict[str, Any],
    client: WikiTreeClient,
) -> list[TextContent]:
    """Get ancestor tree (parents, grandparents, etc.) from WikiTree.

    Uses getPeople with ancestors param (getAncestors is deprecated).

    Args:
        params: Validated parameters (key, depth, fields).
        client: WikiTree API client.

    Returns:
        List of TextContent with JSON-formatted ancestor data.
    """
    try:
        result = await client.call(
            "getPeople",
            keys=params["key"],
            ancestors=params["depth"],
            fields=params.get("fields"),
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_ancestors", identifier=params["key"])
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_descendants_handler(
    params: dict[str, Any],
    client: WikiTreeClient,
) -> list[TextContent]:
    """Get descendant tree (children, grandchildren, etc.) from WikiTree.

    Args:
        params: Validated parameters (key, depth, fields, bio_format).
        client: WikiTree API client.

    Returns:
        List of TextContent with JSON-formatted descendant data.
    """
    try:
        result = await client.call(
            "getDescendants",
            key=params["key"],
            depth=params["depth"],
            fields=params.get("fields"),
            bioFormat=params.get("bio_format"),
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_descendants", identifier=params["key"])
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_relatives_handler(
    params: dict[str, Any],
    client: WikiTreeClient,
) -> list[TextContent]:
    """Get relatives (parents, children, siblings, spouses) for profiles.

    Args:
        params: Validated parameters (keys, fields, get_parents, etc.).
        client: WikiTree API client.

    Returns:
        List of TextContent with JSON-formatted relatives data.
    """
    try:
        result = await client.call(
            "getRelatives",
            keys=params["keys"],
            fields=params.get("fields"),
            getParents=params.get("get_parents"),
            getChildren=params.get("get_children"),
            getSiblings=params.get("get_siblings"),
            getSpouses=params.get("get_spouses"),
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_relatives", identifier=params["keys"])
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
