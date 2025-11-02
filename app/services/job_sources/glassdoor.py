"""Glassdoor job source scraping implementation."""

from __future__ import annotations

from typing import Iterable
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

from ...config import Settings
from ...utils.text import clean_whitespace
from .base import FetchedJob, JobQuery, JobSource


class GlassdoorJobSource(JobSource):
    source_name = "glassdoor"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def fetch(self, query: JobQuery, limit: int | None = None) -> Iterable[FetchedJob]:
        max_results = limit or self.settings.glassdoor_scrape_limit
        search_url = self._build_url(query)
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        async with httpx.AsyncClient(timeout=self.settings.job_board_timeout) as client:
            response = await client.get(search_url, headers=headers)
            response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results: list[FetchedJob] = []
        cards = soup.select("article.job-card") or soup.select("li.react-job-listing")
        for card in cards:
            if len(results) >= max_results:
                break
            job_id = card.get("data-id") or card.get("data-job-id") or ""
            title_tag = card.select_one("a.jobLink") or card.select_one("a[data-test='job-title']")
            company_tag = card.select_one("div.jobCardCompany") or card.select_one("div.job-info__company-name")
            location_tag = card.select_one("span.jobCardShelfItem")
            salary_tag = card.select_one("span[data-test='detailSalary']")
            snippet_tag = card.select_one("div.job-snippet") or card.select_one("p.job-snippet")
            link = title_tag.get("href") if title_tag else ""
            title = clean_whitespace(title_tag.text if title_tag else query.title)
            company = clean_whitespace(company_tag.text if company_tag else "")
            location = clean_whitespace(location_tag.text if location_tag else query.location)
            salary = clean_whitespace(salary_tag.text) if salary_tag else None
            description = clean_whitespace(snippet_tag.text if snippet_tag else title)
            apply_url = self._normalize_link(link)
            results.append(
                FetchedJob(
                    source=self.source_name,
                    external_id=job_id or quote_plus(apply_url or title),
                    title=title,
                    company=company,
                    location=location,
                    description=description,
                    apply_url=apply_url,
                    salary=salary,
                )
            )
        return results

    def _build_url(self, query: JobQuery) -> str:
        keyword = quote_plus(query.title)
        location = quote_plus(query.location)
        return f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keyword}&locT=C&locId=0&locKeyword={location}"

    def _normalize_link(self, href: str | None) -> str:
        if not href:
            return ""
        if href.startswith("http"):
            return href
        return f"https://www.glassdoor.com{href}"


__all__ = ["GlassdoorJobSource"]
