from crawler_service.executors.base import CrawlerExecutor
from crawler_service.executors.http_executor import HttpExecutor
from crawler_service.executors.cloak_executor import CloakBrowserExecutor
from shared.config import settings

async def create_executor() -> CrawlerExecutor:
    if settings.cloakbrowser_enabled:
        return CloakBrowserExecutor()
    return HttpExecutor()

__all__ = ["CrawlerExecutor", "HttpExecutor", "CloakBrowserExecutor", "create_executor"]
