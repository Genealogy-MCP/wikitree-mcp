# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from __future__ import annotations

import pytest

from wikitree_mcp.client import WikiTreeApiError
from wikitree_mcp.tools._errors import McpToolError, raise_tool_error


def test_mcp_tool_error_is_exception() -> None:
    assert issubclass(McpToolError, Exception)


def test_raise_tool_error_with_api_error() -> None:
    api_err = WikiTreeApiError("Profile not found")
    with pytest.raises(McpToolError, match="Profile not found"):
        raise_tool_error(api_err, "get_profile")


def test_raise_tool_error_with_mcp_tool_error() -> None:
    mcp_err = McpToolError("Already formatted error")
    with pytest.raises(McpToolError, match="Already formatted error"):
        raise_tool_error(mcp_err, "get_profile")


def test_raise_tool_error_with_generic_exception() -> None:
    err = RuntimeError("connection reset")
    with pytest.raises(McpToolError, match="Unexpected error during get_profile: connection reset"):
        raise_tool_error(err, "get_profile")


def test_raise_tool_error_appends_identifier() -> None:
    api_err = WikiTreeApiError("Not found")
    with pytest.raises(McpToolError, match=r"Not found \[id: Clemens-1\]"):
        raise_tool_error(api_err, "get_profile", identifier="Clemens-1")


def test_raise_tool_error_chains_original_exception() -> None:
    original = WikiTreeApiError("API down")
    with pytest.raises(McpToolError) as exc_info:
        raise_tool_error(original, "get_profile")
    assert exc_info.value.__cause__ is original
