"""SQLAlchemy models for the JobApply MVP."""

from __future__ import annotations

import datetime as dt
from typing import Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_job_source_external"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(50), index=True)
    external_id: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    company: Mapped[str] = mapped_column(String(255), index=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    salary: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    post_date: Mapped[Optional[dt.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    apply_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[list[JobTag]] = relationship("JobTag", back_populates="job", cascade="all, delete-orphan")
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    embedding: Mapped[Optional[list[float]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow
    )

    applications: Mapped[list[Application]] = relationship("Application", back_populates="job", cascade="all, delete-orphan")


class JobTag(Base):
    __tablename__ = "job_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)

    job: Mapped[Job] = relationship("Job", back_populates="tags")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    auto_submitted: Mapped[bool] = mapped_column(Boolean, default=False)
    resume_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    cover_letter_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow
    )

    job: Mapped[Job] = relationship("Job", back_populates="applications")


__all__ = ["Application", "Job", "JobTag"]
