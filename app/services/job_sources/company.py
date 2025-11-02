"""Company career page ingestion via RSS or Atom feeds."""

from __future__ import annotations

import datetime as dt
from typing import Iterable

import feedparser
import httpx

from ...config import Settings
from ...utils.text import clean_whitespace
from .base import FetchedJob, JobQuery, JobSource


class CompanyFeedJobSource(JobSource):
    source_name = "company"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def fetch(self, query: JobQuery, limit: int | None = None) -> Iterable[FetchedJob]:
        max_results = limit or self.settings.company_max_entries
        aggregated: list[FetchedJob] = []
        for feed_url in self.settings.company_feeds:
            try:
                async with httpx.AsyncClient(timeout=self.settings.job_board_timeout) as client:
                    response = await client.get(feed_url)
                    response.raise_for_status()
            except Exception:
                continue
            feed = feedparser.parse(response.text)
            for entry in feed.entries[:max_results]:
                title = entry.get("title", "")
                summary = clean_whitespace(entry.get("summary", ""))
                link = entry.get("link", "")
                published = entry.get("published_parsed")
                post_date = None
                if published:
                    post_date = dt.datetime.fromtimestamp(dt.datetime(*published[0:6]).timestamp(), tz=dt.timezone.utc)
                aggregated.append(
                    FetchedJob(
                        source=self.source_name,
                        external_id=f"{feed_url}-{entry.get('id', link)}",
                        title=title,
                        company=entry.get("author", ""),
                        location=query.location,
                        description=summary,
                        apply_url=link,
                        post_date=post_date,
                    )
                )
        return aggregated[:max_results]


__all__ = ["CompanyFeedJobSource"]
