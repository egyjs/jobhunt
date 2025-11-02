"""Base classes and utilities for job source fetchers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional, Protocol


@dataclass(slots=True)
class JobQuery:
    """Normalized search parameters shared across job sources."""

    keywords: List[str]
    locations: List[str]
    job_types: List[str]
    salary_min: Optional[int] = None
    limit: int = 50


@dataclass(slots=True)
class JobSourceResult:
    """Structured job posting returned from a fetcher."""

    source: str
    external_id: str
    title: str
    company: str
    location: Optional[str]
    description: Optional[str]
    requirements: Optional[str]
    salary: Optional[str]
    post_date: Optional[datetime]
    apply_link: Optional[str]
    tags: List[str]


class JobFetcher(Protocol):
    """Protocol all job fetchers must implement."""

    source: str

    async def fetch(self, query: JobQuery) -> Iterable[JobSourceResult]:
        """Fetch job postings for the given query."""


def tag_keywords(description: str | None, keywords: Iterable[str]) -> List[str]:
    """Return unique tags from description matched to keywords."""

    if not description:
        return []
    normalized = description.lower()
    tags = {kw.lower() for kw in keywords if kw.lower() in normalized}
    return sorted(tags)


__all__ = ["JobQuery", "JobSourceResult", "JobFetcher", "tag_keywords"]

