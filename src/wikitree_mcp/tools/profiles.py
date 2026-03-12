from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import Context, FastMCP

from wikitree_mcp.client import WikiTreeClient


def _get_client(ctx: Context[Any, Any, Any]) -> WikiTreeClient:
    return ctx.request_context.lifespan_context.client  # type: ignore[no-any-return]


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def get_profile(
        ctx: Context[Any, Any, Any],
        key: str,
        fields: str | None = None,
        bio_format: str | None = None,
        resolve_redirect: int | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve a person or free-space profile from WikiTree.

        Args:
            key: WikiTree ID or page name (e.g. "Clemens-1")
            fields: Comma-separated list of fields to return
            bio_format: "wiki", "html", or "both"
            resolve_redirect: Set to 1 to follow redirects
        """
        client = _get_client(ctx)
        return await client.call(
            "getProfile",
            key=key,
            fields=fields,
            bioFormat=bio_format,
            resolveRedirect=resolve_redirect,
        )

    @mcp.tool()
    async def get_person(
        ctx: Context[Any, Any, Any],
        key: str,
        fields: str | None = None,
        bio_format: str | None = None,
        resolve_redirect: int | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve a person profile from WikiTree (person profiles only).

        Args:
            key: WikiTree ID or page name (e.g. "Clemens-1")
            fields: Comma-separated list of fields to return
            bio_format: "wiki", "html", or "both"
            resolve_redirect: Set to 1 to follow redirects
        """
        client = _get_client(ctx)
        return await client.call(
            "getPerson",
            key=key,
            fields=fields,
            bioFormat=bio_format,
            resolveRedirect=resolve_redirect,
        )

    @mcp.tool()
    async def get_people(
        ctx: Context[Any, Any, Any],
        keys: str,
        fields: str | None = None,
        ancestors: int | None = None,
        descendants: int | None = None,
        siblings: int | None = None,
        nuclear: int | None = None,
        limit: int | None = None,
        start: int | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch multiple profiles from WikiTree by keys or relationships.

        Args:
            keys: Comma-separated WikiTree IDs (e.g. "Clemens-1,Twain-1")
            fields: Comma-separated list of fields to return
            ancestors: Number of ancestor generations to include
            descendants: Number of descendant generations to include
            siblings: Set to 1 to include siblings
            nuclear: Set to 1 to include nuclear family (parents, siblings, spouses, children)
            limit: Maximum number of profiles to return
            start: Starting offset for pagination
        """
        client = _get_client(ctx)
        return await client.call(
            "getPeople",
            keys=keys,
            fields=fields,
            ancestors=ancestors,
            descendants=descendants,
            siblings=siblings,
            nuclear=nuclear,
            limit=limit,
            start=start,
        )

    @mcp.tool()
    async def search_person(
        ctx: Context[Any, Any, Any],
        first_name: str | None = None,
        last_name: str | None = None,
        birth_date: str | None = None,
        death_date: str | None = None,
        birth_location: str | None = None,
        gender: str | None = None,
        limit: int | None = None,
        start: int | None = None,
        fields: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search WikiTree person profiles by criteria.

        Args:
            first_name: First name to search for
            last_name: Last name to search for
            birth_date: Birth date or year (e.g. "1835" or "1835-11-30")
            death_date: Death date or year
            birth_location: Birth location to search for
            gender: "Male" or "Female"
            limit: Maximum number of results
            start: Starting offset for pagination
            fields: Comma-separated list of fields to return
        """
        client = _get_client(ctx)
        return await client.call(
            "searchPerson",
            FirstName=first_name,
            LastName=last_name,
            BirthDate=birth_date,
            DeathDate=death_date,
            BirthLocation=birth_location,
            Gender=gender,
            limit=limit,
            start=start,
            fields=fields,
        )
