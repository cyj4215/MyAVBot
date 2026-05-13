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
        return {
            "id": studio.id,
            "name": studio.name,
            "country": studio.country,
            "website": studio.website,
            "logo": studio.logo,
            "description": studio.description,
        }
    finally:
        db.close()
