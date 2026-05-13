from crawler_service.executors.base import CrawlerExecutor
from crawler_service.executors.http_executor import HttpExecutor
from crawler_service.executors.cloak_executor import CloakBrowserExecutor
from shared.config import settings

_executor: CrawlerExecutor | None = None

async def create_executor() -> CrawlerExecutor:
    global _executor
    if _executor is None:
        if settings.cloakbrowser_enabled:
            _executor = CloakBrowserExecutor()
        else:
            _executor = HttpExecutor()
    return _executor

__all__ = ["CrawlerExecutor", "HttpExecutor", "CloakBrowserExecutor", "create_executor"]
