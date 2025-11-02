"""LinkedIn job source integration via public search endpoint."""

from __future__ import annotations

import datetime as dt
from typing import Iterable
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

from ...config import Settings
from ...utils.text import clean_whitespace
from .base import FetchedJob, JobQuery, JobSource


class LinkedInJobSource(JobSource):
    source_name = "linkedin"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def fetch(self, query: JobQuery, limit: int | None = None) -> Iterable[FetchedJob]:
        max_results = limit or self.settings.linkedin_scrape_limit
        params = {
            "keywords": query.title,
            "location": query.location,
            "f_TPR": "r86400",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        async with httpx.AsyncClient(timeout=self.settings.job_board_timeout) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select("li")
        results: list[FetchedJob] = []
        for item in items:
            if len(results) >= max_results:
                break
            job_id = item.get("data-entity-urn") or item.get("data-id") or ""
            title_tag = item.select_one("h3")
            company_tag = item.select_one("h4")
            location_tag = item.select_one("span.job-search-card__location")
            time_tag = item.select_one("time")
            description_tag = item.select_one("div.job-search-card__snippet")
            link_tag = item.select_one("a")
            title = clean_whitespace(title_tag.text if title_tag else "")
            company = clean_whitespace(company_tag.text if company_tag else "")
            location = clean_whitespace(location_tag.text if location_tag else query.location)
            description = clean_whitespace(description_tag.text if description_tag else title)
            link = link_tag.get("href") if link_tag else ""
            post_date = None
            if time_tag and time_tag.has_attr("datetime"):
                try:
                    post_date = dt.datetime.fromisoformat(time_tag["datetime"])
                    if post_date.tzinfo is None:
                        post_date = post_date.replace(tzinfo=dt.timezone.utc)
                except ValueError:
                    post_date = None
            results.append(
                FetchedJob(
                    source=self.source_name,
                    external_id=job_id or quote_plus(link or title),
                    title=title,
                    company=company,
                    location=location,
                    description=description,
                    apply_url=link,
                    post_date=post_date,
                )
            )
        return results


__all__ = ["LinkedInJobSource"]
