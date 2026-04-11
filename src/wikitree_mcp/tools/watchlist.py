# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""Watchlist operation handler for WikiTree API.

Requires authentication — calls ensure_auth() before the API call.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from wikitree_mcp.client import WikiTreeApiError, WikiTreeClient

from ._errors import raise_tool_error


async def get_watchlist_handler(
    params: dict[str, Any],
    client: WikiTreeClient,
) -> list[TextContent]:
    """Get the authenticated user's watchlist from WikiTree.

    Args:
        params: Validated parameters (all optional).
        client: WikiTree API client.

    Returns:
        List of TextContent with JSON-formatted watchlist data.
    """
    try:
        await client.ensure_auth()
        result = await client.call(
            "getWatchlist",
            limit=params.get("limit"),
            offset=params.get("offset"),
            order=params.get("order"),
            getPerson=params.get("get_person"),
            getSpace=params.get("get_space"),
            onlyLiving=params.get("only_living"),
            excludeLiving=params.get("exclude_living"),
            fields=params.get("fields"),
            bioFormat=params.get("bio_format"),
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_watchlist")
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
