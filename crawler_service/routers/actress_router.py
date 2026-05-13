from fastapi import APIRouter, Query, HTTPException
from sqlalchemy.orm import Session
from shared.database import SessionLocal
from shared.models import Actress
from crawler_service.parsers.iafd_parser import IAFDParser

router = APIRouter(prefix="/api/v1/actress", tags=["actress"])


@router.get("/search")
async def search_actress(q: str = Query(..., min_length=1), page: int = 1, autofill: bool = True):
    db: Session = SessionLocal()
    try:
        query = db.query(Actress).filter(Actress.name.ilike(f"%{q}%"))
        total = query.count()
        actresses = query.offset((page - 1) * 20).limit(20).all()

        if actresses:
            return {"results": [_actress_summary(a) for a in actresses], "total": total}

        # Live search IAFD
        try:
            parser = IAFDParser()
            raw = await parser.search(q)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Search failed: {e}")

        saved = []
        for i, r in enumerate(raw):
            existing = db.query(Actress).filter(Actress.source_url == r["url"]).first()
            if existing:
                saved.append(existing)
                continue
            actress = Actress(name=r["name"], source_url=r["url"])
            db.add(actress)
            db.flush()

            # Auto-fill first result with full profile
            if i == 0 and autofill:
                try:
                    profile = await parser.parse_profile(r["url"])
                    if profile:
                        for key, val in profile.items():
                            if val is not None:
                                setattr(actress, key, val)
                except Exception:
                    pass
            saved.append(actress)

        db.commit()
        return {"results": [_actress_summary(a) for a in saved], "total": len(saved)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/{actress_id}")
async def get_actress(actress_id: int):
    db: Session = SessionLocal()
    try:
        actress = db.query(Actress).filter(Actress.id == actress_id).first()
        if not actress:
            raise HTTPException(status_code=404, detail="Not found")
        return _actress_detail(actress)
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


def _actress_summary(a: Actress) -> dict:
    return {"id": a.id, "name": a.name, "profile_image": a.profile_image}


def _actress_detail(a: Actress) -> dict:
    return {
        "id": a.id,
        "name": a.name,
        "aliases": a.aliases,
        "birthday": str(a.birthday) if a.birthday else None,
        "birthplace": a.birthplace,
        "height": a.height,
        "measurements": a.measurements,
        "bust": a.bust,
        "country": a.country,
        "career_start": a.career_start,
        "bio_text": a.bio_text,
        "profile_image": a.profile_image,
        "social_links": a.social_links,
        "status": a.status.value if a.status else None,
        "source_url": a.source_url,
    }
