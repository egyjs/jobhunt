from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(default="sqlite:///./jobhunt.db")
    openai_api_key: Optional[str] = Field(default=None, repr=False)
    log_level: str = Field(default="INFO")

    job_search_terms: List[str] = Field(default_factory=lambda: ["Laravel Developer"])
    job_locations: List[str] = Field(default_factory=lambda: ["Remote"])
    job_types: List[str] = Field(default_factory=list)
    job_salary_min: Optional[int] = None
    job_remote_only: bool = Field(default=True)

    linkedin_search_pages: int = Field(default=1, ge=1, le=5)
    indeed_search_pages: int = Field(default=1, ge=1, le=5)
    glassdoor_search_pages: int = Field(default=1, ge=1, le=5)

    company_career_pages: List[AnyHttpUrl] = Field(default_factory=list)

    scheduler_interval_minutes: int = Field(default=720, ge=5)

    resume_pdf_path: Path = Field(default=Path("profiles/resume.pdf"))
    profile_json_path: Path = Field(default=Path("profiles/profile.json"))

    storage_dir: Path = Field(default=Path("storage"))
    application_output_dir: Path = Field(default=Path("storage/applications"))
    logs_dir: Path = Field(default=Path("logs"))

    dashboard_base_url: Optional[AnyHttpUrl] = None

    browser_use_enabled: bool = Field(default=False)

    @field_validator("job_search_terms", "job_locations", "job_types", mode="before")
    @classmethod
    def _split_csv(cls, value):  # type: ignore[no-untyped-def]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("company_career_pages", mode="before")
    @classmethod
    def _split_company_pages(cls, value):  # type: ignore[no-untyped-def]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    settings.application_output_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    return settings


__all__ = ["Settings", "get_settings"]
