from fastapi import FastAPI
from shared.database import init_db

app = FastAPI(title="Crawler Service")

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/health")
async def health():
    return {"status": "ok"}
