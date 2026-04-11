# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""Content operation handlers for WikiTree API.

Each handler takes a validated params dict and a WikiTreeClient,
performs the API call, and returns a list of TextContent.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from wikitree_mcp.client import WikiTreeApiError, WikiTreeClient

from ._errors import raise_tool_error


async def get_bio_handler(
    params: dict[str, Any],
    client: WikiTreeClient,
) -> list[TextContent]:
    """Retrieve biography text for a WikiTree profile.

    Args:
        params: Validated parameters (key, bio_format).
        client: WikiTree API client.

    Returns:
        List of TextContent with JSON-formatted biography data.
    """
    try:
        result = await client.call(
            "getBio",
            key=params["key"],
            bioFormat=params.get("bio_format"),
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_bio", identifier=params["key"])
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_photos_handler(
    params: dict[str, Any],
    client: WikiTreeClient,
) -> list[TextContent]:
    """Get photos linked to a WikiTree profile.

    Args:
        params: Validated parameters (key, limit, start, order).
        client: WikiTree API client.

    Returns:
        List of TextContent with JSON-formatted photo data.
    """
    try:
        result = await client.call(
            "getPhotos",
            key=params["key"],
            limit=params.get("limit"),
            start=params.get("start"),
            order=params.get("order"),
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_photos", identifier=params["key"])
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_categories_handler(
    params: dict[str, Any],
    client: WikiTreeClient,
) -> list[TextContent]:
    """Retrieve categories associated with a WikiTree profile.

    Args:
        params: Validated parameters (key).
        client: WikiTree API client.

    Returns:
        List of TextContent with JSON-formatted category data.
    """
    try:
        result = await client.call(
            "getCategories",
            key=params["key"],
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_categories", identifier=params["key"])
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
