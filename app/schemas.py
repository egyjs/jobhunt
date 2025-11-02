"""Pydantic schemas for API serialization."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models import ApplicationStatus


class JobBase(BaseModel):
    id: int
    source: str
    external_id: str
    title: str
    company: str
    location: Optional[str] = None
    salary: Optional[str] = None
    post_date: Optional[datetime] = None
    apply_link: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class JobDetail(JobBase):
    description: Optional[str] = None
    requirements: Optional[str] = None
    summary: Optional[str] = None


class JobCreate(BaseModel):
    source: str
    external_id: str
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary: Optional[str] = None
    post_date: Optional[datetime] = None
    apply_link: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class ApplicationBase(BaseModel):
    id: int
    status: ApplicationStatus
    score: Optional[float] = None
    resume_path: Optional[str] = None
    cover_letter_path: Optional[str] = None
    notes: Optional[str] = None
    applied_at: Optional[datetime] = None
    updated_at: datetime


class ApplicationDetail(ApplicationBase):
    job: JobDetail


class FetchResponse(BaseModel):
    fetched: int
    created: int
    updated: int


class MatchResult(JobBase):
    score: float
    summary: str


class MatchResponse(BaseModel):
    matches: List[MatchResult]


class ApplyRequest(BaseModel):
    job_id: int
    auto_submit: bool = False


class ApplyResponse(BaseModel):
    application: ApplicationDetail


__all__ = [
    "JobBase",
    "JobDetail",
    "JobCreate",
    "ApplicationBase",
    "ApplicationDetail",
    "FetchResponse",
    "MatchResult",
    "MatchResponse",
    "ApplyRequest",
    "ApplyResponse",
]

