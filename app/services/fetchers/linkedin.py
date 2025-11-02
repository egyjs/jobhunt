from __future__ import annotations

import logging
from typing import Iterable, List

import httpx
from bs4 import BeautifulSoup

from .base import FetchedJob, JobFetcher, SearchParams

logger = logging.getLogger(__name__)


class LinkedInFetcher(JobFetcher):
    slug = "linkedin"
    name = "LinkedIn"

    def __init__(self, pages: int = 1) -> None:
        self.pages = pages
        self.base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    async def fetch(self, params: SearchParams, limit: int) -> Iterable[FetchedJob]:
        jobs: List[FetchedJob] = []
        async with httpx.AsyncClient(timeout=20) as client:
            for term in params.terms or [""]:
                for location in params.locations or [""]:
                    for page in range(self.pages):
                        if len(jobs) >= limit:
                            break
                        start = page * 25
                        query_params = {
                            "keywords": term,
                            "location": location,
                            "start": start,
                        }
                        try:
                            response = await client.get(
                                self.base_url,
                                params=query_params,
                                headers={
                                    "User-Agent": "Mozilla/5.0 (JobApplyBot)",
                                },
                            )
                            response.raise_for_status()
                        except httpx.HTTPError as exc:
                            logger.warning("LinkedIn fetch failed: %s", exc)
                            continue
                        jobs.extend(self._parse_results(response.text, limit - len(jobs)))
        return jobs

    def _parse_results(self, html_fragment: str, remaining: int) -> List[FetchedJob]:
        soup = BeautifulSoup(html_fragment, "html.parser")
        cards = soup.select("li")
        parsed: List[FetchedJob] = []
        for card in cards:
            if remaining and len(parsed) >= remaining:
                break
            job_id = card.get("data-id") or card.get("data-entity-urn")
            if not job_id:
                continue
            title_el = card.select_one("h3.base-search-card__title")
            company_el = card.select_one("h4.base-search-card__subtitle")
            location_el = card.select_one("span.job-search-card__location")
            description = card.select_one("p.job-search-card__snippet")
            link_el = card.select_one("a.base-card__full-link")
            title = title_el.get_text(strip=True) if title_el else ""
            company = company_el.get_text(strip=True) if company_el else ""
            location = location_el.get_text(strip=True) if location_el else None
            summary = description.get_text(" ", strip=True) if description else None
            url = link_el["href"].split("?")[0] if link_el and link_el.has_attr("href") else ""
            tags = self._extract_tags(summary or "")

            parsed.append(
                FetchedJob(
                    external_id=str(job_id),
                    title=title or "Unknown Role",
                    company=company or "Unknown Company",
                    location=location,
                    description=summary or "",
                    url=url,
                    salary=None,
                    job_type=None,
                    is_remote="remote" in (summary or "").lower(),
                    posted_at=None,
                    tags=tags,
                    summary=summary,
                )
            )
        return parsed

    @staticmethod
    def _extract_tags(text: str) -> List[str]:
        keywords = ["laravel", "php", "api", "lead", "aws", "full stack", "remote"]
        lowered = text.lower()
        return [kw for kw in keywords if kw in lowered]


__all__ = ["LinkedInFetcher"]
