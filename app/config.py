"""Configuration loader for the JobApply MVP."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Sequence

from dotenv import load_dotenv


@dataclass(slots=True)
class Settings:
    """Runtime configuration values loaded from environment variables."""

    database_url: str = "sqlite:///./data/jobapply.db"
    openai_api_key: str | None = None
    job_titles: List[str] = field(default_factory=lambda: ["Senior Laravel Developer"])
    job_locations: List[str] = field(default_factory=lambda: ["Remote", "Egypt"])
    job_types: List[str] = field(default_factory=lambda: ["full-time", "remote"])
    company_feeds: List[str] = field(default_factory=list)
    embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    scheduler_enabled: bool = True
    scheduler_interval_minutes: int = 60 * 12
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    application_output_dir: str = "data/applications"
    profile_json_path: str = "data/profile.json"
    resume_pdf_path: str = "data/resume.pdf"
    min_match_score: float = 0.35
    fetch_page_size: int = 20
    linkedin_scrape_limit: int = 25
    glassdoor_scrape_limit: int = 25
    indeed_max_entries: int = 50
    company_max_entries: int = 50
    job_board_timeout: float = 15.0
    ai_model_name: str = "gpt-4o-mini"
    ai_temperature: float = 0.2
    timezone: str = "UTC"
    dashboard_refresh_seconds: int = 30

    @property
    def job_queries(self) -> Sequence[tuple[str, str]]:
        return [(title, location) for title in self.job_titles for location in self.job_locations]


_SETTINGS: Settings | None = None


def _parse_list(value: str | None) -> List[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except json.JSONDecodeError:
        pass
    return [item.strip() for item in value.split(",") if item.strip()]


def get_settings() -> Settings:
    """Load settings from environment variables once per process."""
    global _SETTINGS
    if _SETTINGS is not None:
        return _SETTINGS

    load_dotenv()

    database_url = os.getenv("DATABASE_URL") or Settings.database_url
    openai_api_key = os.getenv("OPENAI_API_KEY")
    job_titles = _parse_list(os.getenv("JOB_TITLES")) or Settings.job_titles
    job_locations = _parse_list(os.getenv("JOB_LOCATIONS")) or Settings.job_locations
    job_types = _parse_list(os.getenv("JOB_TYPES")) or Settings.job_types
    company_feeds = _parse_list(os.getenv("COMPANY_FEEDS")) or Settings.company_feeds
    cors_origins = _parse_list(os.getenv("CORS_ORIGINS")) or Settings.cors_origins

    embeddings_model = os.getenv("EMBEDDINGS_MODEL") or Settings.embeddings_model
    scheduler_enabled = os.getenv("SCHEDULER_ENABLED", "true").lower() in {"1", "true", "yes", "on"}
    scheduler_interval_minutes = int(os.getenv("SCHEDULER_INTERVAL_MINUTES") or Settings.scheduler_interval_minutes)
    application_output_dir = os.getenv("APPLICATION_OUTPUT_DIR") or Settings.application_output_dir
    profile_json_path = os.getenv("PROFILE_JSON_PATH") or Settings.profile_json_path
    resume_pdf_path = os.getenv("RESUME_PDF_PATH") or Settings.resume_pdf_path
    min_match_score = float(os.getenv("MIN_MATCH_SCORE") or Settings.min_match_score)
    fetch_page_size = int(os.getenv("FETCH_PAGE_SIZE") or Settings.fetch_page_size)
    linkedin_scrape_limit = int(os.getenv("LINKEDIN_SCRAPE_LIMIT") or Settings.linkedin_scrape_limit)
    glassdoor_scrape_limit = int(os.getenv("GLASSDOOR_SCRAPE_LIMIT") or Settings.glassdoor_scrape_limit)
    indeed_max_entries = int(os.getenv("INDEED_MAX_ENTRIES") or Settings.indeed_max_entries)
    company_max_entries = int(os.getenv("COMPANY_MAX_ENTRIES") or Settings.company_max_entries)
    job_board_timeout = float(os.getenv("JOB_BOARD_TIMEOUT") or Settings.job_board_timeout)
    ai_model_name = os.getenv("AI_MODEL_NAME") or Settings.ai_model_name
    ai_temperature = float(os.getenv("AI_TEMPERATURE") or Settings.ai_temperature)
    timezone = os.getenv("TIMEZONE") or Settings.timezone
    dashboard_refresh_seconds = int(os.getenv("DASHBOARD_REFRESH_SECONDS") or Settings.dashboard_refresh_seconds)

    Path(application_output_dir).mkdir(parents=True, exist_ok=True)

    _SETTINGS = Settings(
        database_url=database_url,
        openai_api_key=openai_api_key,
        job_titles=job_titles,
        job_locations=job_locations,
        job_types=job_types,
        company_feeds=company_feeds,
        embeddings_model=embeddings_model,
        scheduler_enabled=scheduler_enabled,
        scheduler_interval_minutes=scheduler_interval_minutes,
        cors_origins=cors_origins,
        application_output_dir=application_output_dir,
        profile_json_path=profile_json_path,
        resume_pdf_path=resume_pdf_path,
        min_match_score=min_match_score,
        fetch_page_size=fetch_page_size,
        linkedin_scrape_limit=linkedin_scrape_limit,
        glassdoor_scrape_limit=glassdoor_scrape_limit,
        indeed_max_entries=indeed_max_entries,
        company_max_entries=company_max_entries,
        job_board_timeout=job_board_timeout,
        ai_model_name=ai_model_name,
        ai_temperature=ai_temperature,
        timezone=timezone,
        dashboard_refresh_seconds=dashboard_refresh_seconds,
    )
    return _SETTINGS


__all__ = ["Settings", "get_settings"]
