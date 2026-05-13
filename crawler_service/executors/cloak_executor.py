import asyncio
from crawler_service.executors.base import CrawlerExecutor
from shared.config import settings


class CloakBrowserExecutor(CrawlerExecutor):
    """
    Uses CloakBrowser (stealth Chromium) for anti-bot circumvention.
    https://github.com/CloakHQ/CloakBrowser
    """

    def __init__(self):
        self._playwright = None
        self._browser = None
        self._context = None
        self._launch_lock = asyncio.Lock()
        self._launched = False

    async def fetch(self, url: str) -> str:
        if not self._launched:
            async with self._launch_lock:
                if not self._launched:
                    await self._launch()
                    self._launched = True
        page = await self._context.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            content = await page.content()
            return content
        finally:
            await page.close()

    async def _launch(self):
        from cloakbrowser.async_api import async_playwright  # type: ignore

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=settings.cloakbrowser_headless,
        )
        self._context = await self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )

    async def close(self):
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
