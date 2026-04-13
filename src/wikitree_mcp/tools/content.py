# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""Content operation handlers for WikiTree API.

Each handler takes an MCP context and validated Pydantic params,
performs the API call, and returns a list of TextContent.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from wikitree_mcp.client import WikiTreeApiError

from ._errors import raise_tool_error


async def get_bio_handler(
    ctx: Any,
    params: Any,
) -> list[TextContent]:
    """Retrieve biography text for a WikiTree profile.

    Args:
        ctx: MCP request context.
        params: Validated GetBioParams (key, bio_format).

    Returns:
        List of TextContent with JSON-formatted biography data.
    """
    client = ctx.request_context.lifespan_context.client
    try:
        result = await client.call(
            "getBio",
            key=params.key,
            bioFormat=params.bio_format,
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_bio", identifier=params.key)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_photos_handler(
    ctx: Any,
    params: Any,
) -> list[TextContent]:
    """Get photos linked to a WikiTree profile.

    Args:
        ctx: MCP request context.
        params: Validated GetPhotosParams (key, limit, start, order).

    Returns:
        List of TextContent with JSON-formatted photo data.
    """
    client = ctx.request_context.lifespan_context.client
    try:
        result = await client.call(
            "getPhotos",
            key=params.key,
            limit=params.limit,
            start=params.start,
            order=params.order,
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_photos", identifier=params.key)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_categories_handler(
    ctx: Any,
    params: Any,
) -> list[TextContent]:
    """Retrieve categories associated with a WikiTree profile.

    Args:
        ctx: MCP request context.
        params: Validated GetCategoriesParams (key).

    Returns:
        List of TextContent with JSON-formatted category data.
    """
    client = ctx.request_context.lifespan_context.client
    try:
        result = await client.call(
            "getCategories",
            key=params.key,
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_categories", identifier=params.key)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
