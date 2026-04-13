# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""MCP server entry point with Code Mode tool registration."""

from __future__ import annotations

import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import TextContent, ToolAnnotations
from mcp_codemode import (
    ExecuteOperationParams,
    SearchOperationsParams,
    execute_operation,
    format_search_results,
    search_operations,
)

from wikitree_mcp.client import WikiTreeClient
from wikitree_mcp.settings import Settings

# MCP-15: stdio transport uses stdout as JSON-RPC channel; log to stderr.
logging.basicConfig(level=logging.INFO, stream=sys.stderr)


@dataclass
class AppContext:
    """Lifespan context holding the shared WikiTree API client."""

    client: WikiTreeClient


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Create and tear down the WikiTree API client."""
    settings = Settings()
    client = WikiTreeClient(settings)
    try:
        yield AppContext(client=client)
    finally:
        await client.close()


def _register_tools(mcp: FastMCP) -> None:
    """Register search + execute meta-tools using library functions.

    Uses mcp.types.ToolAnnotations directly to avoid the library's
    lightweight ToolAnnotations dataclass incompatibility with newer
    FastMCP versions (library bug, tracked upstream).
    """

    @mcp.tool(
        name="search",
        description=(
            "Discover available WikiTree operations and their parameters. "
            "Call with a top-level 'query' string (not inside params). "
            "Returns matching operations with parameter schemas. "
            "Always use this before calling 'execute' to find the correct "
            "operation name."
        ),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def search(arguments: SearchOperationsParams) -> list[TextContent]:
        from wikitree_mcp.operations import OPERATION_REGISTRY

        matches = search_operations(
            arguments.query,
            OPERATION_REGISTRY,
            category=arguments.category,
        )
        text = format_search_results(matches, OPERATION_REGISTRY)
        return [TextContent(type="text", text=text)]

    @mcp.tool(
        name="execute",
        description=(
            "Run a named operation against the WikiTree API. "
            "Use 'search' first to discover the exact operation name and "
            "its params schema, then call this with "
            "{operation: '...', params: {...}}."
        ),
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        ),
    )
    async def execute(
        ctx: Context[Any, Any, Any],
        arguments: ExecuteOperationParams,
    ) -> list[Any]:
        from wikitree_mcp.operations import OPERATION_REGISTRY

        return await execute_operation(arguments.model_dump(), OPERATION_REGISTRY, ctx)


def create_server() -> FastMCP:
    """Create and configure the WikiTree MCP server."""
    from wikitree_mcp.operations import OPERATION_REGISTRY

    mcp = FastMCP("WikiTree", lifespan=app_lifespan)
    _register_tools(mcp)

    @mcp.custom_route("/health", ["GET"])
    async def health_check(request: Any) -> Any:
        """Health check endpoint for Docker HEALTHCHECK."""
        from starlette.responses import JSONResponse

        return JSONResponse(
            {
                "status": "healthy",
                "service": "WikiTree MCP Server",
                "tools": 2,
                "operations": len(OPERATION_REGISTRY),
            }
        )

    return mcp
