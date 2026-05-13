from __future__ import annotations
import httpx
from crawler_service.executors.base import CrawlerExecutor


class HttpExecutor(CrawlerExecutor):
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
            },
        )

    async def fetch(self, url: str) -> str:
        resp = await self.client.get(url)
        resp.raise_for_status()
        return resp.text

    async def fetch_with_status(self, url: str) -> tuple[int, str]:
        resp = await self.client.get(url)
        return (resp.status_code, resp.text)

    async def close(self):
        await self.client.aclose()
