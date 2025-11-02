"""Base classes for job source integrations."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Iterable, Protocol


@dataclass(slots=True)
class JobQuery:
    """Describe a normalized job search query."""

    title: str
    location: str
    job_types: tuple[str, ...] = ()


@dataclass(slots=True)
class FetchedJob:
    """Normalized representation of a job posting from a provider."""

    source: str
    external_id: str
    title: str
    company: str
    location: str
    description: str
    apply_url: str
    salary: str | None = None
    post_date: dt.datetime | None = None
    tags: tuple[str, ...] = ()


class JobSource(Protocol):
    """Protocol implemented by job board integrations."""

    source_name: str

    async def fetch(self, query: JobQuery, limit: int | None = None) -> Iterable[FetchedJob]:
        """Return an iterable of jobs that satisfy the query."""


__all__ = ["FetchedJob", "JobQuery", "JobSource"]
