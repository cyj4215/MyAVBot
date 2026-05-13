from fastapi import FastAPI
from shared.database import init_db
from crawler_service.routers.actress_router import router as actress_router
from crawler_service.routers.work_router import router as work_router
from crawler_service.routers.studio_router import router as studio_router
from crawler_service.executors import close_executor

app = FastAPI(title="Crawler Service")
app.include_router(actress_router)
app.include_router(work_router)
app.include_router(studio_router)

@app.on_event("startup")
async def startup():
    init_db()

@app.on_event("shutdown")
async def shutdown():
    await close_executor()

@app.get("/health")
async def health():
    return {"status": "ok"}
