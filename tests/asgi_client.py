"""Small synchronous facade over HTTPX's in-process ASGI transport.

Starlette's thread-portal ``TestClient`` can deadlock in restricted execution
environments. This facade keeps tests synchronous while exercising the real
ASGI application without opening sockets or starting a server process.
"""

import asyncio

import httpx


class ASGITestClient:
    """Issue isolated synchronous requests against an ASGI application."""

    def __init__(self, app) -> None:
        self.app = app

    async def _request(self, method: str, path: str, **kwargs):
        transport = httpx.ASGITransport(app=self.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.request(method, path, **kwargs)

    def request(self, method: str, path: str, **kwargs):
        return asyncio.run(self._request(method, path, **kwargs))

    def get(self, path: str, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self.request("POST", path, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False
