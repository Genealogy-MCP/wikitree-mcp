# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""Genealogy operation handlers for WikiTree API.

Each handler takes an MCP context and validated Pydantic params,
performs the API call, and returns a list of TextContent.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from wikitree_mcp.client import WikiTreeApiError

from ._errors import raise_tool_error


async def get_ancestors_handler(
    ctx: Any,
    params: Any,
) -> list[TextContent]:
    """Get ancestor tree (parents, grandparents, etc.) from WikiTree.

    Uses getPeople with ancestors param (getAncestors is deprecated).

    Args:
        ctx: MCP request context.
        params: Validated GetAncestorsParams (key, depth, fields).

    Returns:
        List of TextContent with JSON-formatted ancestor data.
    """
    client = ctx.request_context.lifespan_context.client
    try:
        result = await client.call(
            "getPeople",
            keys=params.key,
            ancestors=params.depth,
            fields=params.fields,
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_ancestors", identifier=params.key)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_descendants_handler(
    ctx: Any,
    params: Any,
) -> list[TextContent]:
    """Get descendant tree (children, grandchildren, etc.) from WikiTree.

    Args:
        ctx: MCP request context.
        params: Validated GetDescendantsParams (key, depth, fields, bio_format).

    Returns:
        List of TextContent with JSON-formatted descendant data.
    """
    client = ctx.request_context.lifespan_context.client
    try:
        result = await client.call(
            "getDescendants",
            key=params.key,
            depth=params.depth,
            fields=params.fields,
            bioFormat=params.bio_format,
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_descendants", identifier=params.key)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_relatives_handler(
    ctx: Any,
    params: Any,
) -> list[TextContent]:
    """Get relatives (parents, children, siblings, spouses) for profiles.

    Args:
        ctx: MCP request context.
        params: Validated GetRelativesParams (keys, fields, get_parents, etc.).

    Returns:
        List of TextContent with JSON-formatted relatives data.
    """
    client = ctx.request_context.lifespan_context.client
    try:
        result = await client.call(
            "getRelatives",
            keys=params.keys,
            fields=params.fields,
            getParents=params.get_parents,
            getChildren=params.get_children,
            getSiblings=params.get_siblings,
            getSpouses=params.get_spouses,
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_relatives", identifier=params.keys)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
