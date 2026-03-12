from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "WIKITREE_"}

    app_id: str
    api_base_url: str = "https://api.wikitree.com/api.php"
    http_timeout: float = 10.0
    max_retries: int = 3
