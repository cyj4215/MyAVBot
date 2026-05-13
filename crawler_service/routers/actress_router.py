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
            return {
                "results": [
                    {"id": a.id, "name": a.name, "profile_image": a.profile_image}
                    for a in actresses
                ],
                "total": total,
            }

        try:
            parser = IAFDParser()
            results = await parser.search(q)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Search failed: {e}")
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
        return {
            "id": actress.id,
            "name": actress.name,
            "aliases": actress.aliases,
            "birthday": str(actress.birthday) if actress.birthday else None,
            "birthplace": actress.birthplace,
            "height": actress.height,
            "measurements": actress.measurements,
            "bust": actress.bust,
            "country": actress.country,
            "career_start": actress.career_start,
            "bio_text": actress.bio_text,
            "profile_image": actress.profile_image,
            "social_links": actress.social_links,
            "status": actress.status.value if actress.status else None,
        }
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
