# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""Watchlist operation handler for WikiTree API.

Requires authentication -- calls ensure_auth() before the API call.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from wikitree_mcp.client import WikiTreeApiError

from ._errors import raise_tool_error


async def get_watchlist_handler(
    ctx: Any,
    params: Any,
) -> list[TextContent]:
    """Get the authenticated user's watchlist from WikiTree.

    Args:
        ctx: MCP request context.
        params: Validated GetWatchlistParams (all optional).

    Returns:
        List of TextContent with JSON-formatted watchlist data.
    """
    client = ctx.request_context.lifespan_context.client
    try:
        await client.ensure_auth()
        result = await client.call(
            "getWatchlist",
            limit=params.limit,
            offset=params.offset,
            order=params.order,
            getPerson=params.get_person,
            getSpace=params.get_space,
            onlyLiving=params.only_living,
            excludeLiving=params.exclude_living,
            fields=params.fields,
            bioFormat=params.bio_format,
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_watchlist")
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
