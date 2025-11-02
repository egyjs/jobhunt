"""Background scheduler configuration."""

from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .config import Settings
from .services.job_fetcher import JobFetcher

logger = logging.getLogger(__name__)


def build_scheduler(job_fetcher: JobFetcher, settings: Settings) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=settings.timezone)

    async def run_fetch() -> None:
        logger.info("Scheduled job discovery started")
        counts = await job_fetcher.fetch_all()
        logger.info("Scheduled job discovery completed: %s", counts)

    scheduler.add_job(run_fetch, "interval", minutes=settings.scheduler_interval_minutes, id="job_fetcher", replace_existing=True)
    return scheduler


__all__ = ["build_scheduler"]
