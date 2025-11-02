from __future__ import annotations

import logging
from typing import Iterable, List

import httpx
from bs4 import BeautifulSoup

from .base import FetchedJob, JobFetcher, SearchParams

logger = logging.getLogger(__name__)


class GlassdoorFetcher(JobFetcher):
    slug = "glassdoor"
    name = "Glassdoor"

    def __init__(self, pages: int = 1) -> None:
        self.pages = pages
        self.base_url = "https://www.glassdoor.com/Job/jobs.htm"

    async def fetch(self, params: SearchParams, limit: int) -> Iterable[FetchedJob]:
        jobs: List[FetchedJob] = []
        async with httpx.AsyncClient(timeout=20) as client:
            for term in params.terms or [""]:
                for location in params.locations or [""]:
                    for page in range(1, self.pages + 1):
                        if len(jobs) >= limit:
                            break
                        query_params = {
                            "keyword": term,
                            "locT": "C",
                            "locId": "-1",
                            "locKeyword": location,
                            "p": page,
                        }
                        try:
                            response = await client.get(
                                self.base_url,
                                params=query_params,
                                headers={"User-Agent": "Mozilla/5.0 (JobApplyBot)"},
                            )
                            response.raise_for_status()
                        except httpx.HTTPError as exc:
                            logger.warning("Glassdoor fetch failed: %s", exc)
                            continue
                        jobs.extend(self._parse_results(response.text, limit - len(jobs)))
        return jobs

    def _parse_results(self, html: str, remaining: int) -> List[FetchedJob]:
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select("li.react-job-listing")
        parsed: List[FetchedJob] = []
        for card in cards:
            if remaining and len(parsed) >= remaining:
                break
            job_id = card.get("data-id") or card.get("data-job-id")
            if not job_id:
                continue
            title_el = card.select_one("a.jobLink span") or card.select_one("a.jobLink")
            company_el = card.select_one("div.d-flex div")
            location_el = card.select_one("span.pr-xxsm")
            salary_el = card.select_one("div.salary-estimate")
            summary_el = card.select_one("div.job-snippet")

            title = title_el.get_text(strip=True) if title_el else ""
            company = company_el.get_text(strip=True) if company_el else ""
            location = location_el.get_text(strip=True) if location_el else None
            salary = salary_el.get_text(strip=True) if salary_el else None
            summary = summary_el.get_text(" ", strip=True) if summary_el else None
            url_el = card.select_one("a.jobLink")
            url = "https://www.glassdoor.com" + url_el["href"] if url_el and url_el.has_attr("href") else ""

            parsed.append(
                FetchedJob(
                    external_id=str(job_id),
                    title=title or "Unknown Role",
                    company=company or "Unknown Company",
                    location=location,
                    description=summary or "",
                    url=url,
                    salary=salary,
                    job_type=None,
                    is_remote="remote" in (summary or "").lower(),
                    posted_at=None,
                    tags=self._extract_tags(summary or ""),
                    summary=summary,
                )
            )
        return parsed

    @staticmethod
    def _extract_tags(text: str) -> List[str]:
        keywords = ["laravel", "php", "aws", "rest", "microservices", "lead", "remote"]
        lowered = text.lower()
        return [kw for kw in keywords if kw in lowered]


__all__ = ["GlassdoorFetcher"]
