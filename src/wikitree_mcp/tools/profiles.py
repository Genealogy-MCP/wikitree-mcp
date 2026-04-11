# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
"""Profile operation handlers for WikiTree API.

Each handler takes a validated params dict and a WikiTreeClient,
performs the API call, and returns a list of TextContent.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from wikitree_mcp.client import WikiTreeApiError, WikiTreeClient

from ._errors import raise_tool_error


async def get_profile_handler(
    params: dict[str, Any],
    client: WikiTreeClient,
) -> list[TextContent]:
    """Retrieve a person or free-space profile from WikiTree.

    Args:
        params: Validated parameters (key, fields, bio_format, resolve_redirect).
        client: WikiTree API client.

    Returns:
        List of TextContent with JSON-formatted profile data.
    """
    try:
        result = await client.call(
            "getProfile",
            key=params["key"],
            fields=params.get("fields"),
            bioFormat=params.get("bio_format"),
            resolveRedirect=params.get("resolve_redirect"),
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_profile", identifier=params["key"])
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_person_handler(
    params: dict[str, Any],
    client: WikiTreeClient,
) -> list[TextContent]:
    """Retrieve a person profile from WikiTree (person profiles only).

    Args:
        params: Validated parameters (key, fields, bio_format, resolve_redirect).
        client: WikiTree API client.

    Returns:
        List of TextContent with JSON-formatted person data.
    """
    try:
        result = await client.call(
            "getPerson",
            key=params["key"],
            fields=params.get("fields"),
            bioFormat=params.get("bio_format"),
            resolveRedirect=params.get("resolve_redirect"),
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_person", identifier=params["key"])
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_people_handler(
    params: dict[str, Any],
    client: WikiTreeClient,
) -> list[TextContent]:
    """Fetch multiple profiles from WikiTree by keys or relationships.

    Args:
        params: Validated parameters (keys, fields, ancestors, descendants, etc.).
        client: WikiTree API client.

    Returns:
        List of TextContent with JSON-formatted profiles data.
    """
    try:
        result = await client.call(
            "getPeople",
            keys=params["keys"],
            fields=params.get("fields"),
            ancestors=params.get("ancestors"),
            descendants=params.get("descendants"),
            siblings=params.get("siblings"),
            nuclear=params.get("nuclear"),
            limit=params.get("limit"),
            start=params.get("start"),
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "get_people", identifier=params["keys"])
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def search_person_handler(
    params: dict[str, Any],
    client: WikiTreeClient,
) -> list[TextContent]:
    """Search WikiTree person profiles by criteria.

    Args:
        params: Validated parameters (first_name, last_name, birth_date, etc.).
        client: WikiTree API client.

    Returns:
        List of TextContent with JSON-formatted search results.
    """
    try:
        result = await client.call(
            "searchPerson",
            FirstName=params.get("first_name"),
            LastName=params.get("last_name"),
            BirthDate=params.get("birth_date"),
            DeathDate=params.get("death_date"),
            BirthLocation=params.get("birth_location"),
            Gender=params.get("gender"),
            limit=params.get("limit"),
            start=params.get("start"),
            fields=params.get("fields"),
        )
    except WikiTreeApiError as e:
        raise_tool_error(e, "search_person")
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
