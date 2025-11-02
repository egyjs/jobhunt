"""Generate job-specific resume variants."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from textwrap import dedent

from app.config import get_settings
from typing import Union

from app.models import JobPosting, UserProfile
from app.schemas import JobDetail


JobLike = Union[JobPosting, JobDetail]


def tailor_resume(job: JobLike, profile: UserProfile | None) -> Path:
    """Create a simple tailored resume text file for the job."""

    settings = get_settings()
    resume_dir = settings.output_dir / "resumes"
    resume_dir.mkdir(parents=True, exist_ok=True)
    filename = resume_dir / f"resume_{job.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"

    summary = job.description or job.requirements or ""
    skills_line = ", ".join(profile.skills) if profile else ""
    content = dedent(
        f"""
        Tailored Resume for {job.title} at {job.company}
        =============================================

        Candidate: {profile.full_name if profile else 'Unknown Candidate'}
        Headline: {profile.headline if profile else 'N/A'}

        Highlighted Skills: {skills_line}

        Role Alignment Summary:
        {summary}

        Recent Experience:
        {profile.experience if profile and profile.experience else 'Experience details not provided.'}
        """
    ).strip()

    filename.write_text(content, encoding="utf-8")
    return filename


__all__ = ["tailor_resume"]

