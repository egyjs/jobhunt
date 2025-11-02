from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class JobSearchRequest(BaseModel):
    terms: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    job_types: List[str] = Field(default_factory=list)
    remote_only: Optional[bool] = None
    salary_min: Optional[int] = None
    limit: int = Field(default=50, ge=1, le=500)


class JobPostingBase(BaseModel):
    id: int
    source: str
    title: str
    company: str
    location: Optional[str]
    description: str
    url: str
    salary: Optional[str]
    job_type: Optional[str]
    is_remote: bool
    summary: Optional[str]
    posted_at: Optional[datetime]
    scraped_at: datetime
    tags: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class JobMatch(JobPostingBase):
    match_score: Optional[float]


class JobFetchResponse(BaseModel):
    jobs: List[JobPostingBase]
    total: int


class JobMatchResponse(BaseModel):
    jobs: List[JobMatch]
    total: int


class ApplyRequest(BaseModel):
    job_id: int
    auto_submit: bool = False


class ApplicationResponse(BaseModel):
    job_id: int
    status: str
    match_score: Optional[float]
    resume_path: Optional[str]
    cover_letter_path: Optional[str]
    notes: Optional[str]
    auto_submitted: bool
    submitted_at: Optional[datetime]


__all__ = [
    "JobSearchRequest",
    "JobPostingBase",
    "JobFetchResponse",
    "JobMatch",
    "JobMatchResponse",
    "ApplyRequest",
    "ApplicationResponse",
]
