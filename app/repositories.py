from __future__ import annotations

import json
from datetime import datetime
from typing import Iterable, List, Optional, Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .models import ApplicationRecord, JobPosting, JobSource


class JobRepository:
    """Persistence helper for job sources, postings, and applications."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # --- Sources -----------------------------------------------------------------
    def get_or_create_source(self, slug: str, name: str, homepage_url: Optional[str] = None) -> JobSource:
        source = self.session.exec(select(JobSource).where(JobSource.slug == slug)).one_or_none()
        if source:
            return source

        source = JobSource(slug=slug, name=name, homepage_url=homepage_url)
        self.session.add(source)
        self.session.commit()
        self.session.refresh(source)
        return source

    # --- Postings ----------------------------------------------------------------
    def upsert_postings(self, source: JobSource, postings: Sequence[JobPosting]) -> List[JobPosting]:
        saved: List[JobPosting] = []
        for posting in postings:
            posting.source_id = source.id  # ensure FK
            posting.source = source
            existing = self.session.exec(
                select(JobPosting).where(JobPosting.source_id == source.id, JobPosting.external_id == posting.external_id)
            ).one_or_none()
            if existing:
                existing.title = posting.title
                existing.company = posting.company
                existing.location = posting.location
                existing.description = posting.description
                existing.url = posting.url
                existing.salary = posting.salary
                existing.job_type = posting.job_type
                existing.is_remote = posting.is_remote
                existing.tags_json = posting.tags_json
                existing.posted_at = posting.posted_at
                existing.summary = posting.summary
                existing.scraped_at = datetime.utcnow()
                existing.source = source
                saved.append(existing)
                continue

            self.session.add(posting)
            try:
                self.session.commit()
            except IntegrityError:
                self.session.rollback()
                continue
            self.session.refresh(posting)
            saved.append(posting)
        self.session.commit()
        return saved

    def list_recent_jobs(self, limit: int = 100) -> List[JobPosting]:
        statement = (
            select(JobPosting)
            .options(selectinload(JobPosting.source))
            .order_by(JobPosting.scraped_at.desc())
            .limit(limit)
        )
        return list(self.session.exec(statement))

    def iter_jobs(self) -> Iterable[JobPosting]:
        statement = select(JobPosting).options(selectinload(JobPosting.source))
        yield from self.session.exec(statement)

    def get_job(self, job_id: int) -> Optional[JobPosting]:
        statement = select(JobPosting).options(selectinload(JobPosting.source)).where(JobPosting.id == job_id)
        return self.session.exec(statement).one_or_none()

    # --- Applications ------------------------------------------------------------
    def save_application(
        self,
        job: JobPosting,
        status: str,
        match_score: Optional[float],
        resume_path: Optional[str],
        cover_letter_path: Optional[str],
        notes: Optional[str],
        auto_submitted: bool,
        submitted_at: Optional[datetime] = None,
    ) -> ApplicationRecord:
        record = ApplicationRecord(
            job_posting_id=job.id,
            status=status,
            match_score=match_score,
            resume_path=resume_path,
            cover_letter_path=cover_letter_path,
            notes=notes,
            auto_submitted=auto_submitted,
            submitted_at=submitted_at,
            updated_at=datetime.utcnow(),
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    # --- Tags --------------------------------------------------------------------
    @staticmethod
    def tags_to_json(tags: Sequence[str]) -> Optional[str]:
        if not tags:
            return None
        return json.dumps(sorted(set(tag.strip().lower() for tag in tags if tag)))


__all__ = ["JobRepository"]
