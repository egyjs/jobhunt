"""Workflow to produce ranked job matches."""

from __future__ import annotations

from app.services.matching import match_jobs, sync_application_scores


def run_match_workflow(limit: int = 50):
    sync_application_scores()
    return match_jobs(limit=limit)


__all__ = ["run_match_workflow"]

