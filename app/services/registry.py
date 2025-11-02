"""Service registry for dependency wiring."""

from __future__ import annotations

from dataclasses import dataclass

from ..config import Settings
from .ai import AITextGenerator
from .application_service import ApplicationService
from .embeddings import EmbeddingService
from .job_fetcher import JobFetcher
from .job_sources.company import CompanyFeedJobSource
from .job_sources.glassdoor import GlassdoorJobSource
from .job_sources.indeed import IndeedJobSource
from .job_sources.linkedin import LinkedInJobSource
from .matching import MatchingService
from .profile import ProfileLoader
from .tagging import TagService


@dataclass(slots=True)
class ServiceRegistry:
    """Materialize shared services from configuration."""

    settings: Settings

    def __post_init__(self) -> None:
        self.ai = AITextGenerator(
            api_key=self.settings.openai_api_key,
            model=self.settings.ai_model_name,
            temperature=self.settings.ai_temperature,
        )
        self.embeddings = EmbeddingService(self.settings.embeddings_model)
        self.profile_loader = ProfileLoader(self.settings)
        self.tag_service = TagService(self.settings.job_types)
        self.job_sources = [
            IndeedJobSource(self.settings),
            LinkedInJobSource(self.settings),
            GlassdoorJobSource(self.settings),
            CompanyFeedJobSource(self.settings),
        ]
        self.job_fetcher = JobFetcher(
            settings=self.settings,
            sources=self.job_sources,
            embeddings=self.embeddings,
            ai=self.ai,
            tag_service=self.tag_service,
        )
        self.matching = MatchingService(self.settings, self.embeddings, self.profile_loader)
        self.application = ApplicationService(self.settings, self.ai, self.profile_loader)


__all__ = ["ServiceRegistry"]
