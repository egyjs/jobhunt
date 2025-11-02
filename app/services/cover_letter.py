"""Generate cover letters tailored to a job posting."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from textwrap import dedent

from app.config import get_settings
from typing import Union

from app.models import JobPosting, UserProfile
from app.schemas import JobDetail


JobLike = Union[JobPosting, JobDetail]


def generate_cover_letter(job: JobLike, profile: UserProfile | None) -> Path:
    """Create a short cover letter text artifact."""

    settings = get_settings()
    cover_dir = settings.output_dir / "cover_letters"
    cover_dir.mkdir(parents=True, exist_ok=True)
    filename = cover_dir / f"cover_letter_{job.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"

    intro = (
        f"Dear {job.company} Hiring Team," if job.company else "To whom it may concern,"
    )
    skills_line = ", ".join(profile.skills) if profile else "relevant experience"
    experience = profile.experience if profile and profile.experience else "my background in software development"

    body = dedent(
        f"""
        {intro}

        I am excited to apply for the {job.title} role. With {experience}, I have delivered results that align with your
        needs, particularly in the focus areas highlighted in the description. I am confident that my skills in
        {skills_line} will help your team ship impactful solutions quickly.

        I welcome the opportunity to discuss how I can contribute to {job.company or 'your organization'}'s goals.

        Best regards,
        {profile.full_name if profile else 'Your Name'}
        """
    ).strip()

    filename.write_text(body, encoding="utf-8")
    return filename


__all__ = ["generate_cover_letter"]

