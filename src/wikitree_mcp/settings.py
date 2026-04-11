# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "WIKITREE_"}

    app_id: str = "Genealogy-MCP_wikitree-mcp"
    api_base_url: str = "https://api.wikitree.com/api.php"
    http_timeout: float = 10.0
    max_retries: int = 3
    email: str | None = None
    password: str | None = None

    @property
    def has_credentials(self) -> bool:
        return self.email is not None and self.password is not None
