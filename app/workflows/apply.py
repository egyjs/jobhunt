"""Workflow for preparing or submitting job applications."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import select

from app.database import session_scope
from app.models import ApplicationStatus, JobApplication, JobPosting, UserProfile
from app.schemas import ApplicationDetail, ApplyResponse, JobDetail
from app.services.cover_letter import generate_cover_letter
from app.services.profile import load_profile_from_json
from app.services.resume_tailor import tailor_resume


def _get_profile() -> UserProfile | None:
    from app.config import get_settings

    settings = get_settings()
    load_profile_from_json(settings.profile_json_path)
    with session_scope() as session:
        return session.exec(select(UserProfile)).first()


def run_apply_workflow(job_id: int, auto_submit: bool = False) -> ApplyResponse:
    profile = _get_profile()

    with session_scope() as session:
        statement = select(JobPosting).where(JobPosting.id == job_id)
        job = session.exec(statement).one_or_none()
        if not job:
            raise ValueError(f"Job with id {job_id} not found")

        job_snapshot = JobDetail(
            id=job.id,
            source=job.source,
            external_id=job.external_id,
            title=job.title,
            company=job.company,
            location=job.location,
            salary=job.salary,
            post_date=job.post_date,
            apply_link=job.apply_link,
            tags=job.tags,
            description=job.description,
            requirements=job.requirements,
            summary=(job.description or job.requirements or "").split(". ")[0],
        )

    resume_path = tailor_resume(job_snapshot, profile)
    cover_letter_path = generate_cover_letter(job_snapshot, profile)

    with session_scope() as session:
        job_record = session.exec(select(JobPosting).where(JobPosting.id == job_id)).one()
        statement = select(JobApplication).where(JobApplication.job_id == job_record.id)
        application = session.exec(statement).one_or_none()
        if not application:
            application = JobApplication(job_id=job_record.id)
            session.add(application)
        application.resume_path = str(resume_path)
        application.cover_letter_path = str(cover_letter_path)
        application.updated_at = datetime.utcnow()
        if auto_submit:
            application.status = ApplicationStatus.APPLIED
            application.applied_at = datetime.utcnow()
            application.notes = "Auto-submitted via MVP workflow"
        else:
            application.status = ApplicationStatus.PENDING
            application.notes = "Manual review required for submission"
        session.flush()
        response = ApplyResponse(
            application=ApplicationDetail(
                id=application.id,
                status=application.status,
                score=application.score,
                resume_path=application.resume_path,
                cover_letter_path=application.cover_letter_path,
                notes=application.notes,
                applied_at=application.applied_at,
                updated_at=application.updated_at,
                job=job_snapshot,
            )
        )
    return response


__all__ = ["run_apply_workflow"]

