"""API routes for job discovery, matching, and application."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from ..schemas import (
    ApplyJobRequest,
    ApplyJobResponse,
    FetchJobsResponse,
    JobSchema,
    MatchJobResponse,
)
from ..services.registry import ServiceRegistry

router = APIRouter()


def get_services(request: Request) -> ServiceRegistry:
    return request.app.state.services


@router.post("/jobs/fetch", response_model=FetchJobsResponse)
async def fetch_jobs(services: ServiceRegistry = Depends(get_services)) -> FetchJobsResponse:
    counts = await services.job_fetcher.fetch_all()
    return FetchJobsResponse(counts=counts)


@router.get("/jobs/match", response_model=MatchJobResponse)
async def match_jobs(
    limit: int = Query(25, ge=1, le=100),
    services: ServiceRegistry = Depends(get_services),
) -> MatchJobResponse:
    results = await services.matching.match(limit=limit)
    jobs: List[JobSchema] = []
    for result in results:
        job = result.job
        tags = [tag.name for tag in job.tags]
        jobs.append(
            JobSchema(
                id=job.id,
                source=job.source,
                external_id=job.external_id,
                title=job.title,
                company=job.company,
                location=job.location,
                salary=job.salary,
                post_date=job.post_date,
                apply_url=job.apply_url,
                summary=job.summary,
                tags=tags,
                match_score=result.score,
            )
        )
    return MatchJobResponse(jobs=jobs)


@router.post("/jobs/apply", response_model=ApplyJobResponse)
async def apply_to_job(
    payload: ApplyJobRequest,
    services: ServiceRegistry = Depends(get_services),
) -> ApplyJobResponse:
    try:
        application = await services.application.prepare(
            job_id=payload.job_id,
            auto_submit=payload.auto_submit,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ApplyJobResponse(
        application_id=application.id,
        status=application.status,
        resume_path=application.resume_path,
        cover_letter_path=application.cover_letter_path,
    )


__all__ = ["router"]
