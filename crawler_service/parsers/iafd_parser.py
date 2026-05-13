from __future__ import annotations
from urllib.parse import quote
from typing import Optional
from crawler_service.parsers import ActressParser
from crawler_service.executors import create_executor


class IAFDParser(ActressParser):
    BASE_URL = "https://www.iafd.com"

    async def search(self, name: str) -> list[dict]:
        executor = await create_executor()
        url = f"{self.BASE_URL}/ramesearch.asp?searchtype=comprehensive&searchstring={quote(name)}"
        html = await executor.fetch(url)
        from parsel import Selector
        sel = Selector(text=html)
        results = []
        for link in sel.css("a[href*='person.rme']"):
            href = link.attrib.get("href", "")
            display_name = link.css("::text").get("").strip()
            if not display_name or "person.rme" not in href:
                continue
            results.append({
                "name": display_name,
                "url": f"{self.BASE_URL}/{href.lstrip('/')}",
            })
        return results

    async def parse_profile(self, url: str) -> Optional[dict]:
        executor = await create_executor()
        if not hasattr(executor, '_browser') or executor._browser is None:
            # Fallback: try HTML parsing for HttpExecutor
            return await self._parse_profile_html(executor, url)
        return await self._parse_profile_js(executor, url)

    async def _parse_profile_js(self, executor, url: str) -> Optional[dict]:
        """Parse profile using browser evaluate for JS-rendered pages."""
        page = await executor._context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            import asyncio
            await asyncio.sleep(4)
            text = await page.evaluate("document.body.innerText")
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            data = self._extract_fields(lines)
            data["source_url"] = url
            return data
        finally:
            await page.close()

    async def _parse_profile_html(self, executor, url: str) -> Optional[dict]:
        """Fallback HTML-based profile parsing for non-JS executors."""
        html = await executor.fetch(url)
        from parsel import Selector
        sel = Selector(text=html)

        def get_label(label: str) -> Optional[str]:
            row = sel.xpath(f'//td[contains(text(), "{label}")]/following-sibling::td[1]')
            return row.css("::text").get("").strip() if row else None

        return {
            "name": get_label("Name"),
            "birthday": get_label("Birthday"),
            "birthplace": get_label("Birthplace"),
            "height": get_label("Height"),
            "measurements": get_label("Measurements"),
            "country": get_label("Country"),
            "career_start": get_label("Career Started"),
            "bio_text": get_label("Bio"),
            "source_url": url,
        }

    def _extract_fields(self, lines: list[str]) -> dict:
        """Extract bio fields from text lines (key: value pattern)."""
        field_map = {}
        label_map = {
            "BIRTHDAY": "birthday",
            "BIRTHPLACE": "birthplace",
            "HEIGHT": "height",
            "WEIGHT": "weight",
            "MEASUREMENTS": "measurements",
            "NATIONALITY": "country",
            "ETHNICITY": "ethnicity",
            "YEARS ACTIVE AS PERFORMER": "career_start",
            "HAIR COLORS": "hair_colors",
            "EYE COLOR": "eye_color",
        }

        for i, line in enumerate(lines):
            key = label_map.get(line)
            if key is not None and i + 1 < len(lines):
                val = lines[i + 1].strip()
                # Clean up birthday to date
                if key == "birthday":
                    import re
                    m = re.match(r"([A-Za-z]+ \d+, \d+)", val)
                    if m:
                        from datetime import datetime
                        try:
                            dt = datetime.strptime(m.group(1), "%B %d, %Y")
                            field_map[key] = dt.strftime("%Y-%m-%d")
                            continue
                        except ValueError:
                            pass
                    field_map[key] = val
                elif key == "height":
                    import re
                    m = re.search(r"(\d+) cm", val)
                    field_map[key] = int(m.group(1)) if m else val
                elif key == "career_start":
                    import re
                    m = re.match(r"(\d{4})", val)
                    field_map[key] = int(m.group(1)) if m else val
                else:
                    field_map[key] = val
        return field_map
