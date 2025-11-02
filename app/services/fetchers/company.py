from __future__ import annotations

import logging
from datetime import datetime
from typing import Iterable, List, Sequence

import httpx
from bs4 import BeautifulSoup

from .base import FetchedJob, JobFetcher, SearchParams

logger = logging.getLogger(__name__)


class CompanyFeedFetcher(JobFetcher):
    slug = "company"
    name = "Company Careers"

    def __init__(self, feeds: Sequence[str]) -> None:
        self.feeds = list(feeds)

    async def fetch(self, params: SearchParams, limit: int) -> Iterable[FetchedJob]:
        if not self.feeds:
            return []
        jobs: List[FetchedJob] = []
        async with httpx.AsyncClient(timeout=20) as client:
            for feed_url in self.feeds:
                if len(jobs) >= limit:
                    break
                try:
                    response = await client.get(feed_url, headers={"User-Agent": "Mozilla/5.0 (JobApplyBot)"})
                    response.raise_for_status()
                except httpx.HTTPError as exc:
                    logger.warning("Company feed fetch failed (%s): %s", feed_url, exc)
                    continue
                jobs.extend(self._parse_feed(feed_url, response.text, params, limit - len(jobs)))
        return jobs

    def _parse_feed(
        self,
        feed_url: str,
        content: str,
        params: SearchParams,
        remaining: int,
    ) -> List[FetchedJob]:
        soup = BeautifulSoup(content, "xml")
        items = soup.select("item") or soup.select("entry")
        parsed: List[FetchedJob] = []
        for item in items:
            if remaining and len(parsed) >= remaining:
                break
            title_el = item.find("title")
            link_el = item.find("link")
            summary_el = item.find("description") or item.find("summary")
            pub_date_el = item.find("pubDate") or item.find("updated")

            title = title_el.get_text(strip=True) if title_el else "Unknown Role"
            url = link_el.get_text(strip=True) if link_el else feed_url
            summary = summary_el.get_text(" ", strip=True) if summary_el else ""
            posted_at = None
            if pub_date_el and pub_date_el.get_text(strip=True):
                try:
                    posted_at = datetime.fromisoformat(pub_date_el.get_text(strip=True).replace("Z", "+00:00"))
                except ValueError:
                    posted_at = None

            if params.terms and not any(term.lower() in summary.lower() or term.lower() in title.lower() for term in params.terms):
                continue
            if params.locations and not any(loc.lower() in summary.lower() or loc.lower() in title.lower() for loc in params.locations):
                continue

            parsed.append(
                FetchedJob(
                    external_id=f"{feed_url}:{title}",
                    title=title,
                    company=self._extract_company(feed_url) or "Company",
                    location=None,
                    description=summary,
                    url=url,
                    salary=None,
                    job_type=None,
                    is_remote="remote" in summary.lower(),
                    posted_at=posted_at,
                    tags=self._extract_tags(summary),
                    summary=summary,
                )
            )
        return parsed

    @staticmethod
    def _extract_company(feed_url: str) -> str:
        domain = feed_url.split("//")[-1]
        return domain.split("/")[0]

    @staticmethod
    def _extract_tags(text: str) -> List[str]:
        keywords = ["laravel", "php", "backend", "remote", "contract", "full-time"]
        lowered = text.lower()
        return [kw for kw in keywords if kw in lowered]


__all__ = ["CompanyFeedFetcher"]
