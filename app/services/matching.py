"""Matching engine between user profile/resume and job postings."""

from __future__ import annotations

from typing import List, Sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlmodel import select

from app.database import session_scope
from app.models import ApplicationStatus, JobApplication, JobPosting, UserProfile
from app.schemas import MatchResult


def _load_user_profile(session) -> UserProfile | None:
    return session.exec(select(UserProfile)).first()


def _prepare_corpus(jobs: Sequence[JobPosting], profile: UserProfile | None) -> List[str]:
    base = []
    for job in jobs:
        text = "\n".join(
            filter(
                None,
                [job.title, job.company, job.description or "", job.requirements or ""],
            )
        )
        base.append(text)
    if profile:
        resume_text = profile.resume_text or ""
        profile_text = "\n".join(
            filter(
                None,
                [profile.full_name, profile.headline or "", profile.summary or "", resume_text],
            )
        )
        base.append(profile_text)
    return base


def _vectorize(corpus: List[str]):
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(corpus)
    return vectorizer, matrix


def _score_jobs(jobs: Sequence[JobPosting], profile: UserProfile | None) -> List[float]:
    if not jobs:
        return []

    corpus = _prepare_corpus(jobs, profile)
    _, matrix = _vectorize(corpus)
    if not profile:
        return [0.0 for _ in jobs]

    profile_vector = matrix[-1]
    job_matrix = matrix[:-1]
    scores = cosine_similarity(job_matrix, profile_vector).flatten()
    return scores.tolist()


def match_jobs(limit: int = 50) -> List[MatchResult]:
    """Return ranked job matches with similarity scores."""

    with session_scope() as session:
        jobs = session.exec(select(JobPosting)).all()
        profile = _load_user_profile(session)

    scores = _score_jobs(jobs, profile)
    scored_jobs = sorted(
        zip(jobs, scores), key=lambda pair: pair[1], reverse=True
    )[:limit]

    results: List[MatchResult] = []
    for job, score in scored_jobs:
        summary = (job.description or job.requirements or "").split(". ")[0]
        if not summary:
            summary = f"{job.title} at {job.company}"
        results.append(
            MatchResult(
                id=job.id,
                source=job.source,
                external_id=job.external_id,
                title=job.title,
                company=job.company,
                location=job.location,
                salary=job.salary,
                post_date=job.post_date,
                apply_link=job.apply_link,
                tags=job.tags,
                score=round(float(score), 4),
                summary=summary,
            )
        )
    return results


def sync_application_scores() -> None:
    """Persist similarity scores to application records."""

    matches = match_jobs()
    score_lookup = {match.id: match.score for match in matches}
    with session_scope() as session:
        for job_id, score in score_lookup.items():
            statement = select(JobApplication).where(JobApplication.job_id == job_id)
            application = session.exec(statement).one_or_none()
            if not application:
                application = JobApplication(job_id=job_id, status=ApplicationStatus.MATCHED)
                session.add(application)
            application.score = score
            application.status = ApplicationStatus.MATCHED


__all__ = ["match_jobs", "sync_application_scores"]

