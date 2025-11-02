from __future__ import annotations

import asyncio
import logging
from typing import Iterable, List, Sequence

from sqlmodel import Session

from ..models import JobPosting
from ..repositories import JobRepository
from ..config import get_settings
from .fetchers.base import FetchedJob, JobFetcher
from .fetchers.company import CompanyFeedFetcher
from .fetchers.glassdoor import GlassdoorFetcher
from .fetchers.indeed import IndeedFetcher
from .fetchers.linkedin import LinkedInFetcher
from .search_params import DiscoveryParams

logger = logging.getLogger(__name__)


class JobDiscoveryService:
    """Coordinates fetchers and persists job postings."""

    def __init__(self, fetchers: Sequence[JobFetcher] | None = None) -> None:
        settings = get_settings()
        self.fetchers = list(fetchers or self._default_fetchers(settings))
        self.settings = settings

    async def fetch_and_store(
        self,
        session: Session,
        params: DiscoveryParams,
        limit: int,
    ) -> List[JobPosting]:
        repo = JobRepository(session)
        tasks = [self._collect(fetcher, params, limit) for fetcher in self.fetchers]
        all_results = await asyncio.gather(*tasks, return_exceptions=True)

        persisted: List[JobPosting] = []
        for fetcher, result in zip(self.fetchers, all_results):
            if isinstance(result, Exception):
                logger.error("Fetcher %s failed: %s", fetcher.slug, result)
                continue
            fetched_jobs: Iterable[FetchedJob] = result
            source = repo.get_or_create_source(fetcher.slug, fetcher.name)
            postings = [self._to_model(job, source.id) for job in fetched_jobs]
            saved = repo.upsert_postings(source, postings)
            persisted.extend(saved)
        return persisted

    async def _collect(self, fetcher: JobFetcher, params: DiscoveryParams, limit: int) -> Iterable[FetchedJob]:
        try:
            return await fetcher.fetch(params, limit)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error fetching jobs from %s", fetcher.slug)
            return []

    def _to_model(self, job: FetchedJob, source_id: int) -> JobPosting:
        tags_json = JobRepository.tags_to_json(job.tags)
        return JobPosting(
            source_id=source_id,
            external_id=job.external_id,
            title=job.title,
            company=job.company,
            location=job.location,
            description=job.description,
            url=job.url,
            salary=job.salary,
            job_type=job.job_type,
            is_remote=job.is_remote,
            tags_json=tags_json,
            posted_at=job.posted_at,
            summary=job.summary,
        )

    def _default_fetchers(self, settings) -> Sequence[JobFetcher]:
        fetchers: List[JobFetcher] = [
            LinkedInFetcher(pages=settings.linkedin_search_pages),
            IndeedFetcher(pages=settings.indeed_search_pages),
            GlassdoorFetcher(pages=settings.glassdoor_search_pages),
        ]
        if settings.company_career_pages:
            fetchers.append(CompanyFeedFetcher(settings.company_career_pages))
        return fetchers


__all__ = ["JobDiscoveryService"]
