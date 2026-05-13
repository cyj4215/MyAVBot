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
        query = (
            db.query(MagnetLink)
            .filter(
                MagnetLink.category == cat_enum,
                MagnetLink.title.ilike(f"%{q}%"),
            )
        )
        total = query.count()
        results = query.offset((page - 1) * 20).limit(20).all()
        return {
            "results": [
                {
                    "id": m.id, "title": m.title,
                    "info_hash": m.info_hash, "file_size": m.file_size,
                    "seeders": m.seeders, "leechers": m.leechers,
                    "source_site": m.source_site,
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
        return {
            "id": magnet.id, "title": magnet.title,
            "info_hash": magnet.info_hash, "file_size": magnet.file_size,
            "file_count": magnet.file_count, "source_site": magnet.source_site,
            "work_id": magnet.work_id,
            "category": magnet.category.value if magnet.category else None,
            "seeders": magnet.seeders, "leechers": magnet.leechers,
        }
    finally:
        db.close()
