# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""MCP ``execute`` meta-tool -- runs a validated operation from the registry.

Part of the Code Mode architecture (MCP-ORG-1). The LLM discovers operations
via ``search``, then calls this tool to run one. Each operation is validated
via its Pydantic schema before dispatching to the handler.
"""

from __future__ import annotations

import difflib
from typing import Any

from mcp.types import TextContent
from pydantic import BaseModel, Field

from ..operations import OPERATION_REGISTRY
from ._errors import McpToolError


class ExecuteOperationParams(BaseModel):
    """Input schema for the execute meta-tool."""

    operation: str = Field(
        ...,
        description=(
            "Name of the operation to run. Use the 'search' meta-tool "
            "first to discover available operations and their parameters."
        ),
    )
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters for the operation (see operation schema).",
    )


async def execute_operation_tool(
    arguments: dict[str, Any],
    client: Any,
) -> list[TextContent]:
    """Execute a named operation from the registry.

    Args:
        arguments: Dict with 'operation' and 'params'.
        client: WikiTreeClient instance from the lifespan context.

    Returns:
        List of TextContent from the operation handler.

    Raises:
        McpToolError: If the operation is unknown or params are invalid.
    """
    validated = ExecuteOperationParams(**arguments)

    entry = OPERATION_REGISTRY.get(validated.operation)
    if entry is None:
        attempted = validated.operation
        close = difflib.get_close_matches(
            attempted,
            OPERATION_REGISTRY.keys(),
            n=3,
            cutoff=0.4,
        )
        suggestion = ""
        if close:
            suggestion = f" Did you mean: {', '.join(close)}?"
        raise McpToolError(
            f"Unknown operation '{attempted}'.{suggestion} "
            "Use the 'search' tool to discover available operations."
        )

    try:
        entry.params_schema(**validated.params)
    except Exception as e:
        raise McpToolError(f"Invalid parameters for '{validated.operation}': {e}") from e

    return await entry.handler(validated.params, client)
