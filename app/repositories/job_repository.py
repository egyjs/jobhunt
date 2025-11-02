"""Repository helpers for job persistence."""

from __future__ import annotations

import datetime as dt
from typing import Iterable, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Job, JobTag


class JobRepository:
    """Encapsulate job persistence operations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert_jobs(self, jobs: Sequence[dict]) -> list[Job]:
        """Insert or update job records from provider payloads."""
        stored: list[Job] = []
        for payload in jobs:
            job = self.session.execute(
                select(Job).where(Job.source == payload["source"], Job.external_id == payload["external_id"])
            ).scalar_one_or_none()
            if job is None:
                job = Job(**payload)
                self.session.add(job)
            else:
                for key, value in payload.items():
                    setattr(job, key, value)
                job.updated_at = dt.datetime.utcnow()
            stored.append(job)
        return stored

    def replace_tags(self, job: Job, tags: Iterable[str]) -> None:
        """Replace tag set for a job."""
        job.tags.clear()
        for tag in sorted(set(tags)):
            job.tags.append(JobTag(name=tag))

    def list_recent(self, limit: int = 50) -> list[Job]:
        stmt = select(Job).order_by(Job.post_date.desc().nullslast(), Job.created_at.desc()).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def all_jobs(self) -> list[Job]:
        return list(self.session.execute(select(Job)).scalars().all())

    def count_by_source(self) -> dict[str, int]:
        stmt = select(Job.source, func.count()).group_by(Job.source)
        return {source: count for source, count in self.session.execute(stmt).all()}

    def get(self, job_id: int) -> Job | None:
        return self.session.get(Job, job_id)


__all__ = ["JobRepository"]
