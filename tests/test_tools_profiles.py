# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from wikitree_mcp.client import WikiTreeApiError, WikiTreeClient
from wikitree_mcp.tools._errors import McpToolError
from wikitree_mcp.tools.profiles import (
    get_people_handler,
    get_person_handler,
    get_profile_handler,
    search_person_handler,
)


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=WikiTreeClient)


async def test_get_profile(mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"page_name": "Clemens-1", "status": 0}]
    result = await get_profile_handler({"key": "Clemens-1", "fields": "Id,Name"}, mock_client)
    mock_client.call.assert_called_once_with(
        "getProfile",
        key="Clemens-1",
        fields="Id,Name",
        bioFormat=None,
        resolveRedirect=None,
    )
    assert len(result) == 1
    assert json.loads(result[0].text) == [{"page_name": "Clemens-1", "status": 0}]


async def test_get_person(mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"page_name": "Clemens-1", "status": 0}]
    result = await get_person_handler({"key": "Clemens-1", "bio_format": "wiki"}, mock_client)
    mock_client.call.assert_called_once_with(
        "getPerson",
        key="Clemens-1",
        fields=None,
        bioFormat="wiki",
        resolveRedirect=None,
    )
    assert len(result) == 1


async def test_get_people(mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"status": 0}]
    result = await get_people_handler({"keys": "Clemens-1,Twain-1", "ancestors": 2}, mock_client)
    mock_client.call.assert_called_once_with(
        "getPeople",
        keys="Clemens-1,Twain-1",
        fields=None,
        ancestors=2,
        descendants=None,
        siblings=None,
        nuclear=None,
        limit=None,
        start=None,
    )
    assert len(result) == 1


async def test_search_person(mock_client: AsyncMock) -> None:
    mock_client.call.return_value = [{"status": 0}]
    result = await search_person_handler(
        {"first_name": "Mark", "last_name": "Twain", "limit": 10},
        mock_client,
    )
    mock_client.call.assert_called_once_with(
        "searchPerson",
        FirstName="Mark",
        LastName="Twain",
        BirthDate=None,
        DeathDate=None,
        BirthLocation=None,
        Gender=None,
        limit=10,
        start=None,
        fields=None,
    )
    assert len(result) == 1


async def test_get_profile_api_error(mock_client: AsyncMock) -> None:
    mock_client.call.side_effect = WikiTreeApiError("Not found")
    with pytest.raises(McpToolError, match="Not found"):
        await get_profile_handler({"key": "Bad-1"}, mock_client)
