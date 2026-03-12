# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import Context, FastMCP

from wikitree_mcp.client import WikiTreeClient


def _get_client(ctx: Context[Any, Any, Any]) -> WikiTreeClient:
    return ctx.request_context.lifespan_context.client  # type: ignore[no-any-return]


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def get_bio(
        ctx: Context[Any, Any, Any],
        key: str,
        bio_format: str | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve biography text for a WikiTree profile.

        Args:
            key: WikiTree ID or page name (e.g. "Clemens-1")
            bio_format: "wiki", "html", or "both"
        """
        client = _get_client(ctx)
        return await client.call("getBio", key=key, bioFormat=bio_format)

    @mcp.tool()
    async def get_photos(
        ctx: Context[Any, Any, Any],
        key: str,
        limit: int | None = None,
        start: int | None = None,
        order: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get photos linked to a WikiTree profile.

        Args:
            key: WikiTree ID or page name (e.g. "Clemens-1")
            limit: Maximum number of photos to return
            start: Starting offset for pagination
            order: Sort order for photos
        """
        client = _get_client(ctx)
        return await client.call("getPhotos", key=key, limit=limit, start=start, order=order)

    @mcp.tool()
    async def get_categories(
        ctx: Context[Any, Any, Any],
        key: str,
    ) -> list[dict[str, Any]]:
        """Retrieve categories associated with a WikiTree profile.

        Args:
            key: WikiTree ID or page name (e.g. "Clemens-1")
        """
        client = _get_client(ctx)
        return await client.call("getCategories", key=key)
