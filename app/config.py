"""Configuration utilities for the job automation MVP."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables or `.env` files."""

    database_url: str = Field(
        default="sqlite:///./jobhunt.db",
        description="SQLAlchemy connection string for persistence.",
    )
    job_titles: List[str] = Field(
        default_factory=lambda: ["Senior Laravel Developer"],
        description="Preferred job titles or keywords to search for.",
    )
    locations: List[str] = Field(
        default_factory=lambda: ["Remote", "Egypt", "Gulf"],
        description="Target locations for job searches.",
    )
    job_types: List[str] = Field(
        default_factory=lambda: ["Full-time"],
        description="Target job types (e.g., full-time, contract).",
    )
    salary_min: Optional[int] = Field(
        default=None,
        description="Minimum salary threshold for filtering results.",
    )
    fetch_limit: int = Field(
        default=50,
        description="Maximum number of jobs to pull per source each run.",
    )
    company_career_pages: List[str] = Field(
        default_factory=list,
        description="List of direct company career page URLs to monitor.",
    )
    resume_pdf_path: Path = Field(
        default=Path("data/resume.pdf"),
        description="Path to the base resume used for tailoring.",
    )
    profile_json_path: Path = Field(
        default=Path("data/user_profile.json"),
        description="Path to the structured user profile JSON file.",
    )
    output_dir: Path = Field(
        default=Path("output"),
        description="Root directory for generated artifacts.",
    )
    scheduler_interval_minutes: int = Field(
        default=120,
        description="Interval for automatic job fetch scheduling.",
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="Model name for optional OpenAI powered tailoring.",
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="Optional OpenAI API key for LLM-backed modules.",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @staticmethod
    def _split_csv(value: str | List[str]) -> List[str]:
        if isinstance(value, list):
            return value
        return [item.strip() for item in value.split(",") if item.strip()]

    _split_job_titles = field_validator("job_titles", mode="before")(_split_csv)
    _split_locations = field_validator("locations", mode="before")(_split_csv)
    _split_job_types = field_validator("job_types", mode="before")(_split_csv)
    _split_company_pages = field_validator("company_career_pages", mode="before")(_split_csv)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    settings = Settings()
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    (settings.output_dir / "resumes").mkdir(parents=True, exist_ok=True)
    (settings.output_dir / "cover_letters").mkdir(parents=True, exist_ok=True)
    (settings.output_dir / "logs").mkdir(parents=True, exist_ok=True)
    return settings


__all__ = ["Settings", "get_settings"]

