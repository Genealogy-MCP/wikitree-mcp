# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from __future__ import annotations

"""Unit tests for MCP tool error formatting (MCP-8, MCP-9, MCP-10)."""

import pytest

from wikitree_mcp.client import WikiTreeApiError
from wikitree_mcp.tools._errors import McpToolError, raise_tool_error


class TestRaiseToolError:
    def test_api_error_preserves_message(self) -> None:
        with pytest.raises(McpToolError, match="Permission Denied"):
            raise_tool_error(WikiTreeApiError("Permission Denied"), "get profile")

    def test_identifier_appended_to_message(self) -> None:
        with pytest.raises(McpToolError, match="Clemens-1"):
            raise_tool_error(
                WikiTreeApiError("Not found"),
                "get profile",
                identifier="Clemens-1",
            )

    def test_mcp_tool_error_passthrough(self) -> None:
        original = McpToolError("already formatted")
        with pytest.raises(McpToolError, match="already formatted"):
            raise_tool_error(original, "operation")

    def test_unexpected_error_uses_str(self) -> None:
        with pytest.raises(McpToolError, match="connection refused"):
            raise_tool_error(ConnectionError("connection refused"), "get bio")

    def test_raises_mcp_tool_error_not_original(self) -> None:
        with pytest.raises(McpToolError):
            raise_tool_error(WikiTreeApiError("upstream"), "test op")

    def test_chained_exception_preserved(self) -> None:
        original = WikiTreeApiError("upstream")
        try:
            raise_tool_error(original, "test op")
        except McpToolError as exc:
            assert exc.__cause__ is original


class TestMcpToolError:
    def test_is_exception(self) -> None:
        err = McpToolError("bad thing happened")
        assert isinstance(err, Exception)
        assert str(err) == "bad thing happened"
