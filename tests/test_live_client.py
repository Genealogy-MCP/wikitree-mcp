import pytest

from wikitree_mcp.client import WikiTreeApiError, WikiTreeClient

pytestmark = pytest.mark.live


async def test_get_profile_clemens(live_client: WikiTreeClient) -> None:
    result = await live_client.call(
        "getProfile", key="Clemens-1", fields="Id,Name,FirstName,LastNameAtBirth"
    )
    profile = result[0]["profile"]
    assert profile["FirstName"] == "Samuel"
    assert profile["LastNameAtBirth"] == "Clemens"


async def test_get_profile_franklin(live_client: WikiTreeClient) -> None:
    result = await live_client.call(
        "getProfile", key="Franklin-10478", fields="Id,Name,FirstName"
    )
    profile = result[0]["profile"]
    assert profile["FirstName"] == "Aretha"


async def test_search_person_twain(live_client: WikiTreeClient) -> None:
    result = await live_client.call(
        "searchPerson", FirstName="Samuel", LastName="Clemens", limit=5
    )
    assert len(result) >= 1
    assert result[0]["status"] == 0


async def test_get_people_ancestors_clemens(live_client: WikiTreeClient) -> None:
    result = await live_client.call(
        "getPeople", keys="Clemens-1", ancestors=1, fields="Id,Name"
    )
    people = result[0].get("people", {})
    assert len(people) >= 2


async def test_get_bio_clemens(live_client: WikiTreeClient) -> None:
    result = await live_client.call("getBio", key="Clemens-1")
    assert "bio" in result[0]


async def test_invalid_key_returns_error(live_client: WikiTreeClient) -> None:
    with pytest.raises(WikiTreeApiError):
        await live_client.call("getProfile", key="ThisKey-DoesNotExist-99999999")
