from fastapi import FastAPI
from shared.database import init_db
from magnet_service.routers.magnet_router import router as magnet_router
from magnet_service.routers.task_router import router as task_router

app = FastAPI(title="Magnet Service")
app.include_router(magnet_router)
app.include_router(task_router)


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/health")
async def health():
    return {"status": "ok"}
