"""Generate human-readable summaries for job listings."""

from __future__ import annotations

from textwrap import shorten

from app.models import JobPosting


def summarize_job(job: JobPosting, length: int = 200) -> str:
    base = job.description or job.requirements or ""
    if not base:
        base = f"{job.title} at {job.company}"
    return shorten(base.replace("\n", " "), width=length, placeholder="...")


__all__ = ["summarize_job"]

