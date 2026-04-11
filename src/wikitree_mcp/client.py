# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Federico Castagnini
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
        self._authenticated = False

    @property
    def settings(self) -> Settings:
        return self._settings

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

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

    async def login(self) -> None:
        """Authenticate with WikiTree using the 2-step clientLogin flow."""
        from urllib.parse import parse_qs, urlparse

        step1 = await self._http.post(
            self._settings.api_base_url,
            data={
                "action": "clientLogin",
                "doLogin": "1",
                "wpEmail": self._settings.email,
                "wpPassword": self._settings.password,
            },
            follow_redirects=False,
        )

        if step1.status_code != 302 or "Location" not in step1.headers:
            body: dict[str, Any] = (
                step1.json() if step1.status_code == 200 else {}
            )
            login_info: dict[str, Any] = body.get("clientLogin", {})
            detail: str = login_info.get(
                "message", "no redirect received"
            )
            raise WikiTreeApiError(f"Login failed: {detail}")

        location = step1.headers["Location"]
        qs = parse_qs(urlparse(location).query)
        authcodes = qs.get("authcode", [])
        if not authcodes:
            raise WikiTreeApiError("Login failed: no authcode in redirect")

        step2 = await self._http.post(
            self._settings.api_base_url,
            data={"action": "clientLogin", "authcode": authcodes[0]},
        )
        body = step2.json()
        login_result = body.get("clientLogin", {}).get("result")
        if login_result != "success":
            raise WikiTreeApiError(f"Login failed: {login_result or 'unknown error'}")

        self._authenticated = True

    async def ensure_auth(self) -> None:
        """Ensure the client is authenticated, logging in if needed."""
        if self._authenticated:
            return
        if not self._settings.has_credentials:
            msg = "Authentication required but WIKITREE_EMAIL and WIKITREE_PASSWORD not set."
            raise WikiTreeApiError(msg)
        await self.login()

    def _check_status(self, data: list[dict[str, Any]]) -> None:
        for item in data:
            status = item.get("status")
            if isinstance(status, str) and status not in ("0", ""):
                raise WikiTreeApiError(status)

    async def close(self) -> None:
        await self._http.aclose()
