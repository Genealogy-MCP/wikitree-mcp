# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""Operation registry for Code Mode architecture (MCP-ORG-1 through MCP-ORG-4).

Single source of truth for all available operations. Each entry describes
an operation's name, category, parameter schema, handler function, and
behavioral hints. The ``search`` meta-tool queries this registry; the
``execute`` meta-tool dispatches to the handler.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# Import handlers from tool modules.
# These modules MUST NOT import from this module (avoids circular imports).
from .tools.content import (
    get_bio_handler,
    get_categories_handler,
    get_photos_handler,
)
from .tools.genealogy import (
    get_ancestors_handler,
    get_descendants_handler,
    get_relatives_handler,
)
from .tools.profiles import (
    get_people_handler,
    get_person_handler,
    get_profile_handler,
    search_person_handler,
)

# ---------------------------------------------------------------------------
# Pydantic parameter models
# ---------------------------------------------------------------------------


class ProfileKeyParams(BaseModel):
    """Parameters for get_profile and get_person operations."""

    key: str = Field(..., description="WikiTree ID or page name (e.g. 'Clemens-1')")
    fields: str | None = Field(None, description="Comma-separated list of fields to return")
    bio_format: str | None = Field(None, description="'wiki', 'html', or 'both'")
    resolve_redirect: int | None = Field(None, description="Set to 1 to follow redirects")


class GetPeopleParams(BaseModel):
    """Parameters for the get_people operation."""

    keys: str = Field(..., description="Comma-separated WikiTree IDs (e.g. 'Clemens-1,Twain-1')")
    fields: str | None = Field(None, description="Comma-separated list of fields to return")
    ancestors: int | None = Field(None, description="Number of ancestor generations to include")
    descendants: int | None = Field(None, description="Number of descendant generations to include")
    siblings: int | None = Field(None, description="Set to 1 to include siblings")
    nuclear: int | None = Field(
        None,
        description="Set to 1 to include nuclear family",
    )
    limit: int | None = Field(None, description="Maximum number of profiles to return")
    start: int | None = Field(None, description="Starting offset for pagination")


class SearchPersonParams(BaseModel):
    """Parameters for the search_person operation."""

    first_name: str | None = Field(None, description="First name to search for")
    last_name: str | None = Field(None, description="Last name to search for")
    birth_date: str | None = Field(
        None, description="Birth date or year (e.g. '1835' or '1835-11-30')"
    )
    death_date: str | None = Field(None, description="Death date or year")
    birth_location: str | None = Field(None, description="Birth location to search for")
    gender: str | None = Field(None, description="'Male' or 'Female'")
    limit: int | None = Field(None, description="Maximum number of results")
    start: int | None = Field(None, description="Starting offset for pagination")
    fields: str | None = Field(None, description="Comma-separated list of fields to return")


class GetAncestorsParams(BaseModel):
    """Parameters for get_ancestors operation (uses getPeople internally)."""

    key: str = Field(..., description="WikiTree ID or page name (e.g. 'Clemens-1')")
    depth: int = Field(..., description="Number of ancestor generations to retrieve")
    fields: str | None = Field(None, description="Comma-separated list of fields to return")


class GetDescendantsParams(BaseModel):
    """Parameters for get_descendants operation."""

    key: str = Field(..., description="WikiTree ID or page name (e.g. 'Clemens-1')")
    depth: int = Field(..., description="Number of descendant generations to retrieve")
    fields: str | None = Field(None, description="Comma-separated list of fields to return")
    bio_format: str | None = Field(None, description="'wiki', 'html', or 'both'")


class GetRelativesParams(BaseModel):
    """Parameters for the get_relatives operation."""

    keys: str = Field(..., description="Comma-separated WikiTree IDs (e.g. 'Clemens-1,Twain-1')")
    fields: str | None = Field(None, description="Comma-separated list of fields to return")
    get_parents: int | None = Field(None, description="Set to 1 to include parents")
    get_children: int | None = Field(None, description="Set to 1 to include children")
    get_siblings: int | None = Field(None, description="Set to 1 to include siblings")
    get_spouses: int | None = Field(None, description="Set to 1 to include spouses")


class GetBioParams(BaseModel):
    """Parameters for the get_bio operation."""

    key: str = Field(..., description="WikiTree ID or page name (e.g. 'Clemens-1')")
    bio_format: str | None = Field(None, description="'wiki', 'html', or 'both'")


class GetPhotosParams(BaseModel):
    """Parameters for the get_photos operation."""

    key: str = Field(..., description="WikiTree ID or page name (e.g. 'Clemens-1')")
    limit: int | None = Field(None, description="Maximum number of photos to return")
    start: int | None = Field(None, description="Starting offset for pagination")
    order: str | None = Field(None, description="Sort order for photos")


class GetCategoriesParams(BaseModel):
    """Parameters for the get_categories operation."""

    key: str = Field(..., description="WikiTree ID or page name (e.g. 'Clemens-1')")


# ---------------------------------------------------------------------------
# OperationEntry dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OperationEntry:
    """Describes a single operation in the registry.

    Args:
        name: Stable snake_case identifier (e.g. "get_profile").
        summary: One-line description for search results.
        description: Full description (shown on ``execute`` errors or docs).
        category: One of "search", "read", "content", "analysis".
        params_schema: Pydantic model class for parameter validation.
        handler: Async handler function that performs the operation.
        read_only: True if the operation does not mutate data.
        destructive: True if the operation deletes data.
        token_warning: Optional warning about token-heavy output.
    """

    name: str
    summary: str
    description: str
    category: str
    params_schema: type
    handler: Callable[..., Any]
    read_only: bool
    destructive: bool
    token_warning: str | None = field(default=None)


# ---------------------------------------------------------------------------
# OPERATION_REGISTRY — 10 operations
# ---------------------------------------------------------------------------

OPERATION_REGISTRY: dict[str, OperationEntry] = {
    # --- search (1) ---
    "search_person": OperationEntry(
        name="search_person",
        summary="Search WikiTree person profiles by criteria",
        description=(
            "Search WikiTree person profiles by first name, last name, "
            "birth/death date, birth location, or gender."
        ),
        category="search",
        params_schema=SearchPersonParams,
        handler=search_person_handler,
        read_only=True,
        destructive=False,
    ),
    # --- read (4) ---
    "get_profile": OperationEntry(
        name="get_profile",
        summary="Retrieve a person or free-space profile from WikiTree",
        description=(
            "Retrieve a person or free-space profile by WikiTree ID or page name. "
            "Returns profile fields including name, dates, and biography."
        ),
        category="read",
        params_schema=ProfileKeyParams,
        handler=get_profile_handler,
        read_only=True,
        destructive=False,
    ),
    "get_person": OperationEntry(
        name="get_person",
        summary="Retrieve a person profile from WikiTree (person profiles only)",
        description=(
            "Retrieve a person profile by WikiTree ID. Unlike get_profile, "
            "this only returns person profiles, not free-space profiles."
        ),
        category="read",
        params_schema=ProfileKeyParams,
        handler=get_person_handler,
        read_only=True,
        destructive=False,
    ),
    "get_people": OperationEntry(
        name="get_people",
        summary="Fetch multiple profiles by keys or relationships",
        description=(
            "Fetch multiple profiles from WikiTree by WikiTree IDs. "
            "Optionally include ancestors, descendants, siblings, or nuclear family."
        ),
        category="read",
        params_schema=GetPeopleParams,
        handler=get_people_handler,
        read_only=True,
        destructive=False,
    ),
    "get_relatives": OperationEntry(
        name="get_relatives",
        summary="Get relatives (parents, children, siblings, spouses) for profiles",
        description=(
            "Get relatives for one or more profiles. Specify which relation types "
            "to include: parents, children, siblings, spouses."
        ),
        category="read",
        params_schema=GetRelativesParams,
        handler=get_relatives_handler,
        read_only=True,
        destructive=False,
    ),
    # --- analysis (2) ---
    "get_ancestors": OperationEntry(
        name="get_ancestors",
        summary="Get ancestor tree (parents, grandparents, etc.)",
        description=(
            "Get ancestor tree for a person. Returns parents, grandparents, etc. "
            "up to the specified depth. Uses getPeople API internally "
            "(getAncestors is deprecated)."
        ),
        category="analysis",
        params_schema=GetAncestorsParams,
        handler=get_ancestors_handler,
        read_only=True,
        destructive=False,
        token_warning="Token-heavy. Use depth <= 5 to limit output.",
    ),
    "get_descendants": OperationEntry(
        name="get_descendants",
        summary="Get descendant tree (children, grandchildren, etc.)",
        description=(
            "Get descendant tree for a person. Returns children, grandchildren, etc. "
            "up to the specified depth."
        ),
        category="analysis",
        params_schema=GetDescendantsParams,
        handler=get_descendants_handler,
        read_only=True,
        destructive=False,
        token_warning="Token-heavy. Use depth <= 5 to limit output.",
    ),
    # --- content (3) ---
    "get_bio": OperationEntry(
        name="get_bio",
        summary="Retrieve biography text for a WikiTree profile",
        description=(
            "Retrieve the biography text for a WikiTree profile in wiki, HTML, or both formats."
        ),
        category="content",
        params_schema=GetBioParams,
        handler=get_bio_handler,
        read_only=True,
        destructive=False,
    ),
    "get_photos": OperationEntry(
        name="get_photos",
        summary="Get photos linked to a WikiTree profile",
        description=(
            "Get photos linked to a WikiTree profile with optional pagination and ordering."
        ),
        category="content",
        params_schema=GetPhotosParams,
        handler=get_photos_handler,
        read_only=True,
        destructive=False,
    ),
    "get_categories": OperationEntry(
        name="get_categories",
        summary="Retrieve categories associated with a WikiTree profile",
        description="Retrieve the categories associated with a WikiTree profile.",
        category="content",
        params_schema=GetCategoriesParams,
        handler=get_categories_handler,
        read_only=True,
        destructive=False,
    ),
}


# ---------------------------------------------------------------------------
# Search algorithm
# ---------------------------------------------------------------------------


def search_operations(
    query: str,
    *,
    category: str | None = None,
    max_results: int = 10,
) -> list[OperationEntry]:
    """Search the operation registry by keyword.

    Scoring:
    - +3 for exact name match
    - +2 for query token found in operation name
    - +1 for query token found in summary or description

    Args:
        query: Free-text search query.
        category: Optional category filter (search/read/content/analysis).
        max_results: Maximum number of results to return (default: 10).

    Returns:
        List of matching OperationEntry objects, ordered by score descending.
    """
    candidates = list(OPERATION_REGISTRY.values())
    if category:
        candidates = [e for e in candidates if e.category == category]

    if not query.strip():
        return candidates[:max_results]

    tokens = query.lower().split()
    scored: list[tuple[int, OperationEntry]] = []

    for entry in candidates:
        score = 0
        name_lower = entry.name.lower()
        searchable = f"{entry.summary} {entry.description}".lower()

        if query.lower() == name_lower:
            score += 3

        for token in tokens:
            if token in name_lower:
                score += 2
            if token in searchable:
                score += 1

        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [entry for _, entry in scored[:max_results]]


# ---------------------------------------------------------------------------
# Parameter summarization
# ---------------------------------------------------------------------------


def summarize_params(schema: type) -> list[dict[str, Any]]:
    """Produce a condensed parameter summary from a Pydantic model.

    Args:
        schema: A Pydantic BaseModel subclass.

    Returns:
        List of dicts with keys: name, type, required, description.
    """
    if not issubclass(schema, BaseModel):
        return []

    result: list[dict[str, Any]] = []
    for field_name, field_info in schema.model_fields.items():
        annotation = field_info.annotation
        type_str = getattr(annotation, "__name__", str(annotation))
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            values = [str(e.value) for e in annotation]
            type_str = f"{type_str}: {', '.join(values)}"
        result.append(
            {
                "name": field_name,
                "type": type_str,
                "required": field_info.is_required(),
                "description": field_info.description or "",
            }
        )
    return result
