import asyncio
from crawler_service.executors.base import CrawlerExecutor
from shared.config import settings


class CloakBrowserExecutor(CrawlerExecutor):
    """
    Uses CloakBrowser (stealth Chromium) for anti-bot circumvention.
    https://github.com/CloakHQ/CloakBrowser
    """

    def __init__(self):
        self._browser = None
        self._context = None
        self._launch_lock = asyncio.Lock()
        self._launched = False

    async def fetch(self, url: str) -> str:
        page = await self._get_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            content = await page.content()
            return content
        finally:
            await page.close()

    async def new_page(self):
        """Create a new browser page. Ensures browser is launched first."""
        if not self._launched:
            async with self._launch_lock:
                if not self._launched:
                    await self._launch()
                    self._launched = True
        return await self._context.new_page()

    async def _get_page(self):
        if not self._launched:
            async with self._launch_lock:
                if not self._launched:
                    await self._launch()
                    self._launched = True
        return await self._context.new_page()

    async def _launch(self):
        import cloakbrowser

        self._browser = await cloakbrowser.launch_async(
            headless=settings.cloakbrowser_headless,
            locale="en-US",
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
