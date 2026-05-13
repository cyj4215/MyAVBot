from __future__ import annotations
from abc import ABC, abstractmethod


class MagnetSearcher(ABC):
    @abstractmethod
    async def search(
        self, keyword: str, category: str = "adult_eu", page: int = 1
    ) -> list[dict]:
        """
        Return list of:
        { "title": str, "info_hash": str, "file_size": int,
          "seeders": int, "leechers": int, "source_site": str }
        """
        ...
