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

from wikitree_mcp.client import WikiTreeClient
from wikitree_mcp.settings import Settings
from wikitree_mcp.tools.meta_execute import (
    ExecuteOperationParams,
    execute_operation_tool,
)
from wikitree_mcp.tools.meta_search import (
    SearchOperationsParams,
    search_operations_tool,
)

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


# ============================================================================
# Code Mode: 2 Meta-Tool Registration (MCP-ORG-1)
# ============================================================================

_META_TOOLS: dict[str, dict[str, Any]] = {
    "search": {
        "schema": SearchOperationsParams,
        "handler": search_operations_tool,
        "description": (
            "Discover available WikiTree operations and their parameters. "
            "Call with a top-level 'query' string (not inside params). "
            "Returns matching operations with parameter schemas. "
            "Always use this before calling 'execute' to find the correct "
            "operation name."
        ),
        "annotations": ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    },
    "execute": {
        "schema": ExecuteOperationParams,
        "handler": execute_operation_tool,
        "description": (
            "Run a named operation against the WikiTree API. "
            "Use 'search' first to discover the exact operation name and "
            "its params schema, then call this with "
            "{operation: '...', params: {...}}."
        ),
        "annotations": ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        ),
    },
}


def register_tools(app: FastMCP) -> None:
    """Register the 2 Code Mode meta-tools with FastMCP."""
    # search: no ctx needed (queries local registry only)
    search_config = _META_TOOLS["search"]
    search_handler = search_config["handler"]

    async def search(
        arguments: SearchOperationsParams,
    ) -> list[TextContent]:
        return await search_handler(arguments.model_dump())

    search.__name__ = "search"
    search.__doc__ = search_config["description"]
    app.tool(
        description=search_config["description"],
        annotations=search_config["annotations"],
    )(search)

    # execute: needs ctx to extract WikiTreeClient from lifespan
    execute_config = _META_TOOLS["execute"]
    execute_handler = execute_config["handler"]

    async def execute(
        ctx: Context[Any, Any, Any],
        arguments: ExecuteOperationParams,
    ) -> list[TextContent]:
        client = ctx.request_context.lifespan_context.client
        return await execute_handler(arguments.model_dump(), client)

    execute.__name__ = "execute"
    execute.__doc__ = execute_config["description"]
    app.tool(
        description=execute_config["description"],
        annotations=execute_config["annotations"],
    )(execute)


def create_server() -> FastMCP:
    """Create and configure the WikiTree MCP server."""
    from wikitree_mcp.operations import OPERATION_REGISTRY

    mcp = FastMCP("WikiTree", lifespan=app_lifespan)
    register_tools(mcp)

    @mcp.custom_route("/health", ["GET"])
    async def health_check(request: Any) -> Any:
        """Health check endpoint for Docker HEALTHCHECK."""
        from starlette.responses import JSONResponse

        return JSONResponse(
            {
                "status": "healthy",
                "service": "WikiTree MCP Server",
                "tools": len(_META_TOOLS),
                "operations": len(OPERATION_REGISTRY),
            }
        )

    return mcp
