from typing import Optional
from crawler_service.executors.base import CrawlerExecutor
from crawler_service.executors.http_executor import HttpExecutor
from crawler_service.executors.cloak_executor import CloakBrowserExecutor
from shared.config import settings

_executor: Optional[CrawlerExecutor] = None

async def create_executor() -> CrawlerExecutor:
    global _executor
    if _executor is None:
        if settings.cloakbrowser_enabled:
            _executor = CloakBrowserExecutor()
        else:
            _executor = HttpExecutor()
    return _executor

async def close_executor():
    global _executor
    if _executor is not None:
        await _executor.close()
        _executor = None

__all__ = ["CrawlerExecutor", "HttpExecutor", "CloakBrowserExecutor",
           "create_executor", "close_executor"]
