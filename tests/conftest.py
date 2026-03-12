import pytest
import respx

from wikitree_mcp.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(app_id="test-app")


@pytest.fixture
def mock_api() -> respx.MockRouter:
    with respx.mock(assert_all_called=False) as router:
        yield router
