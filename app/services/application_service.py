"""Application workflow orchestration."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from ..config import Settings
from ..database import session_scope
from ..models import Application
from ..repositories.application_repository import ApplicationRepository
from ..repositories.job_repository import JobRepository
from .ai import AITextGenerator
from .profile import ProfileLoader


class ApplicationService:
    """Prepare tailored application artifacts for a job."""

    def __init__(self, settings: Settings, ai: AITextGenerator, profile_loader: ProfileLoader) -> None:
        self.settings = settings
        self.ai = ai
        self.profile_loader = profile_loader

    async def prepare(self, job_id: int, auto_submit: bool = False, notes: str | None = None) -> Application:
        profile = self.profile_loader.load()
        with session_scope() as session:
            job_repo = JobRepository(session)
            job = job_repo.get(job_id)
            if not job:
                raise ValueError(f"Job {job_id} not found")
            app_repo = ApplicationRepository(session)
            resume_text = await self.ai.resume_bullets(profile.resume_text, job.description)
            cover_letter_text = await self.ai.cover_letter(profile.summary, job.description, job.company)
            timestamp = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(self.settings.application_output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            resume_path = output_dir / f"resume_{job.id}_{timestamp}.txt"
            cover_letter_path = output_dir / f"cover_letter_{job.id}_{timestamp}.txt"
            resume_path.write_text(resume_text)
            cover_letter_path.write_text(cover_letter_text)
            application = app_repo.create(
                {
                    "job_id": job.id,
                    "status": "applied" if auto_submit else "pending",
                    "auto_submitted": auto_submit,
                    "resume_path": str(resume_path),
                    "cover_letter_path": str(cover_letter_path),
                    "notes": notes,
                }
            )
            session.flush()
            return application


__all__ = ["ApplicationService"]
