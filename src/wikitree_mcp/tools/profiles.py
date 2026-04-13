# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""Profile operation handlers for WikiTree API.

Each handler takes an MCP context and validated Pydantic params,
performs the API call, and returns a list of TextContent.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from wikitree_mcp.client import WikiTreeApiError

from ._errors import raise_tool_error


async def get_profile_handler(
    ctx: Any,
    params: Any,
) -> list[TextContent]:
    """Retrieve a person or free-space profile from WikiTree.

    Args:
        ctx: MCP request context.
        params: Validated ProfileKeyParams (key, fields, bio_format, resolve_redirect).

    Returns:
        List of TextContent with JSON-formatted profile data.
    """
    client = ctx.request_context.lifespan_context.client
    try:
        result = await client.call(
            "getProfile",
            key=params.key,
            fields=params.fields,
            bioFormat=params.bio_format,
            resolveRedirect=params.resolve_redirect,
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_profile", identifier=params.key)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_person_handler(
    ctx: Any,
    params: Any,
) -> list[TextContent]:
    """Retrieve a person profile from WikiTree (person profiles only).

    Args:
        ctx: MCP request context.
        params: Validated ProfileKeyParams (key, fields, bio_format, resolve_redirect).

    Returns:
        List of TextContent with JSON-formatted person data.
    """
    client = ctx.request_context.lifespan_context.client
    try:
        result = await client.call(
            "getPerson",
            key=params.key,
            fields=params.fields,
            bioFormat=params.bio_format,
            resolveRedirect=params.resolve_redirect,
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_person", identifier=params.key)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_people_handler(
    ctx: Any,
    params: Any,
) -> list[TextContent]:
    """Fetch multiple profiles from WikiTree by keys or relationships.

    Args:
        ctx: MCP request context.
        params: Validated GetPeopleParams (keys, fields, ancestors, descendants, etc.).

    Returns:
        List of TextContent with JSON-formatted profiles data.
    """
    client = ctx.request_context.lifespan_context.client
    try:
        result = await client.call(
            "getPeople",
            keys=params.keys,
            fields=params.fields,
            ancestors=params.ancestors,
            descendants=params.descendants,
            siblings=params.siblings,
            nuclear=params.nuclear,
            limit=params.limit,
            start=params.start,
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_people", identifier=params.keys)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def search_person_handler(
    ctx: Any,
    params: Any,
) -> list[TextContent]:
    """Search WikiTree person profiles by criteria.

    Args:
        ctx: MCP request context.
        params: Validated SearchPersonParams (first_name, last_name, birth_date, etc.).

    Returns:
        List of TextContent with JSON-formatted search results.
    """
    client = ctx.request_context.lifespan_context.client
    try:
        result = await client.call(
            "searchPerson",
            FirstName=params.first_name,
            LastName=params.last_name,
            BirthDate=params.birth_date,
            DeathDate=params.death_date,
            BirthLocation=params.birth_location,
            Gender=params.gender,
            limit=params.limit,
            start=params.start,
            fields=params.fields,
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "search_person")
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
