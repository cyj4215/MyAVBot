from datetime import date
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy.orm import Session
from shared.database import SessionLocal
from shared.models import Actress, Work
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
async def get_actress(actress_id: int, sync_works: bool = False):
    db: Session = SessionLocal()
    try:
        actress = db.query(Actress).filter(Actress.id == actress_id).first()
        if not actress:
            raise HTTPException(status_code=404, detail="Not found")
        result = _actress_detail(actress)
        # Auto-refresh profile if cached data is incomplete
        if actress.source_url and (not actress.birthday or not actress.social_links):
            try:
                parser = IAFDParser()
                profile = await parser.parse_profile(actress.source_url)
                if profile:
                    for key, val in profile.items():
                        if val is not None:
                            setattr(actress, key, val)
                    db.commit()
                    result = _actress_detail(actress)
            except Exception:
                pass
        if sync_works and actress.source_url:
            existing_works = db.query(Work).filter(
                Work.cast_ids.like(f"%{actress_id}%")
            ).count()
            if existing_works == 0:
                parser = IAFDParser()
                raw_works = await parser.parse_works(actress.source_url)
                for w in raw_works:
                    rel_date = date(w["year"], 1, 1) if w.get("year") else None
                    work = Work(
                        title=w["title"],
                        release_date=rel_date,
                        cast_ids=f"[{actress_id}]",
                        description=w.get("notes", ""),
                    )
                    db.add(work)
                db.commit()
        return result
    finally:
        db.close()


@router.post("/{actress_id}/sync-works")
async def sync_actress_works(actress_id: int):
    """Fetch and save performer credits from IAFD."""
    db: Session = SessionLocal()
    try:
        actress = db.query(Actress).filter(Actress.id == actress_id).first()
        if not actress or not actress.source_url:
            raise HTTPException(status_code=404, detail="Not found or no source URL")

        parser = IAFDParser()
        raw_works = await parser.parse_works(actress.source_url)

        count = 0
        for w in raw_works:
            existing = db.query(Work).filter(
                Work.title == w["title"],
                Work.cast_ids.like(f"%{actress_id}%"),
            ).first()
            if existing:
                continue
            rel_date = date(w["year"], 1, 1) if w.get("year") else None
            work = Work(
                title=w["title"],
                release_date=rel_date,
                cast_ids=f"[{actress_id}]",
                description=w.get("notes", ""),
            )
            db.add(work)
            count += 1

        db.commit()
        return {"status": "synced", "total": len(raw_works), "new": count}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Sync failed: {e}")
    finally:
        db.close()


def _actress_summary(a: Actress) -> dict:
    return {
        "id": a.id, "name": a.name, "profile_image": a.profile_image,
        "birthday": str(a.birthday) if a.birthday else None,
        "country": a.country, "height": a.height,
        "measurements": a.measurements, "bust": a.bust,
        "birthplace": a.birthplace,
        "career_start": a.career_start, "aliases": a.aliases,
        "social_links": a.social_links,
        "status": a.status.value if a.status else None,
    }


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
