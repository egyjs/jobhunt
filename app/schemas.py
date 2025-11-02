"""Pydantic schemas for API responses and requests."""

from __future__ import annotations

import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field


class JobTagSchema(BaseModel):
    name: str


class JobSchema(BaseModel):
    id: int
    source: str
    external_id: str
    title: str
    company: str
    location: Optional[str]
    salary: Optional[str]
    post_date: Optional[dt.datetime]
    apply_url: Optional[str]
    summary: Optional[str]
    tags: list[str]
    match_score: Optional[float] = Field(default=None, description="Similarity score when ranked")

    class Config:
        from_attributes = True


class FetchJobsResponse(BaseModel):
    counts: dict[str, int]


class MatchJobResponse(BaseModel):
    jobs: list[JobSchema]


class ApplyJobRequest(BaseModel):
    job_id: int
    auto_submit: bool = False
    notes: Optional[str] = None


class ApplyJobResponse(BaseModel):
    application_id: int
    status: str
    resume_path: Optional[str]
    cover_letter_path: Optional[str]


__all__ = [
    "ApplyJobRequest",
    "ApplyJobResponse",
    "FetchJobsResponse",
    "JobSchema",
    "MatchJobResponse",
]
