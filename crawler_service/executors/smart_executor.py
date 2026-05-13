from crawler_service.executors.base import CrawlerExecutor
from crawler_service.executors.http_executor import HttpExecutor
from crawler_service.executors.cloak_executor import CloakBrowserExecutor


class SmartExecutor(CrawlerExecutor):
    """Auto-downgrade executor: tries httpx first, falls back to CloakBrowser on failure."""

    def __init__(self):
        self._http = None
        self._cloak = None

    async def fetch(self, url: str) -> str:
        try:
            if self._http is None:
                self._http = HttpExecutor()
            status, html = await self._http.fetch_with_status(url)
            if status < 400 and len(html) > 100:
                return html
        except Exception:
            pass
        if self._cloak is None:
            self._cloak = CloakBrowserExecutor()
        return await self._cloak.fetch(url)

    async def new_page(self):
        if self._cloak is None:
            self._cloak = CloakBrowserExecutor()
        return await self._cloak.new_page()

    async def close(self):
        if self._http:
            await self._http.close()
        if self._cloak:
            await self._cloak.close()
