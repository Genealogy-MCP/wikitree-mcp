# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from __future__ import annotations

import pytest
from pydantic import BaseModel

from wikitree_mcp.operations import (
    OPERATION_REGISTRY,
    search_operations,
    summarize_params,
)

# ---------------------------------------------------------------------------
# Registry completeness
# ---------------------------------------------------------------------------


def test_registry_has_13_entries() -> None:
    assert len(OPERATION_REGISTRY) == 13


def test_all_operations_read_only() -> None:
    for entry in OPERATION_REGISTRY.values():
        assert entry.read_only is True, f"{entry.name} should be read_only"


def test_all_operations_not_destructive() -> None:
    for entry in OPERATION_REGISTRY.values():
        assert entry.destructive is False, f"{entry.name} should not be destructive"


def test_every_entry_has_callable_handler() -> None:
    for entry in OPERATION_REGISTRY.values():
        assert callable(entry.handler), f"{entry.name} handler is not callable"


def test_every_entry_has_pydantic_params_schema() -> None:
    for entry in OPERATION_REGISTRY.values():
        assert issubclass(entry.params_schema, BaseModel), (
            f"{entry.name} params_schema is not a BaseModel subclass"
        )


def test_entry_names_match_keys() -> None:
    for key, entry in OPERATION_REGISTRY.items():
        assert key == entry.name, f"Key '{key}' != entry.name '{entry.name}'"


def test_valid_categories() -> None:
    valid = {"search", "read", "analysis", "content", "dna"}
    for entry in OPERATION_REGISTRY.values():
        assert entry.category in valid, f"{entry.name} has invalid category '{entry.category}'"


def test_token_warnings_on_analysis_ops() -> None:
    for name in ("get_ancestors", "get_descendants"):
        entry = OPERATION_REGISTRY[name]
        assert entry.token_warning is not None, f"{name} should have a token_warning"


# ---------------------------------------------------------------------------
# search_operations()
# ---------------------------------------------------------------------------


def test_search_exact_name_match() -> None:
    results = search_operations("get_profile")
    assert len(results) > 0
    assert results[0].name == "get_profile"


def test_search_partial_token_match() -> None:
    results = search_operations("ancestors")
    names = [r.name for r in results]
    assert "get_ancestors" in names


def test_search_no_match_returns_empty() -> None:
    results = search_operations("xyznonexistent")
    assert results == []


def test_search_category_filter() -> None:
    results = search_operations("", category="analysis")
    names = [r.name for r in results]
    assert set(names) == {"get_ancestors", "get_descendants"}


def test_search_category_filter_excludes_others() -> None:
    results = search_operations("", category="search")
    for entry in results:
        assert entry.category == "search"


def test_search_max_results() -> None:
    results = search_operations("get", max_results=2)
    assert len(results) <= 2


# ---------------------------------------------------------------------------
# summarize_params()
# ---------------------------------------------------------------------------


def test_summarize_params_required_and_optional() -> None:
    from wikitree_mcp.operations import ProfileKeyParams

    summary = summarize_params(ProfileKeyParams)
    names = {p["name"] for p in summary}
    assert "key" in names

    key_param = next(p for p in summary if p["name"] == "key")
    assert key_param["required"] is True

    optional_params = [p for p in summary if p["name"] != "key"]
    for p in optional_params:
        assert p["required"] is False


def test_summarize_params_non_model_returns_empty() -> None:
    assert summarize_params(str) == []


# ---------------------------------------------------------------------------
# Param model validation
# ---------------------------------------------------------------------------


def test_profile_key_params_requires_key() -> None:
    from wikitree_mcp.operations import ProfileKeyParams

    with pytest.raises(ValueError):
        ProfileKeyParams()  # type: ignore[call-arg]

    result = ProfileKeyParams(key="Clemens-1")
    assert result.key == "Clemens-1"


def test_get_people_params_requires_keys() -> None:
    from wikitree_mcp.operations import GetPeopleParams

    with pytest.raises(ValueError):
        GetPeopleParams()  # type: ignore[call-arg]

    result = GetPeopleParams(keys="Clemens-1,Twain-1")
    assert result.keys == "Clemens-1,Twain-1"


def test_search_person_params_all_optional() -> None:
    from wikitree_mcp.operations import SearchPersonParams

    result = SearchPersonParams()
    assert result.first_name is None


def test_get_ancestors_params_requires_key_and_depth() -> None:
    from wikitree_mcp.operations import GetAncestorsParams

    with pytest.raises(ValueError):
        GetAncestorsParams()  # type: ignore[call-arg]

    result = GetAncestorsParams(key="Clemens-1", depth=3)
    assert result.depth == 3


def test_get_descendants_params_requires_key_and_depth() -> None:
    from wikitree_mcp.operations import GetDescendantsParams

    with pytest.raises(ValueError):
        GetDescendantsParams()  # type: ignore[call-arg]

    result = GetDescendantsParams(key="Clemens-1", depth=3)
    assert result.depth == 3


def test_get_relatives_params_requires_keys() -> None:
    from wikitree_mcp.operations import GetRelativesParams

    with pytest.raises(ValueError):
        GetRelativesParams()  # type: ignore[call-arg]


def test_get_bio_params_requires_key() -> None:
    from wikitree_mcp.operations import GetBioParams

    with pytest.raises(ValueError):
        GetBioParams()  # type: ignore[call-arg]


def test_get_photos_params_requires_key() -> None:
    from wikitree_mcp.operations import GetPhotosParams

    with pytest.raises(ValueError):
        GetPhotosParams()  # type: ignore[call-arg]


def test_get_categories_params_requires_key() -> None:
    from wikitree_mcp.operations import GetCategoriesParams

    with pytest.raises(ValueError):
        GetCategoriesParams()  # type: ignore[call-arg]


def test_dna_key_params_requires_key() -> None:
    from wikitree_mcp.operations import DNAKeyParams

    with pytest.raises(ValueError):
        DNAKeyParams()  # type: ignore[call-arg]

    result = DNAKeyParams(key="Whitten-1")
    assert result.key == "Whitten-1"


def test_connected_profiles_params_requires_key_and_dna_id() -> None:
    from wikitree_mcp.operations import ConnectedProfilesByDNAParams

    with pytest.raises(ValueError):
        ConnectedProfilesByDNAParams()  # type: ignore[call-arg]

    with pytest.raises(ValueError):
        ConnectedProfilesByDNAParams(key="Whitten-1")  # type: ignore[call-arg]

    result = ConnectedProfilesByDNAParams(key="Whitten-1", dna_id=1)
    assert result.dna_id == 1
