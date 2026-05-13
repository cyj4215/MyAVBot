import httpx
from shared.config import settings


class ServiceClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)

    async def search_actress(self, name: str, page: int = 1):
        resp = await self.client.get(
            f"{settings.crawler_service_url}/api/v1/actress/search",
            params={"q": name, "page": page},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_actress(self, actress_id: int, sync_works: bool = False):
        params = {"sync_works": "true"} if sync_works else {}
        resp = await self.client.get(
            f"{settings.crawler_service_url}/api/v1/actress/{actress_id}",
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    async def search_work(self, title: str):
        resp = await self.client.get(
            f"{settings.crawler_service_url}/api/v1/work/search",
            params={"q": title},
        )
        resp.raise_for_status()
        return resp.json()

    async def latest_works(self, studio: int = None):
        params = {}
        if studio:
            params["studio"] = studio
        resp = await self.client.get(
            f"{settings.crawler_service_url}/api/v1/work/latest",
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    async def works_by_actress(self, actress_id: int):
        resp = await self.client.get(
            f"{settings.crawler_service_url}/api/v1/work/by-actress/{actress_id}",
        )
        resp.raise_for_status()
        return resp.json()

    async def search_magnet(self, keyword: str, category: str = "adult_eu", page: int = 1):
        resp = await self.client.get(
            f"{settings.magnet_service_url}/api/v1/magnet/search",
            params={"q": keyword, "category": category, "page": page},
        )
        resp.raise_for_status()
        return resp.json()

    async def search_studio(self, name: str):
        resp = await self.client.get(
            f"{settings.crawler_service_url}/api/v1/studio/list",
        )
        resp.raise_for_status()
        studios = resp.json().get("results", [])
        return [s for s in studios if name.lower() in s["name"].lower()]

    async def close(self):
        await self.client.aclose()


client = ServiceClient()
