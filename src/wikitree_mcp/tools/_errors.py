# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from __future__ import annotations

"""Shared error handling for MCP tool responses.

MCP-8: Tool execution errors MUST be returned with isError=True so the LLM
can distinguish errors from valid data and self-correct. The MCP Server SDK
automatically sets isError=True when a tool handler raises an exception.

MCP-10: This is the single source of truth for error formatting.
"""

import logging
from typing import NoReturn

from wikitree_mcp.client import WikiTreeApiError

logger = logging.getLogger(__name__)


class McpToolError(Exception):
    """Raised by tool handlers to signal an error to the LLM.

    The MCP Server SDK catches exceptions from tool handlers and wraps them
    in CallToolResult with isError=True. This exception provides a clean,
    user-facing error message for that purpose.
    """


def raise_tool_error(
    error: Exception,
    operation: str,
    *,
    identifier: str | None = None,
) -> NoReturn:
    """Log and re-raise an exception as McpToolError.

    The MCP Server framework catches this and returns the message to the LLM
    with isError=True, allowing it to self-correct.

    Args:
        error: The original exception.
        operation: Human-readable description of the failed operation
            (e.g. "get profile", "search person").
        identifier: Optional WikiTree key or ID for context.

    Raises:
        McpToolError: Always raised with a formatted error message.
    """
    if isinstance(error, WikiTreeApiError):
        error_msg = str(error)
    elif isinstance(error, McpToolError):
        error_msg = str(error)
    else:
        error_msg = str(error) if str(error) else f"Unexpected error during {operation}"

    # MCP-9: Append key context when available
    if identifier:
        error_msg += f" [key: {identifier}]"

    logger.error("Tool error in %s: %s", operation, error_msg)
    raise McpToolError(error_msg) from error
