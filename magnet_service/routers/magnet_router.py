from fastapi import APIRouter, Query, HTTPException
from sqlalchemy.orm import Session
from shared.database import SessionLocal
from shared.models import MagnetLink, MagnetCategory
from magnet_service.search.sukebei_searcher import SukebeiSearcher

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
        query = (
            db.query(MagnetLink)
            .filter(
                MagnetLink.category == cat_enum,
                MagnetLink.title.ilike(f"%{q}%"),
            )
        )
        total = query.count()
        cached = query.offset((page - 1) * 20).limit(20).all()

        if cached:
            return format_results(cached, total)

        # Live search fallback
        try:
            searcher = SukebeiSearcher()
            live_results = await searcher.search(q, category, page)
        except Exception as e:
            return {"results": [], "total": 0, "error": f"Search failed: {e}"}

        # Cache results in DB
        saved = []
        for r in live_results:
            existing = db.query(MagnetLink).filter(
                MagnetLink.info_hash == r["info_hash"]
            ).first()
            if existing:
                saved.append(existing)
                continue
            link = MagnetLink(
                info_hash=r["info_hash"],
                title=r["title"],
                file_size=r["file_size"],
                seeders=r["seeders"],
                leechers=r["leechers"],
                source_site=r["source_site"],
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
