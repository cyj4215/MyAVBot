from typing import Optional
from crawler_service.executors.base import CrawlerExecutor
from crawler_service.executors.smart_executor import SmartExecutor
from crawler_service.executors.cloak_executor import CloakBrowserExecutor

_executor: Optional[CrawlerExecutor] = None

async def create_executor() -> CrawlerExecutor:
    global _executor
    if _executor is None:
        _executor = SmartExecutor()
    return _executor

async def close_executor():
    global _executor
    if _executor is not None:
        await _executor.close()
        _executor = None

__all__ = ["CrawlerExecutor", "SmartExecutor", "CloakBrowserExecutor",
           "create_executor", "close_executor"]
