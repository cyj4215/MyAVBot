from __future__ import annotations
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy.orm import Session
from shared.database import SessionLocal
from shared.models import MagnetLink, MagnetCategory
from magnet_service.search.nyaa_searcher import NyaaSearcher

router = APIRouter(prefix="/api/v1/magnet", tags=["magnet"])

SUKEBEI = NyaaSearcher("https://sukebei.nyaa.si", "sukebei.nyaa.si")
NYAA = NyaaSearcher("https://nyaa.si", "nyaa.si")


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
        cached = query.offset((page - 1) * 20).limit(20).all()
        if cached:
            return format_results(cached, total)

        searchers = [SUKEBEI]
        if category == "general":
            searchers.append(NYAA)

        seen_hashes = set()
        all_results = []
        for searcher in searchers:
            try:
                results = await searcher.search(q, category, page)
                for r in results:
                    h = r["info_hash"]
                    if h and h not in seen_hashes:
                        seen_hashes.add(h)
                        all_results.append(r)
            except Exception:
                continue

        if not all_results:
            return {"results": [], "total": 0}

        saved = []
        for r in all_results:
            existing = db.query(MagnetLink).filter(
                MagnetLink.info_hash == r["info_hash"]
            ).first()
            if existing:
                saved.append(existing)
                continue
            link = MagnetLink(
                info_hash=r["info_hash"], title=r["title"],
                file_size=r["file_size"], seeders=r["seeders"],
                leechers=r["leechers"], source_site=r["source_site"],
                category=cat_enum,
            )
            db.add(link)
            db.flush()
            saved.append(link)
        db.commit()

        return {"results": [magnet_to_dict(m) for m in saved], "total": len(saved)}
    finally:
        db.close()


@router.get("/{magnet_id}")
async def get_magnet(magnet_id: int):
    db: Session = SessionLocal()
    try:
        magnet = db.query(MagnetLink).filter(MagnetLink.id == magnet_id).first()
        if not magnet:
            raise HTTPException(status_code=404, detail="Not found")
        return magnet_to_dict(magnet)
    finally:
        db.close()


def magnet_to_dict(m: MagnetLink) -> dict:
    return {
        "id": m.id, "title": m.title,
        "info_hash": m.info_hash, "file_size": m.file_size,
        "file_count": m.file_count, "source_site": m.source_site,
        "work_id": m.work_id,
        "category": m.category.value if m.category else None,
        "seeders": m.seeders, "leechers": m.leechers,
    }


def format_results(results: list[MagnetLink], total: int) -> dict:
    return {
        "results": [magnet_to_dict(m) for m in results],
        "total": total,
    }
