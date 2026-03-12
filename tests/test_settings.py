import pytest
from pydantic import ValidationError

from wikitree_mcp.settings import Settings


def test_settings_with_app_id() -> None:
    s = Settings(app_id="my-app")
    assert s.app_id == "my-app"
    assert s.api_base_url == "https://api.wikitree.com/api.php"
    assert s.http_timeout == 10.0
    assert s.max_retries == 3


def test_settings_custom_values() -> None:
    s = Settings(
        app_id="custom",
        api_base_url="https://example.com/api",
        http_timeout=5.0,
        max_retries=1,
    )
    assert s.api_base_url == "https://example.com/api"
    assert s.http_timeout == 5.0
    assert s.max_retries == 1


def test_settings_missing_app_id_raises() -> None:
    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]
