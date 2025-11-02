"""Job matching logic against the candidate profile."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from ..config import Settings
from ..database import session_scope
from ..models import Job
from ..repositories.job_repository import JobRepository
from .embeddings import EmbeddingService
from .profile import ProfileLoader


@dataclass(slots=True)
class MatchResult:
    job: Job
    score: float


class MatchingService:
    """Rank jobs against the candidate profile."""

    def __init__(self, settings: Settings, embeddings: EmbeddingService, profile_loader: ProfileLoader) -> None:
        self.settings = settings
        self.embeddings = embeddings
        self.profile_loader = profile_loader

    async def match(self, limit: int = 50) -> list[MatchResult]:
        with session_scope() as session:
            repo = JobRepository(session)
            jobs = repo.all_jobs()
            if not jobs:
                return []
            descriptions = [job.description for job in jobs]
            computed_embeddings = await self.embeddings.embed(descriptions) if descriptions else []
            candidate_embeddings = []
            for job, vector in zip(jobs, computed_embeddings, strict=False):
                if not job.embedding:
                    job.embedding = vector
                candidate_embeddings.append(job.embedding or vector)
            profile = self.profile_loader.load()
            resume_embedding = (await self.embeddings.embed([profile.combined_text]))[0]
            scores = await self.embeddings.similarity(resume_embedding, candidate_embeddings) if candidate_embeddings else []
            results = [self._score_job(job, score) for job, score in zip(jobs, scores, strict=False)]
            session.commit()

        results = [result for result in results if result.score >= self.settings.min_match_score]
        results.sort(key=lambda item: item.score, reverse=True)
        return results[:limit]

    def _score_job(self, job: Job, similarity: float) -> MatchResult:
        recency_bonus = 0.0
        if job.post_date:
            age_days = (dt.datetime.utcnow().replace(tzinfo=None) - job.post_date.replace(tzinfo=None)).days
            recency_bonus = max(0.0, 0.2 - (age_days * 0.01))
        final_score = float(similarity + recency_bonus)
        return MatchResult(job=job, score=final_score)


__all__ = ["MatchResult", "MatchingService"]
