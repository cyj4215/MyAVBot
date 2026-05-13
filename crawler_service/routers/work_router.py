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
        return {
            "results": [
                {
                    "id": w.id,
                    "title": w.title,
                    "cover_image": w.cover_image,
                    "release_date": str(w.release_date) if w.release_date else None,
                }
                for w in works
            ],
            "total": total,
        }
    finally:
        db.close()


@router.get("/{work_id}")
async def get_work(work_id: int):
    db: Session = SessionLocal()
    try:
        work = db.query(Work).filter(Work.id == work_id).first()
        if not work:
            raise HTTPException(status_code=404, detail="Not found")
        return {
            "id": work.id,
            "title": work.title,
            "work_id": work.work_id,
            "studio_id": work.studio_id,
            "release_date": str(work.release_date) if work.release_date else None,
            "duration": work.duration,
            "cover_image": work.cover_image,
            "description": work.description,
            "genres": work.genres,
            "rating": float(work.rating) if work.rating else None,
        }
    finally:
        db.close()


@router.get("/latest")
async def latest_works(studio: int = None, page: int = 1):
    db: Session = SessionLocal()
    try:
        query = db.query(Work)
        if studio:
            query = query.filter(Work.studio_id == studio)
        query = query.order_by(Work.release_date.desc(), Work.id.asc())
        works = query.offset((page - 1) * 20).limit(20).all()
        return {
            "results": [
                {
                    "id": w.id,
                    "title": w.title,
                    "cover_image": w.cover_image,
                    "release_date": str(w.release_date) if w.release_date else None,
                }
                for w in works
            ]
        }
    finally:
        db.close()


@router.get("/by-actress/{actress_id}")
async def works_by_actress(actress_id: int):
    db: Session = SessionLocal()
    try:
        works = (
            db.query(Work)
            .filter(Work.cast_ids.like(f"%{actress_id}%"))
            .order_by(Work.release_date.desc(), Work.id.asc())
            .limit(50)
            .all()
        )
        return {
            "results": [
                {
                    "id": w.id,
                    "title": w.title,
                    "cover_image": w.cover_image,
                    "release_date": str(w.release_date) if w.release_date else None,
                }
                for w in works
            ]
        }
    finally:
        db.close()
