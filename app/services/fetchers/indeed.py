from __future__ import annotations

import asyncio
import logging
from typing import Iterable, List

import httpx
from bs4 import BeautifulSoup

from .base import FetchedJob, JobFetcher, SearchParams

logger = logging.getLogger(__name__)


class IndeedFetcher(JobFetcher):
    slug = "indeed"
    name = "Indeed"

    def __init__(self, pages: int = 1) -> None:
        self.pages = pages
        self.base_url = "https://www.indeed.com/jobs"

    async def fetch(self, params: SearchParams, limit: int) -> Iterable[FetchedJob]:
        semaphore = asyncio.Semaphore(2)
        jobs: List[FetchedJob] = []
        search_terms = params.terms or [""]
        locations = params.locations or [""]

        async with httpx.AsyncClient(timeout=20) as client:
            for term in search_terms:
                for location in locations:
                    for page in range(self.pages):
                        if len(jobs) >= limit:
                            break
                        query_params = {
                            "q": term,
                            "l": location,
                            "start": page * 10,
                            "fromage": 7,
                        }
                        async with semaphore:
                            try:
                                response = await client.get(self.base_url, params=query_params, headers={
                                    "User-Agent": "Mozilla/5.0 (JobApplyBot)",
                                })
                                response.raise_for_status()
                            except httpx.HTTPError as exc:
                                logger.warning("Indeed fetch failed: %s", exc)
                                continue
                        jobs.extend(self._parse_results(response.text, limit - len(jobs)))
        return jobs

    def _parse_results(self, html: str, remaining: int) -> List[FetchedJob]:
        soup = BeautifulSoup(html, "html.parser")
        job_cards = soup.select(".resultContent") or soup.select("a.tapItem")
        parsed: List[FetchedJob] = []
        for card in job_cards:
            if remaining and len(parsed) >= remaining:
                break
            job_id = card.get("data-jk") or card.get("data-mobtk")
            if not job_id:
                anchor = card.find("a", href=True)
                if anchor and "jk=" in anchor["href"]:
                    job_id = anchor["href"].split("jk=")[-1].split("&")[0]
            if not job_id:
                continue
            title_el = card.select_one("h2.jobTitle span") or card.select_one("span[title]")
            company_el = card.select_one("span.companyName")
            location_el = card.select_one("div.companyLocation")
            summary_el = card.select_one("div.job-snippet")

            title = title_el.get_text(strip=True) if title_el else ""
            company = company_el.get_text(strip=True) if company_el else ""
            location = location_el.get_text(strip=True) if location_el else None
            summary = summary_el.get_text(" ", strip=True) if summary_el else None

            url = f"https://www.indeed.com/viewjob?jk={job_id}"
            is_remote = bool(summary and "remote" in summary.lower())
            posted_at = None
            tags: List[str] = []
            if summary:
                tags = self._extract_tags(summary)

            parsed.append(
                FetchedJob(
                    external_id=job_id,
                    title=title or "Unknown Role",
                    company=company or "Unknown Company",
                    location=location,
                    description=summary or "",
                    url=url,
                    salary=None,
                    job_type=None,
                    is_remote=is_remote,
                    posted_at=posted_at,
                    tags=tags,
                    summary=summary,
                )
            )
        return parsed

    @staticmethod
    def _extract_tags(text: str) -> List[str]:
        keywords = ["laravel", "php", "node", "react", "lead", "remote", "full-time", "contract"]
        lowered = text.lower()
        return [kw for kw in keywords if kw in lowered]


__all__ = ["IndeedFetcher"]
