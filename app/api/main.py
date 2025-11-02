"""FastAPI application factory."""

from __future__ import annotations

import asyncio

from fastapi import FastAPI

from app.api.routes import router
from app.config import get_settings
from app.database import init_db
from app.services.profile import load_profile_from_json
from app.scheduler import start_scheduler


def create_app() -> FastAPI:
    settings = get_settings()
    init_db()
    load_profile_from_json(settings.profile_json_path)

    application = FastAPI(title="JobApply AI Agent", version="0.1.0")
    application.include_router(router)

    scheduler_stop: asyncio.Event | None = None

    @application.on_event("startup")
    async def _startup() -> None:  # pragma: no cover - FastAPI lifecycle
        nonlocal scheduler_stop
        scheduler_stop = await start_scheduler()

    @application.on_event("shutdown")
    async def _shutdown() -> None:  # pragma: no cover - FastAPI lifecycle
        if scheduler_stop:
            scheduler_stop.set()

    return application


app = create_app()


__all__ = ["create_app", "app"]

