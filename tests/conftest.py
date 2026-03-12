from collections.abc import AsyncIterator, Iterator

import pytest
import respx

from wikitree_mcp.client import WikiTreeClient
from wikitree_mcp.settings import Settings

_PROXY_ENV_VARS = (
    "HTTP_PROXY",
    "http_proxy",
    "HTTPS_PROXY",
    "https_proxy",
    "ALL_PROXY",
    "all_proxy",
    "NO_PROXY",
    "no_proxy",
)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help="Run tests that hit the real WikiTree API",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--run-live"):
        return
    skip_live = pytest.mark.skip(reason="pass --run-live to execute")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


@pytest.fixture(autouse=True)
def _clear_proxy_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in _PROXY_ENV_VARS:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def settings() -> Settings:
    return Settings(app_id="test-app")


@pytest.fixture
def mock_api() -> Iterator[respx.MockRouter]:
    with respx.mock(assert_all_called=False) as router:
        yield router


@pytest.fixture
def live_settings() -> Settings:
    return Settings()


@pytest.fixture
async def live_client(live_settings: Settings) -> AsyncIterator[WikiTreeClient]:
    client = WikiTreeClient(live_settings)
    try:
        yield client
    finally:
        await client.close()
