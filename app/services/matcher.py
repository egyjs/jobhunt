from __future__ import annotations

import logging
from datetime import datetime
from typing import Iterable, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlmodel import Session, select

from ..config import get_settings
from ..models import JobPosting, ResumeIndex
from ..schemas import JobMatch
from ..utils.profile import flatten_profile, load_profile
from ..utils.resume import extract_text_from_pdf

logger = logging.getLogger(__name__)


class JobMatcher:
    """Scores job postings against the candidate profile."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def rank_jobs(self, session: Session, jobs: Iterable[JobPosting]) -> List[JobMatch]:
        candidate_text = self.load_candidate_corpus(session)
        jobs_list = list(jobs)
        job_texts = [self._job_to_text(job) for job in jobs_list]
        if not job_texts:
            return []

        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform([candidate_text, *job_texts])
        candidate_vector = tfidf_matrix[0]
        job_vectors = tfidf_matrix[1:]
        scores = cosine_similarity(candidate_vector, job_vectors).flatten()

        ranked: List[Tuple[JobPosting, float]] = sorted(
            zip(jobs_list, scores), key=lambda pair: pair[1], reverse=True
        )
        matches: List[JobMatch] = []
        for job, score in ranked:
            tags = self._tags_from_json(job.tags_json)
            matches.append(
                JobMatch(
                    id=job.id,
                    source=job.source.slug if job.source else "unknown",
                    title=job.title,
                    company=job.company,
                    location=job.location,
                    description=job.description,
                    url=job.url,
                    salary=job.salary,
                    job_type=job.job_type,
                    is_remote=job.is_remote,
                    summary=job.summary,
                    posted_at=job.posted_at,
                    scraped_at=job.scraped_at,
                    tags=tags,
                    match_score=float(score),
                )
            )
        return matches

    def load_candidate_corpus(self, session: Session) -> str:
        resume_text = extract_text_from_pdf(self.settings.resume_pdf_path)
        profile_data = load_profile(self.settings.profile_json_path)
        profile_text = flatten_profile(profile_data)
        corpus = "\n".join(part for part in [resume_text, profile_text] if part)

        record = session.exec(select(ResumeIndex)).one_or_none()
        if record:
            record.extracted_text = corpus
            record.last_updated_at = datetime.utcnow()
            session.add(record)
        else:
            session.add(ResumeIndex(extracted_text=corpus, last_updated_at=datetime.utcnow()))
        session.commit()
        return corpus

    @staticmethod
    def _job_to_text(job: JobPosting) -> str:
        parts = [job.title, job.company, job.description or "", job.summary or ""]
        if job.tags_json:
            parts.append(job.tags_json)
        return "\n".join(part for part in parts if part)

    @staticmethod
    def _tags_from_json(tags_json: str | None) -> List[str]:
        if not tags_json:
            return []
        try:
            import json

            return json.loads(tags_json)
        except Exception:  # noqa: BLE001
            logger.warning("Failed to parse tags json: %s", tags_json)
            return []


__all__ = ["JobMatcher"]
