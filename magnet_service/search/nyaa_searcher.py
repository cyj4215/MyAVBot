from __future__ import annotations
from urllib.parse import quote, urlparse, parse_qs
from parsel import Selector
from magnet_service.search.base import MagnetSearcher


class NyaaSearcher(MagnetSearcher):
    """Scrapes Nyaa.si / Sukebei for magnet links. Same codebase, different base URL."""

    def __init__(self, base_url: str, source_name: str):
        self.base_url = base_url.rstrip("/")
        self.source_name = source_name

    async def search(
        self, keyword: str, category: str = "adult_eu", page: int = 1
    ) -> list[dict]:
        url = f"{self.base_url}/?q={quote(keyword)}&c=0_0&page={page}"
        html = await self._fetch(url)
        sel = Selector(text=html)
        results = []
        for row in sel.css("table.table tbody tr"):
            link = row.css("a[href*='magnet:']")
            if not link:
                continue
            magnet_href = link.attrib.get("href", "")
            info_hash = self._parse_hash(magnet_href)
            title_tag = row.css("td[colspan='2'] a")
            title = title_tag.attrib.get("title", title_tag.css("::text").get("")).strip()
            size_str = row.css("td.text-center").re_first(r"[\d.]+ [KMGTP]iB")
            seeders_str = row.css("td.text-center::text").getall()
            try:
                seeders = int(seeders_str[-3].strip()) if len(seeders_str) >= 3 else 0
                leechers = int(seeders_str[-2].strip()) if len(seeders_str) >= 2 else 0
            except (ValueError, IndexError):
                seeders = 0
                leechers = 0

            results.append({
                "title": title,
                "info_hash": info_hash,
                "file_size": self._parse_size(size_str),
                "seeders": seeders,
                "leechers": leechers,
                "source_site": self.source_name,
            })
        return results

    async def _fetch(self, url: str) -> str:
        import httpx
        async with httpx.AsyncClient(
            timeout=30.0, follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"},
        ) as c:
            resp = await c.get(url)
            resp.raise_for_status()
            return resp.text

    def _parse_hash(self, magnet_href: str) -> str:
        parsed = urlparse(magnet_href)
        xt = parse_qs(parsed.query).get("xt", [""])[0]
        return xt[9:] if xt.startswith("urn:btih:") else ""

    def _parse_size(self, size_str: str | None) -> int:
        if not size_str:
            return 0
        units = {"B": 1, "KiB": 1024, "MiB": 1024**2, "GiB": 1024**3, "TiB": 1024**4}
        parts = size_str.split()
        if len(parts) != 2:
            return 0
        try:
            return int(float(parts[0]) * units.get(parts[1], 1))
        except (ValueError, KeyError):
            return 0
