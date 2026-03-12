# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP

from wikitree_mcp.client import WikiTreeClient
from wikitree_mcp.settings import Settings


@dataclass
class AppContext:
    client: WikiTreeClient


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    settings = Settings()
    client = WikiTreeClient(settings)
    try:
        yield AppContext(client=client)
    finally:
        await client.close()


def create_server() -> FastMCP:
    mcp = FastMCP("WikiTree", lifespan=app_lifespan)

    from wikitree_mcp.tools import content, genealogy, profiles

    profiles.register(mcp)
    genealogy.register(mcp)
    content.register(mcp)

    return mcp
