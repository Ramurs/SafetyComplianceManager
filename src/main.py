from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1 import router as v1_router
from src.config import get_settings
from src.database import init_db
from src.services.framework_service import import_all_frameworks
from src.database import async_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await init_db()
    async with async_session() as db:
        await import_all_frameworks(db, settings.frameworks_dir)
    yield


app = FastAPI(
    title="Safety Compliance Manager",
    version="0.1.0",
    description="AI-powered Safety & Compliance Management API",
    lifespan=lifespan,
)

app.include_router(v1_router)


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
