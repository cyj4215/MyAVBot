from __future__ import annotations
from parsel import Selector
from typing import Optional
from crawler_service.parsers import ActressParser
from crawler_service.executors import create_executor


class IAFDParser(ActressParser):
    BASE_URL = "https://www.iafd.com"

    async def search(self, name: str) -> list[dict]:
        executor = await create_executor()
        try:
            url = f"{self.BASE_URL}/person.rme/perfform=/{name}/gender=f"
            html = await executor.fetch(url)
            sel = Selector(text=html)
            results = []
            for row in sel.css("table#sortabletable tr")[1:]:
                link = row.css("a[href*='person.rme']")
                if link:
                    results.append({
                        "name": link.css("::text").get("").strip(),
                        "url": self.BASE_URL + link.attrib["href"],
                    })
            return results
        finally:
            await executor.close()

    async def parse_profile(self, url: str) -> Optional[dict]:
        executor = await create_executor()
        try:
            html = await executor.fetch(url)
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
        finally:
            await executor.close()
