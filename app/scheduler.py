"""Simple asyncio-based scheduler for recurring job fetches."""

from __future__ import annotations

import asyncio
import logging

from app.config import get_settings
from app.workflows.fetch import run_fetch_workflow


logger = logging.getLogger(__name__)


async def scheduler_loop(stop_event: asyncio.Event) -> None:
    settings = get_settings()
    interval = settings.scheduler_interval_minutes * 60
    while not stop_event.is_set():
        try:
            fetched, created, updated = await run_fetch_workflow()
            logger.info(
                "Scheduled fetch complete",
                extra={
                    "jobs_fetched": fetched,
                    "jobs_created": created,
                    "jobs_updated": updated,
                },
            )
        except Exception as exc:  # pragma: no cover - background logging
            logger.exception("Scheduled fetch failed: %s", exc)

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            continue


async def start_scheduler() -> asyncio.Event:
    stop_event = asyncio.Event()
    asyncio.create_task(scheduler_loop(stop_event))
    return stop_event


__all__ = ["start_scheduler"]

