from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional, Protocol


@dataclass
class FetchedJob:
    external_id: str
    title: str
    company: str
    location: Optional[str]
    description: str
    url: str
    salary: Optional[str]
    job_type: Optional[str]
    is_remote: bool
    posted_at: Optional[datetime]
    tags: List[str]
    summary: Optional[str] = None


class SearchParams(Protocol):
    terms: List[str]
    locations: List[str]
    job_types: List[str]
    remote_only: Optional[bool]
    salary_min: Optional[int]


class JobFetcher(Protocol):
    slug: str
    name: str

    async def fetch(self, params: SearchParams, limit: int) -> Iterable[FetchedJob]:
        ...


__all__ = ["FetchedJob", "SearchParams", "JobFetcher"]
