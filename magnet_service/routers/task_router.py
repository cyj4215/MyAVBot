from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib, json
from datetime import datetime
from sqlalchemy.orm import Session
from shared.database import SessionLocal
from shared.models import SearchCache, CacheQueryType

router = APIRouter(prefix="/api/v1/magnet", tags=["magnet"])


class BatchSearchRequest(BaseModel):
    keywords: list[str]
    category: str = "adult_eu"


@router.post("/batch-search")
async def batch_search(req: BatchSearchRequest):
    task_id = hashlib.sha256(
        json.dumps(req.keywords, sort_keys=True).encode()
    ).hexdigest()[:16]
    return {"task_id": task_id, "status": "queued"}


@router.get("/task/{task_id}")
async def get_task(task_id: str):
    db: Session = SessionLocal()
    try:
        cache = (
            db.query(SearchCache)
            .filter(
                SearchCache.query_hash == task_id,
                SearchCache.expires_at > datetime.utcnow(),
            )
            .first()
        )
        if not cache:
            raise HTTPException(status_code=404, detail="Task not found or expired")
        return {
            "task_id": task_id, "status": "completed",
            "results": json.loads(cache.result_json),
        }
    finally:
        db.close()
