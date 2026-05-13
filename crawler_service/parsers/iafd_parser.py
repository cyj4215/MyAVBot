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
        return await self._parse_profile_js(executor, url)

    async def parse_works(self, url: str) -> list[dict]:
        executor = await create_executor()
        page = await executor.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            try:
                await page.wait_for_function(
                    "document.body.innerText.includes('Movie Title')", timeout=30000)
            except Exception:
                pass
            text = await page.evaluate("document.body.innerText")
            return self._extract_works(text)
        finally:
            await page.close()

    def _extract_works(self, text: str) -> list[dict]:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        header_idx = None
        for i, line in enumerate(lines):
            if line.startswith("Movie Title\t"):
                header_idx = i
                break
        if header_idx is None:
            return []
        works = []
        for line in lines[header_idx + 1:]:
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            raw_title = parts[0].strip()
            seq_title = raw_title.split(" ", 1)
            title = seq_title[1] if len(seq_title) > 1 and seq_title[0].isdigit() else raw_title
            year_str = parts[1].strip()
            distributor = parts[2].strip() if len(parts) > 2 else ""
            notes = parts[3].strip() if len(parts) > 3 else ""
            year = int(year_str) if year_str.isdigit() else None
            works.append({
                "title": title, "year": year,
                "distributor": distributor, "notes": notes,
            })
        return works

    async def _parse_profile_js(self, executor, url: str) -> Optional[dict]:
        page = await executor.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            try:
                await page.wait_for_function(
                    "document.body.innerText.includes('BIRTHDAY')", timeout=30000)
            except Exception:
                pass
            text = await page.evaluate("document.body.innerText")
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            data = self._extract_fields(lines)
            data["source_url"] = url
            return data
        finally:
            await page.close()

    def _extract_fields(self, lines: list[str]) -> dict:
        import json
        field_map = {}
        label_map = {
            "BIRTHDAY": "birthday", "BIRTHPLACE": "birthplace",
            "HEIGHT": "height", "WEIGHT": "weight",
            "MEASUREMENTS": "measurements", "NATIONALITY": "country",
            "ETHNICITY": "ethnicity", "YEARS ACTIVE AS PERFORMER": "career_start",
            "HAIR COLORS": "hair_colors", "EYE COLOR": "eye_color",
            "WEBSITE": "website",
        }
        for i, line in enumerate(lines):
            key = label_map.get(line)
            if key is not None and i + 1 < len(lines):
                val = lines[i + 1].strip()
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
                elif key == "website":
                    if val.startswith("http"):
                        field_map["website"] = val
                else:
                    field_map[key] = val

        # Build social_links JSON from extracted website
        socials = []
        if field_map.get("website"):
            socials.append({"platform": "website", "url": field_map.pop("website")})
        if socials:
            field_map["social_links"] = json.dumps(socials)
        return field_map
