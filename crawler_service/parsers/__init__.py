from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional


class ActressParser(ABC):
    @abstractmethod
    async def search(self, name: str) -> list[dict]:
        """Search actresses by name, return list of {name, url}"""
        ...

    @abstractmethod
    async def parse_profile(self, url: str) -> Optional[dict]:
        """Parse actress profile page, return dict matching Actress fields"""
        ...
