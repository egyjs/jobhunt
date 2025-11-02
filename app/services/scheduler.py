from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ..config import get_settings
from ..database import session_scope
from .job_discovery import JobDiscoveryService
from .search_params import DiscoveryParams

logger = logging.getLogger(__name__)


class SchedulerService:
    """Background scheduler that periodically refreshes job listings."""

    def __init__(self, discovery: JobDiscoveryService | None = None) -> None:
        self.settings = get_settings()
        self.discovery = discovery or JobDiscoveryService()
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        interval = self.settings.scheduler_interval_minutes
        self.scheduler.add_job(self.run_discovery, "interval", minutes=interval, id="job_fetch")
        logger.info("Starting scheduler with interval=%s minutes", interval)
        self.scheduler.start()

    async def run_discovery(self) -> None:
        params = DiscoveryParams(
            terms=self.settings.job_search_terms,
            locations=self.settings.job_locations,
            job_types=self.settings.job_types,
            remote_only=self.settings.job_remote_only,
            salary_min=self.settings.job_salary_min,
        )
        with session_scope() as session:
            results = await self.discovery.fetch_and_store(session, params, limit=200)
            logger.info("Scheduler fetched %s jobs", len(results))

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)


__all__ = ["SchedulerService"]
