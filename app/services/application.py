from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from sqlmodel import Session

from ..config import get_settings
from ..repositories import JobRepository
from ..schemas import ApplicationResponse
from .generation import TailoredContentGenerator
from .matcher import JobMatcher

logger = logging.getLogger(__name__)


class ApplicationService:
    """Prepares tailored application packages and tracks status."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.generator = TailoredContentGenerator()
        self.matcher = JobMatcher()

    def apply(self, session: Session, job_id: int, auto_submit: bool = False) -> ApplicationResponse:
        repo = JobRepository(session)
        job = repo.get_job(job_id)
        if not job:
            raise ValueError(f"Job with id {job_id} not found")

        candidate_text = self.matcher.load_candidate_corpus(session)
        match_result = self.matcher.rank_jobs(session, [job])
        match_score = match_result[0].match_score if match_result else None

        application_dir = self.settings.application_output_dir / str(job_id)
        application_dir.mkdir(parents=True, exist_ok=True)

        resume_text = self.generator.resume_highlights(job.summary or job.description, candidate_text)
        cover_letter_text = self.generator.cover_letter(job.title, job.company, job.summary or job.description, candidate_text)

        resume_path = self._write_file(application_dir / "tailored_resume.txt", resume_text)
        cover_letter_path = self._write_file(application_dir / "cover_letter.txt", cover_letter_text)

        status = "applied" if auto_submit else "pending_review"
        submitted_at = datetime.utcnow() if auto_submit else None

        record = repo.save_application(
            job=job,
            status=status,
            match_score=match_score,
            resume_path=str(resume_path),
            cover_letter_path=str(cover_letter_path),
            notes="Auto-generated application package",
            auto_submitted=auto_submit,
            submitted_at=submitted_at,
        )

        logger.info("Prepared application for job %s (status=%s, auto_submit=%s)", job_id, status, auto_submit)

        return ApplicationResponse(
            job_id=job_id,
            status=record.status,
            match_score=record.match_score,
            resume_path=record.resume_path,
            cover_letter_path=record.cover_letter_path,
            notes=record.notes,
            auto_submitted=record.auto_submitted,
            submitted_at=record.submitted_at,
        )

    @staticmethod
    def _write_file(path: Path, content: str) -> Path:
        path.write_text(content, encoding="utf-8")
        return path


__all__ = ["ApplicationService"]
