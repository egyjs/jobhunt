"""Job discovery orchestration."""

from __future__ import annotations

import asyncio
import logging
from typing import Iterable

from ..config import Settings
from ..database import session_scope
from ..repositories.job_repository import JobRepository
from ..utils.text import clean_whitespace
from .ai import AITextGenerator
from .embeddings import EmbeddingService
from .job_sources.base import FetchedJob, JobQuery, JobSource
from .tagging import TagService

logger = logging.getLogger(__name__)


class JobFetcher:
    """Coordinate provider fetchers and persistence."""

    def __init__(
        self,
        settings: Settings,
        sources: Iterable[JobSource],
        embeddings: EmbeddingService,
        ai: AITextGenerator,
        tag_service: TagService,
    ) -> None:
        self.settings = settings
        self.sources = list(sources)
        self.embeddings = embeddings
        self.ai = ai
        self.tag_service = tag_service

    async def fetch_all(self) -> dict[str, int]:
        """Fetch from all configured sources and persist results."""
        jobs = await self._gather_jobs()
        if not jobs:
            logger.warning("No jobs fetched from providers")
            return {}

        summaries = await self._summaries_for(jobs)
        embeddings = await self.embeddings.embed([job.description for job in jobs])

        with session_scope() as session:
            repo = JobRepository(session)
            payloads = []
            for job, summary, embedding in zip(jobs, summaries, embeddings, strict=False):
                payloads.append(
                    {
                        "source": job.source,
                        "external_id": job.external_id,
                        "title": clean_whitespace(job.title),
                        "company": clean_whitespace(job.company),
                        "location": clean_whitespace(job.location),
                        "description": job.description,
                        "salary": job.salary,
                        "post_date": job.post_date,
                        "apply_url": job.apply_url,
                        "summary": summary,
                        "embedding": embedding,
                    }
                )
            stored = repo.upsert_jobs(payloads)
            for job_obj, payload in zip(stored, payloads, strict=False):
                tags = self.tag_service.tags_for(" ".join([payload["title"], payload["description"]]))
                repo.replace_tags(job_obj, tags)
            counts = repo.count_by_source()
        return counts

    async def _gather_jobs(self) -> list[FetchedJob]:
        tasks = []
        for title, location in self.settings.job_queries:
            query = JobQuery(title=title, location=location, job_types=tuple(self.settings.job_types))
            for source in self.sources:
                tasks.append(self._fetch_from_source(source, query))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        dedup: dict[tuple[str, str], FetchedJob] = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error("Job provider failed", exc_info=result)
                continue
            for job in result:
                key = (job.source, job.external_id or job.apply_url)
                if key not in dedup:
                    dedup[key] = job
        return list(dedup.values())

    async def _fetch_from_source(self, source: JobSource, query: JobQuery) -> list[FetchedJob]:
        try:
            results_iter = await source.fetch(query, self.settings.fetch_page_size)
            results_list = list(results_iter)
            logger.info("Fetched %s jobs from %s", len(results_list), source.source_name)
            return results_list
        except Exception as exc:  # pragma: no cover - external dependency
            logger.exception("Failed to fetch from %s: %s", source.source_name, exc)
            return []

    async def _summaries_for(self, jobs: list[FetchedJob]) -> list[str]:
        summaries: list[str] = []
        for job in jobs:
            summary = await self.ai.summarize_job(job.description, job.title, job.company)
            summaries.append(summary)
        return summaries


__all__ = ["JobFetcher"]
