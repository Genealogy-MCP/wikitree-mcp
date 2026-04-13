# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""Tests for the search meta-tool via FastMCP (backed by mcp-codemode library)."""

from __future__ import annotations

from typing import Any

from mcp_codemode import SearchOperationsParams

from wikitree_mcp.server import create_server


def _find_tool(mcp: Any, name: str) -> Any:
    """Extract a registered tool from FastMCP by name."""
    for tool in mcp._tool_manager._tools.values():
        if tool.name == name:
            return tool
    raise ValueError(f"Tool {name} not found")


def _extract_text(result: Any) -> str:
    """Extract text from tool result (handles various return types)."""
    if isinstance(result, str):
        return result
    if isinstance(result, list) and result:
        return "\n".join(getattr(item, "text", str(item)) for item in result)
    return str(result)


async def test_search_returns_text_content() -> None:
    mcp = create_server()
    tool = _find_tool(mcp, "search")
    result = await tool.fn(arguments=SearchOperationsParams(query="profile"))
    assert isinstance(result, list)
    assert len(result) > 0


async def test_search_keyword_match() -> None:
    mcp = create_server()
    tool = _find_tool(mcp, "search")
    result = _extract_text(await tool.fn(arguments=SearchOperationsParams(query="ancestors")))
    assert "get_ancestors" in result


async def test_search_no_match_lists_all() -> None:
    mcp = create_server()
    tool = _find_tool(mcp, "search")
    result = _extract_text(await tool.fn(arguments=SearchOperationsParams(query="xyznonexistent")))
    assert "No operations matched" in result


async def test_search_category_filter() -> None:
    mcp = create_server()
    tool = _find_tool(mcp, "search")
    result = _extract_text(
        await tool.fn(arguments=SearchOperationsParams(query="", category="analysis"))
    )
    assert "get_ancestors" in result
    assert "get_descendants" in result


async def test_search_shows_token_warning() -> None:
    mcp = create_server()
    tool = _find_tool(mcp, "search")
    result = _extract_text(await tool.fn(arguments=SearchOperationsParams(query="get_ancestors")))
    assert "token" in result.lower() or "WARNING" in result or "Note" in result


async def test_search_shows_parameters() -> None:
    mcp = create_server()
    tool = _find_tool(mcp, "search")
    result = _extract_text(await tool.fn(arguments=SearchOperationsParams(query="get_bio")))
    assert "key" in result
    assert "required" in result.lower() or "str" in result
