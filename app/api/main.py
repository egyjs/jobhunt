from __future__ import annotations

import logging

from fastapi import FastAPI

from ..config import get_settings
from ..database import init_db
from ..services.scheduler import SchedulerService
from .routes.jobs import router as jobs_router

logger = logging.getLogger(__name__)

settings = get_settings()
app = FastAPI(title="JobApply AI MVP", version="0.1.0")
_scheduler = SchedulerService()


@app.on_event("startup")
async def startup_event() -> None:
    init_db()
    try:
        _scheduler.start()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Scheduler failed to start: %s", exc)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    _scheduler.shutdown()


app.include_router(jobs_router)


__all__ = ["app"]
