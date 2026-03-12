import httpx
import pytest
import respx

from wikitree_mcp.client import WikiTreeApiError, WikiTreeClient
from wikitree_mcp.settings import Settings


@pytest.fixture
def client(settings: Settings) -> WikiTreeClient:
    return WikiTreeClient(settings)


async def test_call_success(client: WikiTreeClient, mock_api: respx.MockRouter) -> None:
    mock_api.post("https://api.wikitree.com/api.php").respond(
        json=[{"page_name": "Clemens-1", "status": 0}]
    )
    result = await client.call("getProfile", key="Clemens-1")
    assert result == [{"page_name": "Clemens-1", "status": 0}]


async def test_call_filters_none_params(client: WikiTreeClient, mock_api: respx.MockRouter) -> None:
    route = mock_api.post("https://api.wikitree.com/api.php").respond(json=[{"status": 0}])
    await client.call("getProfile", key="Clemens-1", fields=None, bio_format=None)
    request = route.calls[0].request
    body = request.content.decode()
    assert "fields" not in body
    assert "bio_format" not in body
    assert "key=Clemens-1" in body


async def test_call_injects_app_id(client: WikiTreeClient, mock_api: respx.MockRouter) -> None:
    route = mock_api.post("https://api.wikitree.com/api.php").respond(json=[{"status": 0}])
    await client.call("getProfile", key="Test-1")
    body = route.calls[0].request.content.decode()
    assert "appId=test-app" in body


async def test_call_raises_on_api_error_status(
    client: WikiTreeClient, mock_api: respx.MockRouter
) -> None:
    mock_api.post("https://api.wikitree.com/api.php").respond(
        json=[{"status": "Permission Denied"}]
    )
    with pytest.raises(WikiTreeApiError, match="Permission Denied"):
        await client.call("getProfile", key="Private-1")


async def test_call_raises_on_4xx(client: WikiTreeClient, mock_api: respx.MockRouter) -> None:
    mock_api.post("https://api.wikitree.com/api.php").respond(status_code=400)
    with pytest.raises(WikiTreeApiError):
        await client.call("getProfile", key="Bad-1")


async def test_call_retries_on_5xx(mock_api: respx.MockRouter) -> None:
    settings = Settings(app_id="test-app", max_retries=2)
    client = WikiTreeClient(settings)
    mock_api.post("https://api.wikitree.com/api.php").side_effect = [
        httpx.Response(500),
        httpx.Response(200, json=[{"status": 0}]),
    ]
    result = await client.call("getProfile", key="Retry-1")
    assert result == [{"status": 0}]


async def test_call_fails_after_max_retries(mock_api: respx.MockRouter) -> None:
    settings = Settings(app_id="test-app", max_retries=2)
    client = WikiTreeClient(settings)
    mock_api.post("https://api.wikitree.com/api.php").respond(status_code=500)
    with pytest.raises(WikiTreeApiError, match="2 retries"):
        await client.call("getProfile", key="Fail-1")


async def test_close(client: WikiTreeClient) -> None:
    await client.close()
