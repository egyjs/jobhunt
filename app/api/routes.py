"""FastAPI route definitions for the MVP."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas import ApplyRequest, ApplyResponse, FetchResponse, MatchResponse
from app.services.profile import load_profile_from_json
from app.workflows.apply import run_apply_workflow
from app.workflows.fetch import run_fetch_workflow
from app.workflows.match import run_match_workflow


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/fetch", response_model=FetchResponse)
async def fetch_jobs() -> FetchResponse:
    """Trigger job discovery across all configured sources."""

    fetched, created, updated = await run_fetch_workflow()
    return FetchResponse(fetched=fetched, created=created, updated=updated)


@router.get("/match", response_model=MatchResponse)
async def match_jobs(limit: int = 25) -> MatchResponse:
    matches = run_match_workflow(limit=limit)
    return MatchResponse(matches=matches)


@router.post("/apply", response_model=ApplyResponse)
async def apply_to_job(payload: ApplyRequest) -> ApplyResponse:
    try:
        return run_apply_workflow(job_id=payload.job_id, auto_submit=payload.auto_submit)
    except ValueError as exc:  # pragma: no cover - FastAPI handles HTTP translation
        raise HTTPException(status_code=404, detail=str(exc)) from exc


__all__ = ["router"]

