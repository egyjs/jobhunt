"""Indeed job source implementation using RSS feeds."""

from __future__ import annotations

import datetime as dt
from email.utils import parsedate_to_datetime
from typing import Iterable
from urllib.parse import quote_plus

import feedparser
import httpx
from bs4 import BeautifulSoup

from ...config import Settings
from .base import FetchedJob, JobQuery, JobSource


class IndeedJobSource(JobSource):
    source_name = "indeed"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def fetch(self, query: JobQuery, limit: int | None = None) -> Iterable[FetchedJob]:
        max_entries = limit or self.settings.indeed_max_entries
        rss_url = self._build_rss_url(query)
        async with httpx.AsyncClient(timeout=self.settings.job_board_timeout) as client:
            response = await client.get(rss_url)
            response.raise_for_status()
        feed = feedparser.parse(response.text)
        results: list[FetchedJob] = []
        for entry in feed.entries[:max_entries]:
            description = BeautifulSoup(entry.get("summary", ""), "html.parser").get_text(" ")
            post_date = self._parse_date(entry.get("published_parsed"))
            results.append(
                FetchedJob(
                    source=self.source_name,
                    external_id=entry.get("id", entry.get("link", "")),
                    title=entry.get("title", ""),
                    company=entry.get("author", ""),
                    location=query.location,
                    description=description,
                    apply_url=entry.get("link", ""),
                    post_date=post_date,
                )
            )
        return results

    def _build_rss_url(self, query: JobQuery) -> str:
        title = quote_plus(query.title)
        location = quote_plus(query.location)
        return f"https://rss.indeed.com/rss?q={title}&l={location}"

    def _parse_date(self, value) -> dt.datetime | None:
        if not value:
            return None
        try:
            if isinstance(value, tuple):
                return dt.datetime.fromtimestamp(dt.datetime(*value[0:6]).timestamp(), tz=dt.timezone.utc)
            parsed = parsedate_to_datetime(str(value))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=dt.timezone.utc)
            return parsed
        except Exception:  # pragma: no cover - feedparser edge cases
            return None


__all__ = ["IndeedJobSource"]
