from __future__ import annotations

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ...config import get_settings
from ...database import get_session
from ...repositories import JobRepository
from ...schemas import (
    ApplicationResponse,
    ApplyRequest,
    JobFetchResponse,
    JobMatchResponse,
    JobPostingBase,
    JobSearchRequest,
)
from ...services.application import ApplicationService
from ...services.job_discovery import JobDiscoveryService
from ...services.matcher import JobMatcher
from ...services.search_params import DiscoveryParams

router = APIRouter(prefix="/jobs", tags=["jobs"])

settings = get_settings()
_discovery = JobDiscoveryService()
_matcher = JobMatcher()
_application = ApplicationService()


def _map_posting(posting) -> JobPostingBase:
    tags: List[str] = []
    if posting.tags_json:
        try:
            tags = json.loads(posting.tags_json)
        except json.JSONDecodeError:
            tags = []
    return JobPostingBase(
        id=posting.id,
        source=posting.source.slug if posting.source else "unknown",
        title=posting.title,
        company=posting.company,
        location=posting.location,
        description=posting.description,
        url=posting.url,
        salary=posting.salary,
        job_type=posting.job_type,
        is_remote=posting.is_remote,
        summary=posting.summary,
        posted_at=posting.posted_at,
        scraped_at=posting.scraped_at,
        tags=tags,
    )


@router.post("/fetch", response_model=JobFetchResponse)
async def fetch_jobs(request: JobSearchRequest, session: Session = Depends(get_session)) -> JobFetchResponse:
    params = DiscoveryParams(
        terms=request.terms or settings.job_search_terms,
        locations=request.locations or settings.job_locations,
        job_types=request.job_types or settings.job_types,
        remote_only=settings.job_remote_only if request.remote_only is None else request.remote_only,
        salary_min=request.salary_min or settings.job_salary_min,
    )
    persisted = await _discovery.fetch_and_store(session, params, limit=request.limit)
    jobs = [_map_posting(posting) for posting in persisted]
    return JobFetchResponse(jobs=jobs, total=len(jobs))


@router.get("/match", response_model=JobMatchResponse)
def match_jobs(limit: int = 50, session: Session = Depends(get_session)) -> JobMatchResponse:
    repo = JobRepository(session)
    postings = repo.list_recent_jobs(limit)
    matches = _matcher.rank_jobs(session, postings)
    matches = matches[:limit]
    return JobMatchResponse(jobs=matches, total=len(matches))


@router.post("/apply", response_model=ApplicationResponse)
def apply_job(payload: ApplyRequest, session: Session = Depends(get_session)) -> ApplicationResponse:
    repo = JobRepository(session)
    job = repo.get_job(payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _application.apply(session, payload.job_id, payload.auto_submit)


__all__ = ["router"]
