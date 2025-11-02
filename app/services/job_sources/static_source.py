"""Static JSON-backed job source used for the MVP demo."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from .base import JobFetcher, JobQuery, JobSourceResult, tag_keywords


class StaticJSONJobFetcher(JobFetcher):
    """Load job listings from a JSON file on disk."""

    def __init__(self, source: str, json_path: Path) -> None:
        self.source = source
        self.json_path = json_path

    async def fetch(self, query: JobQuery) -> Iterable[JobSourceResult]:
        if not self.json_path.exists():
            return []

        with self.json_path.open("r", encoding="utf-8") as handle:
            payload: List[dict] = json.load(handle)

        results: List[JobSourceResult] = []
        for entry in payload[: query.limit]:
            description = entry.get("description")
            tags = entry.get("tags") or tag_keywords(description, query.keywords)
            post_date_raw = entry.get("post_date")
            post_date = (
                datetime.fromisoformat(post_date_raw)
                if post_date_raw
                else None
            )
            results.append(
                JobSourceResult(
                    source=self.source,
                    external_id=str(entry.get("external_id") or entry.get("id")),
                    title=entry.get("title", ""),
                    company=entry.get("company", ""),
                    location=entry.get("location"),
                    description=description,
                    requirements=entry.get("requirements"),
                    salary=entry.get("salary"),
                    post_date=post_date,
                    apply_link=entry.get("apply_link"),
                    tags=tags,
                )
            )
        return results


def static_fetchers() -> List[JobFetcher]:
    """Return configured static fetchers for MVP demo data."""

    data_dir = Path("data/sample_jobs")
    return [
        StaticJSONJobFetcher("linkedin", data_dir / "linkedin.json"),
        StaticJSONJobFetcher("indeed", data_dir / "indeed.json"),
        StaticJSONJobFetcher("glassdoor", data_dir / "glassdoor.json"),
        StaticJSONJobFetcher("company", data_dir / "company.json"),
    ]


__all__ = ["StaticJSONJobFetcher", "static_fetchers"]

