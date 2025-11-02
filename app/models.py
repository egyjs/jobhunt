from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class JobSource(SQLModel, table=True):
    __tablename__ = "job_sources"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    slug: str = Field(index=True, unique=True)
    homepage_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    postings: List["JobPosting"] = Relationship(back_populates="source")


class JobPosting(SQLModel, table=True):
    __tablename__ = "job_postings"
    __table_args__ = (UniqueConstraint("source_id", "external_id", name="uq_job_posting_source_external"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="job_sources.id", index=True)
    external_id: str = Field(index=True)
    title: str = Field(index=True)
    company: str = Field(index=True)
    location: Optional[str] = Field(default=None, index=True)
    description: str
    url: str
    salary: Optional[str] = None
    job_type: Optional[str] = None
    is_remote: bool = Field(default=False, index=True)
    tags_json: Optional[str] = None
    posted_at: Optional[datetime] = Field(default=None, index=True)
    scraped_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    summary: Optional[str] = None

    source: Optional[JobSource] = Relationship(back_populates="postings")
    applications: List["ApplicationRecord"] = Relationship(back_populates="job_posting")


class ApplicationRecord(SQLModel, table=True):
    __tablename__ = "job_applications"

    id: Optional[int] = Field(default=None, primary_key=True)
    job_posting_id: int = Field(foreign_key="job_postings.id")
    status: str = Field(default="pending", index=True)
    match_score: Optional[float] = Field(default=None, index=True)
    resume_path: Optional[str] = None
    cover_letter_path: Optional[str] = None
    notes: Optional[str] = None
    auto_submitted: bool = Field(default=False)
    submitted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    job_posting: Optional[JobPosting] = Relationship(back_populates="applications")


class ResumeIndex(SQLModel, table=True):
    __tablename__ = "resume_index"
    id: Optional[int] = Field(default=None, primary_key=True)
    extracted_text: str
    last_updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


__all__ = ["JobSource", "JobPosting", "ApplicationRecord", "ResumeIndex"]
