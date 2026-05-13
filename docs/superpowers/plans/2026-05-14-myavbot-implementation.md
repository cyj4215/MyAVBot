# MyAVBot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Telegram bot for欧美 adult actress info, works, and magnet search — 3 microservices + MySQL + Redis via Docker Compose.

**Architecture:** Bot Service (telegram webhook) → REST calls → Crawler Service + Magnet Service. Async tasks via Redis RQ. CloakBrowser for anti-bot crawling.

**Tech Stack:** Python 3.11+, FastAPI, python-telegram-bot, SQLAlchemy 2.0, MySQL 8.0, Redis + RQ, CloakBrowser (Playwright API), Docker Compose

**Phases:**
1. Project scaffold + shared code (models, config, Docker)
2. Crawler Service (crawler + API)
3. Magnet Service (search + API)
4. Bot Service (telegram handlers + formatting)
5. Integration test + deployment polish

---

## File Structure

```
MyAVBot/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── shared/
│   ├── __init__.py
│   ├── config.py              # Config from env vars
│   ├── models/
│   │   ├── __init__.py
│   │   ├── actress.py          # SQLAlchemy model
│   │   ├── work.py
│   │   ├── studio.py
│   │   ├── magnet.py
│   │   ├── search_cache.py
│   │   └── bot_user.py
│   └── database.py             # Engine, session factory
│
├── crawler-service/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── actress_router.py
│   │   ├── work_router.py
│   │   └── studio_router.py
│   ├── executors/
│   │   ├── __init__.py
│   │   ├── base.py             # CrawlerExecutor ABC
│   │   ├── http_executor.py    # httpx impl
│   │   └── cloak_executor.py   # CloakBrowser impl
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── iafd_parser.py
│   │   ├── adultdvdempire_parser.py
│   │   └── data18_parser.py
│   └── worker.py               # RQ worker for async refresh
│
├── magnet-service/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── magnet_router.py
│   │   └── task_router.py
│   ├── search/
│   │   ├── __init__.py
│   │   ├── base.py             # MagnetSearcher ABC
│   │   ├── btso_parser.py      # BTSO indexer parser
│   │   └── executor.py         # CloakBrowser executor for search
│   └── worker.py               # RQ worker for batch search
│
├── bot-service/
│   ├── __init__.py
│   ├── main.py                 # Telegram webhook app
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py
│   │   ├── actress.py
│   │   ├── work.py
│   │   ├── magnet.py
│   │   ├── studio.py
│   │   └── trending.py
│   ├── keyboards.py            # Inline keyboard builders
│   ├── formatters.py           # Message text formatting
│   └── clients.py              # HTTP clients for other services
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_crawler_service/
    ├── test_magnet_service/
    └── test_bot_service/
```

---

### Task 1: Project Scaffold + Shared Code

**Files:**
- Create: `docker-compose.yml`
- Create: `Dockerfile`
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `shared/__init__.py`
- Create: `shared/config.py`
- Create: `shared/database.py`
- Create: `shared/models/__init__.py`
- Create: `shared/models/actress.py`
- Create: `shared/models/work.py`
- Create: `shared/models/studio.py`
- Create: `shared/models/magnet.py`
- Create: `shared/models/search_cache.py`
- Create: `shared/models/bot_user.py`

- [ ] **Step 1: Create docker-compose.yml**

```yaml
version: "3.8"

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: myavbot
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  crawler-service:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8081:8080"
    env_file: .env
    depends_on:
      - mysql
      - redis
    volumes:
      - .:/app

  magnet-service:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8082:8080"
    env_file: .env
    depends_on:
      - mysql
      - redis
    volumes:
      - .:/app

  bot-service:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    env_file: .env
    depends_on:
      - mysql
      - redis
    volumes:
      - .:/app

volumes:
  mysql_data:
```

- [ ] **Step 2: Create Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

- [ ] **Step 3: Create requirements.txt**

```
fastapi==0.110.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.27
pymysql==1.1.0
python-telegram-bot==21.1.1
rq==1.16.1
redis==5.0.1
httpx==0.27.0
beautifulsoup4==4.12.3
parsel==1.9.1
pydantic==2.6.1
pydantic-settings==2.1.0
python-dotenv==1.0.1
```

- [ ] **Step 4: Create .env.example**

```
MYSQL_ROOT_PASSWORD=change_me
MYSQL_USER=myavbot
MYSQL_PASSWORD=change_me
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=myavbot

REDIS_HOST=redis
REDIS_PORT=6379

TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook

CRAWLER_SERVICE_URL=http://crawler-service:8080
MAGNET_SERVICE_URL=http://magnet-service:8080

CLOAKBROWSER_ENABLED=true
CLOAKBROWSER_HEADLESS=true
```

- [ ] **Step 5: Create shared/config.py**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mysql_root_password: str = "change_me"
    mysql_user: str = "myavbot"
    mysql_password: str = "change_me"
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_database: str = "myavbot"

    redis_host: str = "localhost"
    redis_port: int = 6379

    telegram_bot_token: str = ""
    telegram_webhook_url: str = ""

    crawler_service_url: str = "http://localhost:8081"
    magnet_service_url: str = "http://localhost:8082"

    cloakbrowser_enabled: bool = True
    cloakbrowser_headless: bool = True

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"

    class Config:
        env_file = ".env"

settings = Settings()
```

- [ ] **Step 6: Create shared/database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from shared.config import settings

engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def init_db():
    Base.metadata.create_all(bind=engine)
```

- [ ] **Step 7: Create shared/models/actress.py**

```python
from sqlalchemy import Column, Integer, String, Date, SmallInteger, Text, Enum as SAEnum, DateTime, func
from shared.database import Base
import enum

class ActressStatus(str, enum.Enum):
    active = "active"
    retired = "retired"
    unknown = "unknown"

class Actress(Base):
    __tablename__ = "actresses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    aliases = Column(Text, nullable=True)
    birthday = Column(Date, nullable=True)
    birthplace = Column(String(100), nullable=True)
    height = Column(SmallInteger, nullable=True)
    measurements = Column(String(50), nullable=True)
    bust = Column(String(20), nullable=True)
    country = Column(String(50), nullable=True)
    career_start = Column(SmallInteger, nullable=True)
    bio_text = Column(Text, nullable=True)
    profile_image = Column(String(500), nullable=True)
    social_links = Column(Text, nullable=True)
    status = Column(SAEnum(ActressStatus), default=ActressStatus.unknown)
    source_url = Column(String(500), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())
```

- [ ] **Step 8: Create shared/models/work.py**

```python
from sqlalchemy import (Column, Integer, String, Date, SmallInteger, Text,
                        ForeignKey, Decimal, DateTime, func)
from shared.database import Base

class Work(Base):
    __tablename__ = "works"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(300), nullable=False, index=True)
    work_id = Column(String(50), nullable=True, index=True)
    studio_id = Column(Integer, ForeignKey("studios.id"), nullable=True)
    release_date = Column(Date, nullable=True)
    duration = Column(SmallInteger, nullable=True)
    cover_image = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    genres = Column(Text, nullable=True)
    cast_ids = Column(Text, nullable=True)
    rating = Column(Decimal(2, 1), nullable=True)
    source_url = Column(String(500), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())
```

- [ ] **Step 9: Create shared/models/studio.py**

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from shared.database import Base

class Studio(Base):
    __tablename__ = "studios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    country = Column(String(50), nullable=True)
    website = Column(String(500), nullable=True)
    logo = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
```

- [ ] **Step 10: Create shared/models/magnet.py**

```python
from sqlalchemy import (Column, Integer, String, BigInteger, Text,
                        Enum as SAEnum, DateTime, func)
from shared.database import Base
import enum

class MagnetCategory(str, enum.Enum):
    adult_eu = "adult_eu"
    general = "general"

class MagnetLink(Base):
    __tablename__ = "magnet_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    info_hash = Column(String(40), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=True)
    file_count = Column(Integer, nullable=True)
    source_site = Column(String(100), nullable=True)
    work_id = Column(String(50), nullable=True, index=True)
    category = Column(SAEnum(MagnetCategory), default=MagnetCategory.adult_eu)
    seeders = Column(Integer, default=0)
    leechers = Column(Integer, default=0)
    scraped_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
```

- [ ] **Step 11: Create shared/models/search_cache.py**

```python
from sqlalchemy import Column, Integer, String, Text, Enum as SAEnum, DateTime, func
from shared.database import Base
import enum

class CacheQueryType(str, enum.Enum):
    actress = "actress"
    work = "work"
    magnet = "magnet"

class SearchCache(Base):
    __tablename__ = "search_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_hash = Column(String(64), unique=True, nullable=False, index=True)
    query_type = Column(SAEnum(CacheQueryType), nullable=False)
    result_json = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

- [ ] **Step 12: Create shared/models/bot_user.py**

```python
from sqlalchemy import Column, BigInteger, String, Boolean, Integer, DateTime, func
from shared.database import Base

class BotUser(Base):
    __tablename__ = "bot_users"

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    language = Column(String(10), default="zh")
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    last_active = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())
```

- [ ] **Step 13: Create shared/models/__init__.py**

```python
from shared.models.actress import Actress, ActressStatus
from shared.models.work import Work
from shared.models.studio import Studio
from shared.models.magnet import MagnetLink, MagnetCategory
from shared.models.search_cache import SearchCache, CacheQueryType
from shared.models.bot_user import BotUser

__all__ = [
    "Actress", "ActressStatus",
    "Work",
    "Studio",
    "MagnetLink", "MagnetCategory",
    "SearchCache", "CacheQueryType",
    "BotUser",
]
```

- [ ] **Step 14: Verify scaffold works**

Run: `python -c "from shared.database import Base; print('OK')"`
Expected: `OK`

- [ ] **Step 15: Commit scaffold**

```bash
git add docker-compose.yml Dockerfile requirements.txt .env.example shared/
git commit -m "feat: project scaffold with shared models and Docker Compose"
```

---

### Task 2: Crawler Service — Base Executor + Parser Interface

**Files:**
- Create: `crawler-service/__init__.py`
- Create: `crawler-service/main.py`
- Create: `crawler-service/executors/__init__.py`
- Create: `crawler-service/executors/base.py`
- Create: `crawler-service/executors/http_executor.py`
- Create: `crawler-service/executors/cloak_executor.py`

- [ ] **Step 1: Create crawler-service/main.py**

```python
from fastapi import FastAPI
from shared.database import init_db

app = FastAPI(title="Crawler Service")

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 2: Create crawler-service/executors/base.py**

```python
from abc import ABC, abstractmethod

class CrawlerExecutor(ABC):
    @abstractmethod
    async def fetch(self, url: str) -> str:
        """Fetch URL content, return HTML text."""
        ...

    @abstractmethod
    async def close(self):
        """Release resources."""
        ...
```

- [ ] **Step 3: Create crawler-service/executors/http_executor.py**

```python
import httpx
from crawler_service.executors.base import CrawlerExecutor

class HttpExecutor(CrawlerExecutor):
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
            },
        )

    async def fetch(self, url: str) -> str:
        resp = await self.client.get(url)
        resp.raise_for_status()
        return resp.text

    async def close(self):
        await self.client.aclose()
```

- [ ] **Step 4: Create crawler-service/executors/cloak_executor.py**

```python
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

    async def fetch(self, url: str) -> str:
        if self._context is None:
            await self._launch()
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
```

- [ ] **Step 5: Create executor factory helpers**

Add to `crawler-service/executors/__init__.py`:

```python
from crawler_service.executors.base import CrawlerExecutor
from crawler_service.executors.http_executor import HttpExecutor
from crawler_service.executors.cloak_executor import CloakBrowserExecutor
from shared.config import settings

async def create_executor() -> CrawlerExecutor:
    if settings.cloakbrowser_enabled:
        return CloakBrowserExecutor()
    return HttpExecutor()

__all__ = ["CrawlerExecutor", "HttpExecutor", "CloakBrowserExecutor", "create_executor"]
```

- [ ] **Step 6: Commit**

```bash
git add crawler-service/
git commit -m "feat: crawler service base with CloakBrowser executor"
```

---

### Task 3: Crawler Service — Parsers + Actress API Endpoints

**Files:**
- Create: `crawler-service/parsers/__init__.py`
- Create: `crawler-service/parsers/iafd_parser.py`
- Create: `crawler-service/routers/__init__.py`
- Create: `crawler-service/routers/actress_router.py`
- Create: `crawler-service/worker.py`

- [ ] **Step 1: Create base parser interface**

In `crawler-service/parsers/__init__.py`:

```python
from abc import ABC, abstractmethod
from typing import Optional
from shared.models import Actress

class ActressParser(ABC):
    @abstractmethod
    async def search(self, name: str) -> list[dict]:
        """Search actresses by name, return list of {name, url}"""
        ...

    @abstractmethod
    async def parse_profile(self, url: str) -> Optional[dict]:
        """Parse actress profile page, return dict matching Actress fields"""
        ...
```

- [ ] **Step 2: Create IAFD parser**

In `crawler-service/parsers/iafd_parser.py`:

```python
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
```

- [ ] **Step 3: Create actress router**

In `crawler-service/routers/actress_router.py`:

```python
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy.orm import Session
from shared.database import SessionLocal
from shared.models import Actress
from crawler_service.parsers.iafd_parser import IAFDParser

router = APIRouter(prefix="/api/v1/actress", tags=["actress"])

@router.get("/search")
async def search_actress(q: str = Query(..., min_length=1), page: int = 1):
    db: Session = SessionLocal()
    try:
        query = db.query(Actress).filter(Actress.name.ilike(f"%{q}%"))
        total = query.count()
        actresses = query.offset((page - 1) * 20).limit(20).all()

        if actresses:
            return {"results": [{"id": a.id, "name": a.name, "profile_image": a.profile_image} for a in actresses], "total": total}

        parser = IAFDParser()
        results = await parser.search(q)
        return {"results": results, "total": len(results)}
    finally:
        db.close()

@router.get("/{actress_id}")
async def get_actress(actress_id: int):
    db: Session = SessionLocal()
    try:
        actress = db.query(Actress).filter(Actress.id == actress_id).first()
        if not actress:
            raise HTTPException(status_code=404, detail="Not found")
        return actress
    finally:
        db.close()

@router.post("/refresh/{actress_id}")
async def refresh_actress(actress_id: int):
    db: Session = SessionLocal()
    try:
        actress = db.query(Actress).filter(Actress.id == actress_id).first()
        if not actress or not actress.source_url:
            raise HTTPException(status_code=404, detail="No source URL to refresh from")
        parser = IAFDParser()
        data = await parser.parse_profile(actress.source_url)
        if data:
            for key, val in data.items():
                if val is not None:
                    setattr(actress, key, val)
            db.commit()
        return {"status": "refreshed"}
    finally:
        db.close()
```

- [ ] **Step 4: Register router in main.py**

In `crawler-service/main.py`, add:
```python
from crawler_service.routers.actress_router import router as actress_router
app.include_router(actress_router)
```

- [ ] **Step 5: Commit**

```bash
git add crawler-service/routers/ crawler-service/parsers/ crawler-service/main.py
git commit -m "feat: IAFD parser and actress API endpoints"
```

---

### Task 4: Crawler Service — Work + Studio Endpoints

**Files:**
- Create: `crawler-service/routers/work_router.py`
- Create: `crawler-service/routers/studio_router.py`

- [ ] **Step 1: Create work router**

In `crawler-service/routers/work_router.py`:

```python
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy.orm import Session
from shared.database import SessionLocal
from shared.models import Work

router = APIRouter(prefix="/api/v1/work", tags=["work"])

@router.get("/search")
async def search_work(q: str = Query(..., min_length=1), page: int = 1):
    db: Session = SessionLocal()
    try:
        query = db.query(Work).filter(Work.title.ilike(f"%{q}%"))
        total = query.count()
        works = query.offset((page - 1) * 20).limit(20).all()
        return {"results": [{"id": w.id, "title": w.title, "cover_image": w.cover_image, "release_date": str(w.release_date) if w.release_date else None} for w in works], "total": total}
    finally:
        db.close()

@router.get("/{work_id}")
async def get_work(work_id: int):
    db: Session = SessionLocal()
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        if not work:
            raise HTTPException(status_code=404, detail="Not found")
        return work
    finally:
        db.close()

@router.get("/latest")
async def latest_works(studio: int = None, page: int = 1):
    db: Session = SessionLocal()
    try:
        query = db.query(Work)
        if studio:
            query = query.filter(Work.studio_id == studio)
        query = query.order_by(Work.release_date.desc().nullslast())
        works = query.offset((page - 1) * 20).limit(20).all()
        return {"results": [{"id": w.id, "title": w.title, "cover_image": w.cover_image, "release_date": str(w.release_date) if w.release_date else None} for w in works]}
    finally:
        db.close()

@router.get("/by-actress/{actress_id}")
async def works_by_actress(actress_id: int):
    db: Session = SessionLocal()
    try:
        works = db.query(Work).filter(
            Work.cast_ids.like(f"%{actress_id}%")
        ).order_by(Work.release_date.desc().nullslast()).limit(50).all()
        return {"results": [{"id": w.id, "title": w.title, "cover_image": w.cover_image, "release_date": str(w.release_date) if w.release_date else None} for w in works]}
    finally:
        db.close()
```

- [ ] **Step 2: Create studio router**

In `crawler-service/routers/studio_router.py`:

```python
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from shared.database import SessionLocal
from shared.models import Studio

router = APIRouter(prefix="/api/v1/studio", tags=["studio"])

@router.get("/list")
async def list_studios():
    db: Session = SessionLocal()
    try:
        studios = db.query(Studio).limit(100).all()
        return {"results": [{"id": s.id, "name": s.name, "logo": s.logo} for s in studios]}
    finally:
        db.close()

@router.get("/{studio_id}")
async def get_studio(studio_id: int):
    db: Session = SessionLocal()
    try:
        studio = db.query(Studio).filter(Studio.id == studio_id).first()
        if not studio:
            raise HTTPException(status_code=404, detail="Not found")
        return studio
    finally:
        db.close()
```

- [ ] **Step 3: Register routers in main.py**

Add to `crawler-service/main.py`:
```python
from crawler_service.routers.work_router import router as work_router
from crawler_service.routers.studio_router import router as studio_router
app.include_router(work_router)
app.include_router(studio_router)
```

- [ ] **Step 4: Commit**

```bash
git add crawler-service/routers/work_router.py crawler-service/routers/studio_router.py
git commit -m "feat: work and studio API endpoints"
```

---

### Task 5: Magnet Service

**Files:**
- Create: `magnet-service/__init__.py`
- Create: `magnet-service/main.py`
- Create: `magnet-service/routers/__init__.py`
- Create: `magnet-service/routers/magnet_router.py`
- Create: `magnet-service/routers/task_router.py`
- Create: `magnet-service/search/__init__.py`
- Create: `magnet-service/search/base.py`
- Create: `magnet-service/search/executor.py`
- Create: `magnet-service/worker.py`

- [ ] **Step 1: Create magnet-service/main.py**

```python
from fastapi import FastAPI
from shared.database import init_db
from magnet_service.routers.magnet_router import router as magnet_router
from magnet_service.routers.task_router import router as task_router

app = FastAPI(title="Magnet Service")
app.include_router(magnet_router)
app.include_router(task_router)

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 2: Create search base class**

In `magnet-service/search/base.py`:

```python
from abc import ABC, abstractmethod
from typing import Optional

class MagnetSearcher(ABC):
    @abstractmethod
    async def search(self, keyword: str, category: str = "adult_eu", page: int = 1) -> list[dict]:
        """
        Return list of:
        { "title": str, "info_hash": str, "file_size": int,
          "seeders": int, "leechers": int, "source_site": str }
        """
        ...
```

- [ ] **Step 3: Create magnet router**

In `magnet-service/routers/magnet_router.py`:

```python
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy.orm import Session
from shared.database import SessionLocal
from shared.models import MagnetLink, MagnetCategory

router = APIRouter(prefix="/api/v1/magnet", tags=["magnet"])

@router.get("/search")
async def search_magnet(
    q: str = Query(..., min_length=1),
    category: str = "adult_eu",
    page: int = 1,
):
    db: Session = SessionLocal()
    try:
        cat_enum = MagnetCategory.adult_eu if category == "adult_eu" else MagnetCategory.general
        query = db.query(MagnetLink).filter(
            MagnetLink.category == cat_enum,
            MagnetLink.title.ilike(f"%{q}%"),
        )
        total = query.count()
        results = query.offset((page - 1) * 20).limit(20).all()
        return {
            "results": [
                {
                    "id": m.id, "title": m.title, "info_hash": m.info_hash,
                    "file_size": m.file_size, "seeders": m.seeders,
                    "leechers": m.leechers, "source_site": m.source_site,
                }
                for m in results
            ],
            "total": total,
        }
    finally:
        db.close()

@router.get("/{magnet_id}")
async def get_magnet(magnet_id: int):
    db: Session = SessionLocal()
    try:
        magnet = db.query(MagnetLink).filter(MagnetLink.id == magnet_id).first()
        if not magnet:
            raise HTTPException(status_code=404, detail="Not found")
        return magnet
    finally:
        db.close()
```

- [ ] **Step 4: Create task router (async search)**

In `magnet-service/routers/task_router.py`:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib, json, time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from shared.database import SessionLocal
from shared.models import SearchCache, CacheQueryType

router = APIRouter(prefix="/api/v1/magnet", tags=["magnet"])

class BatchSearchRequest(BaseModel):
    keywords: list[str]
    category: str = "adult_eu"

@router.post("/batch-search")
async def batch_search(req: BatchSearchRequest):
    task_id = hashlib.sha256(json.dumps(req.keywords, sort_keys=True).encode()).hexdigest()[:16]
    return {"task_id": task_id, "status": "queued"}

@router.get("/task/{task_id}")
async def get_task(task_id: str):
    db: Session = SessionLocal()
    try:
        cache = db.query(SearchCache).filter(
            SearchCache.query_hash == task_id,
            SearchCache.expires_at > datetime.utcnow(),
        ).first()
        if not cache:
            raise HTTPException(status_code=404, detail="Task not found or expired")
        return {"task_id": task_id, "status": "completed", "results": json.loads(cache.result_json)}
    finally:
        db.close()
```

- [ ] **Step 5: Commit**

```bash
git add magnet-service/
git commit -m "feat: magnet search service API"
```

---

### Task 6: Bot Service — Setup + Core Handlers

**Files:**
- Create: `bot-service/__init__.py`
- Create: `bot-service/main.py`
- Create: `bot-service/handlers/__init__.py`
- Create: `bot-service/handlers/start.py`
- Create: `bot-service/handlers/actress.py`
- Create: `bot-service/handlers/work.py`
- Create: `bot-service/handlers/magnet.py`
- Create: `bot-service/handlers/studio.py`
- Create: `bot-service/keyboards.py`
- Create: `bot-service/formatters.py`
- Create: `bot-service/clients.py`

- [ ] **Step 1: Create bot-service/clients.py**

```python
import httpx
from shared.config import settings

class ServiceClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search_actress(self, name: str):
        resp = await self.client.get(
            f"{settings.crawler_service_url}/api/v1/actress/search",
            params={"q": name},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_actress(self, actress_id: int):
        resp = await self.client.get(
            f"{settings.crawler_service_url}/api/v1/actress/{actress_id}",
        )
        resp.raise_for_status()
        return resp.json()

    async def search_work(self, title: str):
        resp = await self.client.get(
            f"{settings.crawler_service_url}/api/v1/work/search",
            params={"q": title},
        )
        resp.raise_for_status()
        return resp.json()

    async def latest_works(self, studio: int = None):
        params = {}
        if studio:
            params["studio"] = studio
        resp = await self.client.get(
            f"{settings.crawler_service_url}/api/v1/work/latest",
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    async def search_magnet(self, keyword: str, category: str = "adult_eu"):
        resp = await self.client.get(
            f"{settings.magnet_service_url}/api/v1/magnet/search",
            params={"q": keyword, "category": category},
        )
        resp.raise_for_status()
        return resp.json()

    async def search_studio(self, name: str):
        resp = await self.client.get(
            f"{settings.crawler_service_url}/api/v1/studio/list",
        )
        resp.raise_for_status()
        studios = resp.json().get("results", [])
        return [s for s in studios if name.lower() in s["name"].lower()]

    async def close(self):
        await self.client.aclose()

client = ServiceClient()
```

- [ ] **Step 2: Create bot-service/formatters.py**

```python
def format_actress_card(actress: dict) -> str:
    lines = [f"👩 *{actress['name']}*"]
    if actress.get("birthday"):
        lines.append(f"📅 生日: {actress['birthday']}")
    if actress.get("country"):
        lines.append(f"🌍 国籍: {actress['country']}")
    if actress.get("height"):
        lines.append(f"📏 身高: {actress['height']}cm")
    if actress.get("measurements"):
        lines.append(f"📐 三围: {actress['measurements']}")
    if actress.get("career_start"):
        lines.append(f"🎬 出道: {actress['career_start']}")
    if actress.get("status"):
        status_emoji = "🟢" if actress["status"] == "active" else "🔴"
        lines.append(f"{status_emoji} 状态: {'活跃' if actress['status'] == 'active' else '退役'}")
    return "\n".join(lines)

def format_work_card(work: dict) -> str:
    lines = [f"🎥 *{work['title']}*"]
    if work.get("work_id"):
        lines.append(f"🏷 编号: {work['work_id']}")
    if work.get("release_date"):
        lines.append(f"📅 发行: {work['release_date']}")
    if work.get("duration"):
        lines.append(f"⏱ 时长: {work['duration']}min")
    if work.get("rating"):
        stars = "⭐" * int(float(work["rating"]))
        lines.append(f"评分: {stars} ({work['rating']})")
    return "\n".join(lines)

def format_magnet_result(magnet: dict) -> str:
    size_str = format_size(magnet.get("file_size", 0))
    return (
        f"🔗 `{magnet['info_hash']}`\n"
        f"📄 {magnet['title'][:80]}\n"
        f"📦 {size_str} | ⬆ {magnet.get('seeders', 0)} | ⬇ {magnet.get('leechers', 0)}\n"
        f"🏷 {magnet.get('source_site', 'unknown')}"
    )

def format_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}PB"
```

- [ ] **Step 3: Create bot-service/keyboards.py**

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def actress_detail_keyboard(actress_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📖 详细资料", callback_data=f"actress_detail:{actress_id}"),
            InlineKeyboardButton("🎥 作品列表", callback_data=f"actress_works:{actress_id}"),
        ],
        [
            InlineKeyboardButton("🔍 磁力搜索", callback_data=f"magnet_actress:{actress_id}"),
        ],
    ])

def magnet_category_keyboard(keyword: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌍 欧美成人", callback_data=f"magnet_search:{keyword}:adult_eu"),
            InlineKeyboardButton("🌐 通用搜索", callback_data=f"magnet_search:{keyword}:general"),
        ],
    ])

def pagination_keyboard(base_cmd: str, page: int, total: int, data_id: str = None) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    if page > 1:
        row.append(InlineKeyboardButton("◀ 上一页", callback_data=f"{base_cmd}:{page - 1}:{data_id}" if data_id else f"{base_cmd}:{page - 1}"))
    if page < total:
        row.append(InlineKeyboardButton("下一页 ▶", callback_data=f"{base_cmd}:{page + 1}:{data_id}" if data_id else f"{base_cmd}:{page + 1}"))
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)
```

- [ ] **Step 4: Create bot-service/handlers/start.py**

```python
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 *MyAVBot 欢迎你！*\n\n"
        "搜索欧美成人女优资料、最新作品、磁力链接。\n\n"
        "常用命令：\n"
        "/actress `名字` - 搜索女优\n"
        "/work `标题` - 搜索作品\n"
        "/magnet `关键词` - 磁力搜索\n"
        "/latest - 最新作品\n"
        "/help - 完整帮助\n\n"
        "由 CloakBrowser 技术支持 🛡",
        parse_mode="Markdown",
    )

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*MyAVBot 命令列表*\n\n"
        "/actress `<name>` - 搜索女优资料\n"
        "/work `<title>` - 搜索作品\n"
        "/magnet `<keyword>` - 磁力搜索\n"
        "/latest `[studio]` - 最新作品\n"
        "/studio `<name>` - 片商信息\n"
        "/new - 近期新人\n"
        "/trending - 热门内容\n"
        "/help - 本帮助",
        parse_mode="Markdown",
    )

start_handler = CommandHandler("start", start)
help_handler_cmd = CommandHandler("help", help_handler)
```

- [ ] **Step 5: Create actress handler**

In `bot-service/handlers/actress.py`:

```python
from telegram import Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from bot_service.clients import client
from bot_service.formatters import format_actress_card
from bot_service.keyboards import actress_detail_keyboard

async def search_actress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法: /actress 女优名字")
        return
    name = " ".join(context.args)
    await update.message.reply_text(f"🔍 搜索 \"{name}\"...")
    data = await client.search_actress(name)
    results = data.get("results", [])
    if not results:
        await update.message.reply_text("😞 没有找到结果")
        return
    for r in results[:5]:
        text = format_actress_card(r)
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=actress_detail_keyboard(r["id"]),
        )

async def actress_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("actress_detail:"):
        actress_id = int(data.split(":")[1])
        actress = await client.get_actress(actress_id)
        text = format_actress_card(actress)
        if actress.get("bio_text"):
            text += f"\n\n📝 {actress['bio_text'][:300]}"
        if actress.get("profile_image"):
            await query.message.reply_photo(actress["profile_image"], caption=text, parse_mode="Markdown")
            return
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=actress_detail_keyboard(actress_id))
    elif data.startswith("actress_works:"):
        actress_id = int(data.split(":")[1])
        await query.edit_message_text("🎥 获取作品列表...")
        works = await client.latest_works()
        for w in works.get("results", [])[:5]:
            text = f"🎥 {w['title']}\n📅 {w.get('release_date', 'N/A')}"
            await query.message.reply_text(text)

actress_handler = CommandHandler("actress", search_actress)
actress_cb_handler = CallbackQueryHandler(actress_callback, pattern="^actress_")
```

- [ ] **Step 6: Create work handler**

In `bot-service/handlers/work.py`:

```python
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from bot_service.clients import client
from bot_service.formatters import format_work_card

async def search_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法: /work 作品标题或编号")
        return
    title = " ".join(context.args)
    await update.message.reply_text(f"🔍 搜索 \"{title}\"...")
    data = await client.search_work(title)
    results = data.get("results", [])
    if not results:
        await update.message.reply_text("😞 没有找到结果")
        return
    for r in results[:5]:
        text = format_work_card(r)
        if r.get("cover_image"):
            await update.message.reply_photo(r["cover_image"], caption=text, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, parse_mode="Markdown")

async def latest_works(update: Update, context: ContextTypes.DEFAULT_TYPE):
    studio_id = int(context.args[0]) if context.args and context.args[0].isdigit() else None
    data = await client.latest_works(studio_id)
    results = data.get("results", [])
    if not results:
        await update.message.reply_text("暂无最新作品")
        return
    for r in results[:5]:
        text = format_work_card(r)
        if r.get("cover_image"):
            await update.message.reply_photo(r["cover_image"], caption=text, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, parse_mode="Markdown")

work_handler = CommandHandler("work", search_work)
latest_handler = CommandHandler("latest", latest_works)
```

- [ ] **Step 7: Create magnet handler**

In `bot-service/handlers/magnet.py`:

```python
from telegram import Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from bot_service.clients import client
from bot_service.formatters import format_magnet_result
from bot_service.keyboards import magnet_category_keyboard

async def search_magnet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法: /magnet 关键词")
        return
    keyword = " ".join(context.args)
    await update.message.reply_text(
        "选择搜索范围:",
        reply_markup=magnet_category_keyboard(keyword),
    )

async def magnet_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("magnet_search:"):
        parts = data.split(":")
        keyword = parts[1]
        category = parts[2]
        await query.edit_message_text(f"🔍 搜索磁力 \"{keyword}\"...")
        result = await client.search_magnet(keyword, category)
        items = result.get("results", [])
        if not items:
            await query.edit_message_text("😞 没有找到磁力链接")
            return
        lines = [format_magnet_result(m) for m in items[:10]]
        await query.edit_message_text("\n\n".join(lines), parse_mode="Markdown")

magnet_handler = CommandHandler("magnet", search_magnet)
magnet_cb_handler = CallbackQueryHandler(magnet_callback, pattern="^magnet_")
```

- [ ] **Step 8: Create studio handler**

In `bot-service/handlers/studio.py`:

```python
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from bot_service.clients import client

async def search_studio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法: /studio 片商名称")
        return
    name = " ".join(context.args)
    results = await client.search_studio(name)
    if not results:
        await update.message.reply_text("😞 没有找到该片商")
        return
    for s in results[:5]:
        text = f"🏢 *{s['name']}*"
        await update.message.reply_text(text, parse_mode="Markdown")

studio_handler = CommandHandler("studio", search_studio)
```

- [ ] **Step 9: Wire up bot-service/main.py**

```python
from telegram.ext import ApplicationBuilder, Application
from shared.config import settings
from bot_service.handlers.start import start_handler, help_handler_cmd
from bot_service.handlers.actress import actress_handler, actress_cb_handler
from bot_service.handlers.work import work_handler, latest_handler
from bot_service.handlers.magnet import magnet_handler, magnet_cb_handler
from bot_service.handlers.studio import studio_handler

def build_application() -> Application:
    app = ApplicationBuilder().token(settings.telegram_bot_token).build()
    app.add_handler(start_handler)
    app.add_handler(help_handler_cmd)
    app.add_handler(actress_handler)
    app.add_handler(actress_cb_handler)
    app.add_handler(work_handler)
    app.add_handler(latest_handler)
    app.add_handler(magnet_handler)
    app.add_handler(magnet_cb_handler)
    app.add_handler(studio_handler)
    return app

if __name__ == "__main__":
    app = build_application()
    app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path=settings.telegram_bot_token,
        webhook_url=f"{settings.telegram_webhook_url}/{settings.telegram_bot_token}",
    )
```

- [ ] **Step 10: Commit**

```bash
git add bot-service/
git commit -m "feat: bot service with actress/work/magnet/studio handlers"
```

---

### Task 7: Async Worker + Trending Handler

**Files:**
- Create: `crawler-service/worker.py`
- Create: `magnet-service/worker.py`
- Modify: `bot-service/handlers/trending.py`

- [ ] **Step 1: Create crawler worker RQ consumer**

In `crawler-service/worker.py`:
```python
import redis
from rq import Worker, Queue
from shared.config import settings

conn = redis.Redis.from_url(settings.redis_url)
q = Queue(connection=conn)

if __name__ == "__main__":
    worker = Worker([q], connection=conn)
    worker.work()
```

- [ ] **Step 2: Create magnet worker**

In `magnet-service/worker.py` (same pattern):
```python
import redis
from rq import Worker, Queue
from shared.config import settings

conn = redis.Redis.from_url(settings.redis_url)
q = Queue(connection=conn)

if __name__ == "__main__":
    worker = Worker([q], connection=conn)
    worker.work()
```

- [ ] **Step 3: Create trending handler**

In `bot-service/handlers/trending.py`:
```python
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from bot_service.clients import client

async def trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 获取热门内容...")
    data = await client.latest_works()
    results = data.get("results", [])[:5]
    if not results:
        await update.message.reply_text("暂无数据")
        return
    for r in results:
        text = f"🔥 *{r['title']}*\n📅 {r.get('release_date', 'N/A')}"
        await update.message.reply_text(text, parse_mode="Markdown")

trending_handler = CommandHandler("trending", trending)
```

Add import and handler to `bot-service/main.py`.

- [ ] **Step 4: Commit**

```bash
git add crawler-service/worker.py magnet-service/worker.py bot-service/handlers/trending.py bot-service/main.py
git commit -m "feat: RQ workers and trending handler"
```

---

### Task 8: Tests

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_crawler_service/test_executors.py`
- Create: `tests/test_crawler_service/test_actress_router.py`
- Create: `tests/test_magnet_service/test_magnet_router.py`
- Create: `tests/test_bot_service/test_formatters.py`

- [ ] **Step 1: Create conftest.py**

```python
import pytest
from shared.database import Base, engine

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
```

- [ ] **Step 2: Test executors**

In `tests/test_crawler_service/test_executors.py`:
```python
import pytest
from crawler_service.executors.http_executor import HttpExecutor

@pytest.mark.asyncio
async def test_http_executor_fetch_raises_on_bad_url():
    executor = HttpExecutor()
    with pytest.raises(Exception):
        await executor.fetch("http://nonexistent.invalid")
    await executor.close()
```

- [ ] **Step 3: Test formatters**

In `tests/test_bot_service/test_formatters.py`:
```python
from bot_service.formatters import format_actress_card, format_size

def test_format_actress_card_minimal():
    result = format_actress_card({"name": "Test Actress"})
    assert "Test Actress" in result

def test_format_size_bytes():
    assert format_size(500) == "500.0B"

def test_format_size_mb():
    assert "MB" in format_size(2_000_000)
```

- [ ] **Step 4: Commit**

```bash
git add tests/
git commit -m "test: executor and formatter unit tests"
```

---

### Task 9: Docker Compose Polish + Final Verification

**Files:**
- Modify: `Dockerfile` (add service entrypoint)

- [ ] **Step 1: Update Dockerfile for per-service entrypoint**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "crawler-service.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

- [ ] **Step 2: Update docker-compose.yml with service-specific commands**

In docker-compose.yml, add `command` to each service:
- crawler-service: `command: uvicorn crawler_service.main:app --host 0.0.0.0 --port 8080`
- magnet-service: `command: uvicorn magnet_service.main:app --host 0.0.0.0 --port 8080`
- bot-service: `command: python -m bot_service.main`

- [ ] **Step 3: Final commit**

```bash
git add Dockerfile docker-compose.yml
git commit -m "chore: docker entrypoints and final compose config"
```
