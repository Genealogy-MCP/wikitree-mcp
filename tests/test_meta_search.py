# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from __future__ import annotations

from mcp.types import TextContent

from wikitree_mcp.tools.meta_search import search_operations_tool


async def test_search_returns_text_content() -> None:
    result = await search_operations_tool({"query": "profile"})
    assert isinstance(result, list)
    assert all(isinstance(r, TextContent) for r in result)


async def test_search_keyword_match() -> None:
    result = await search_operations_tool({"query": "ancestors"})
    assert len(result) == 1
    assert "get_ancestors" in result[0].text


async def test_search_no_match_lists_all() -> None:
    result = await search_operations_tool({"query": "xyznonexistent"})
    assert len(result) == 1
    assert "14 operations available" in result[0].text


async def test_search_category_filter() -> None:
    result = await search_operations_tool({"query": "", "category": "analysis"})
    assert len(result) == 1
    text = result[0].text
    assert "get_ancestors" in text
    assert "get_descendants" in text


async def test_search_shows_token_warning() -> None:
    result = await search_operations_tool({"query": "get_ancestors"})
    assert "WARNING" in result[0].text


async def test_search_shows_parameters() -> None:
    result = await search_operations_tool({"query": "get_bio"})
    assert "key" in result[0].text
    assert "required" in result[0].text
