"""Workflow orchestrating job fetching across all sources."""

from __future__ import annotations

from app.config import get_settings
from app.services.job_sources.base import JobQuery
from app.services.job_sources.static_source import static_fetchers
from app.services.jobs import fetch_and_store


async def run_fetch_workflow() -> tuple[int, int, int]:
    settings = get_settings()
    query = JobQuery(
        keywords=settings.job_titles,
        locations=settings.locations,
        job_types=settings.job_types,
        salary_min=settings.salary_min,
        limit=settings.fetch_limit,
    )
    fetchers = static_fetchers()
    return await fetch_and_store(fetchers, query)


__all__ = ["run_fetch_workflow"]

