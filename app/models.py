"""SQLModel data models for job postings and applications."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, Enum as SQLAlchemyEnum, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel


class JobPosting(SQLModel, table=True):
    """Stored job posting details."""

    __tablename__ = "job_postings"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_job_source_external"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    source: str = Field(index=True)
    external_id: str = Field(index=True)
    title: str
    company: str
    location: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    requirements: Optional[str] = Field(default=None)
    salary: Optional[str] = Field(default=None)
    post_date: Optional[datetime] = Field(default=None, index=True)
    apply_link: Optional[str] = Field(default=None)
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False, default=list),
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    applications: Mapped[list["JobApplication"]] = Relationship(back_populates="job")


class ApplicationStatus(str, Enum):
    """Possible job application statuses."""

    NEW = "New"
    MATCHED = "Matched"
    APPLIED = "Applied"
    PENDING = "Pending Manual Review"
    INTERVIEW = "Interview"
    REJECTED = "Rejected"


class JobApplication(SQLModel, table=True):
    """Track application workflow and generated artifacts."""

    __tablename__ = "job_applications"

    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job_postings.id", index=True)
    status: ApplicationStatus = Field(
        sa_column=Column(SQLAlchemyEnum(ApplicationStatus), nullable=False),
        default=ApplicationStatus.NEW,
    )
    score: Optional[float] = Field(default=None)
    resume_path: Optional[str] = Field(default=None)
    cover_letter_path: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    applied_at: Optional[datetime] = Field(default=None)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    job: Mapped["JobPosting"] = Relationship(back_populates="applications")


class UserProfile(SQLModel, table=True):
    """Stored user profile and resume text for matching."""

    __tablename__ = "user_profile"

    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    headline: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    experience: Optional[str] = Field(default=None)
    skills: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False, default=list),
    )
    resume_text: Optional[str] = Field(default=None)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


__all__ = ["JobPosting", "JobApplication", "ApplicationStatus", "UserProfile"]

