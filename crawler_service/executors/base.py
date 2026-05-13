from __future__ import annotations
from abc import ABC, abstractmethod


class CrawlerExecutor(ABC):
    @abstractmethod
    async def fetch(self, url: str) -> str:
        """Fetch URL content, return HTML text."""
        ...

    async def fetch_with_status(self, url: str) -> tuple[int, str]:
        """Fetch URL content, return (status_code, html). Default: calls fetch()."""
        html = await self.fetch(url)
        return (200, html)

    async def new_page(self):
        """Create a new page for JS evaluation. Only supported by browser-based executors."""
        raise NotImplementedError("new_page requires a browser-based executor")

    @abstractmethod
    async def close(self):
        """Release resources."""
        ...
