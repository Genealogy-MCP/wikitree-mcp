from __future__ import annotations

import asyncio
import random
from typing import Any

import httpx

from wikitree_mcp.settings import Settings


class WikiTreeApiError(Exception):
    pass


class WikiTreeClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._http = httpx.AsyncClient(timeout=settings.http_timeout)

    async def call(self, action: str, **params: Any) -> list[dict[str, Any]]:
        filtered = {k: v for k, v in params.items() if v is not None}
        payload = {"action": action, "appId": self._settings.app_id, **filtered}

        last_exc: Exception | None = None
        for attempt in range(self._settings.max_retries):
            try:
                resp = await self._http.post(
                    self._settings.api_base_url,
                    data=payload,
                )
                resp.raise_for_status()
                data: list[dict[str, Any]] = resp.json()
                self._check_status(data)
                return data
            except (httpx.HTTPStatusError, httpx.TransportError) as exc:
                last_exc = exc
                if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code < 500:
                    raise WikiTreeApiError(str(exc)) from exc
                if attempt < self._settings.max_retries - 1:
                    delay = min(2**attempt, 8) + random.uniform(0, 1)
                    await asyncio.sleep(delay)

        msg = f"Request failed after {self._settings.max_retries} retries"
        raise WikiTreeApiError(msg) from last_exc

    def _check_status(self, data: list[dict[str, Any]]) -> None:
        for item in data:
            status = item.get("status")
            if isinstance(status, str) and status not in ("0", ""):
                raise WikiTreeApiError(status)

    async def close(self) -> None:
        await self._http.aclose()
