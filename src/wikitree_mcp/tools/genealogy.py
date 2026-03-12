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
    async def get_ancestors(
        ctx: Context[Any, Any, Any],
        key: str,
        depth: int,
        fields: str | None = None,
        bio_format: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get ancestor tree (parents, grandparents, etc.) from WikiTree.

        Args:
            key: WikiTree ID or page name (e.g. "Clemens-1")
            depth: Number of ancestor generations to retrieve (1=parents, 2=grandparents, etc.)
            fields: Comma-separated list of fields to return
            bio_format: "wiki", "html", or "both"
        """
        client = _get_client(ctx)
        return await client.call(
            "getAncestors",
            key=key,
            depth=depth,
            fields=fields,
            bioFormat=bio_format,
        )

    @mcp.tool()
    async def get_descendants(
        ctx: Context[Any, Any, Any],
        key: str,
        depth: int,
        fields: str | None = None,
        bio_format: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get descendant tree (children, grandchildren, etc.) from WikiTree.

        Args:
            key: WikiTree ID or page name (e.g. "Clemens-1")
            depth: Number of descendant generations to retrieve
            fields: Comma-separated list of fields to return
            bio_format: "wiki", "html", or "both"
        """
        client = _get_client(ctx)
        return await client.call(
            "getDescendants",
            key=key,
            depth=depth,
            fields=fields,
            bioFormat=bio_format,
        )

    @mcp.tool()
    async def get_relatives(
        ctx: Context[Any, Any, Any],
        keys: str,
        fields: str | None = None,
        get_parents: int | None = None,
        get_children: int | None = None,
        get_siblings: int | None = None,
        get_spouses: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get relatives (parents, children, siblings, spouses) for one or more profiles.

        Args:
            keys: Comma-separated WikiTree IDs (e.g. "Clemens-1,Twain-1")
            fields: Comma-separated list of fields to return
            get_parents: Set to 1 to include parents
            get_children: Set to 1 to include children
            get_siblings: Set to 1 to include siblings
            get_spouses: Set to 1 to include spouses
        """
        client = _get_client(ctx)
        return await client.call(
            "getRelatives",
            keys=keys,
            fields=fields,
            getParents=get_parents,
            getChildren=get_children,
            getSiblings=get_siblings,
            getSpouses=get_spouses,
        )
