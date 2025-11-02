"""Job aggregation, deduplication, and persistence services."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, List, Sequence, Tuple

from sqlmodel import select

from app.database import session_scope
from app.models import JobPosting
from app.schemas import JobCreate
from app.services.job_sources.base import JobQuery, JobSourceResult


def _job_identity(job: JobSourceResult) -> Tuple[str, str, str]:
    return (job.title.lower(), job.company.lower(), (job.location or "").lower())


def deduplicate_jobs(jobs: Sequence[JobSourceResult]) -> List[JobSourceResult]:
    """Return deduplicated job postings preferring the most recently updated entry."""

    grouped: Dict[Tuple[str, str, str], JobSourceResult] = {}
    for job in jobs:
        key = _job_identity(job)
        existing = grouped.get(key)
        if not existing:
            grouped[key] = job
            continue
        # Prefer jobs with explicit post dates or longer descriptions
        if job.post_date and (not existing.post_date or job.post_date > existing.post_date):
            grouped[key] = job
            continue
        if job.description and (
            not existing.description
            or len(job.description) > len(existing.description)
        ):
            grouped[key] = job
    return list(grouped.values())


def save_jobs(jobs: Iterable[JobSourceResult]) -> Tuple[int, int]:
    """Persist jobs to the database, returning counts of created and updated rows."""

    created = 0
    updated = 0
    timestamp = datetime.utcnow()
    with session_scope() as session:
        for job in jobs:
            statement = select(JobPosting).where(
                JobPosting.source == job.source,
                JobPosting.external_id == job.external_id,
            )
            existing = session.exec(statement).one_or_none()
            if existing:
                existing.title = job.title
                existing.company = job.company
                existing.location = job.location
                existing.description = job.description
                existing.requirements = job.requirements
                existing.salary = job.salary
                existing.post_date = job.post_date
                existing.apply_link = job.apply_link
                existing.tags = job.tags
                existing.updated_at = timestamp
                updated += 1
            else:
                payload = JobCreate(
                    source=job.source,
                    external_id=job.external_id,
                    title=job.title,
                    company=job.company,
                    location=job.location,
                    description=job.description,
                    requirements=job.requirements,
                    salary=job.salary,
                    post_date=job.post_date,
                    apply_link=job.apply_link,
                    tags=job.tags,
                )
                session.add(JobPosting(**payload.model_dump()))
                created += 1
    return created, updated


async def fetch_and_store(fetchers, query: JobQuery) -> Tuple[int, int, int]:
    """Fetch jobs from all sources, deduplicate, and persist.

    Returns a tuple of (fetched, created, updated).
    """

    aggregated: List[JobSourceResult] = []
    for fetcher in fetchers:
        results = await fetcher.fetch(query)
        aggregated.extend(list(results))

    fetched = len(aggregated)
    deduped = deduplicate_jobs(aggregated)
    created, updated = save_jobs(deduped)
    return fetched, created, updated


__all__ = ["deduplicate_jobs", "save_jobs", "fetch_and_store"]

