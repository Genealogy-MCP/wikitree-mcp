# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""Tests for TOOL_REGISTRY derivation (MCP-6)."""

from wikitree_mcp.server import TOOL_REGISTRY

_EXPECTED_TOOLS = {
    "get_profile",
    "get_person",
    "get_people",
    "search_person",
    "get_ancestors",
    "get_descendants",
    "get_relatives",
    "get_bio",
    "get_photos",
    "get_categories",
}


def test_tool_registry_count() -> None:
    assert len(TOOL_REGISTRY) == 10


def test_tool_registry_names() -> None:
    assert set(TOOL_REGISTRY.keys()) == _EXPECTED_TOOLS


def test_tool_registry_descriptions_non_empty() -> None:
    for name, description in TOOL_REGISTRY.items():
        assert description, f"Tool '{name}' has an empty description"
