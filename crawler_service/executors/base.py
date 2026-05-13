from abc import ABC, abstractmethod


class CrawlerExecutor(ABC):
    @abstractmethod
    async def fetch(self, url: str) -> str:
        """Fetch URL content, return HTML text."""
        ...

    @abstractmethod
    async def close(self):
        """Release resources."""
        ...
