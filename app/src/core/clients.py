from typing import Protocol, Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class ClientProtocol(Protocol):
    async def send(
        self,
        url: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        ...


class HttpClient:
    def __init__(
        self,
        timeout: float = 10.0,
    ) -> None:
        self._client = httpx.AsyncClient(
            timeout=timeout,
        )

    async def close(self) -> None:
        await self._client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(
            (
                httpx.ConnectError,
                httpx.ReadTimeout,
                httpx.WriteTimeout,
                httpx.RemoteProtocolError,
                httpx.HTTPStatusError,
            )
        ),
        reraise=True,
    )
    async def send(
        self,
        url: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        response = await self._client.post(
            url,
            json=payload,
        )

        if response.status_code >= 500:
            response.raise_for_status()

        response.raise_for_status()

        return response.json()

    async def __aenter__(self) -> "HttpClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
