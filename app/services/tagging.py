"""Tagging utilities for job postings."""

from __future__ import annotations

from typing import Iterable

from ..utils.text import extract_keywords

DEFAULT_KEYWORDS = {
    "python",
    "django",
    "flask",
    "fastapi",
    "php",
    "laravel",
    "node.js",
    "react",
    "vue",
    "aws",
    "azure",
    "gcp",
    "remote",
    "full-time",
    "contract",
    "rest",
    "graphql",
    "sql",
    "postgresql",
    "mysql",
    "docker",
    "kubernetes",
    "devops",
    "microservices",
}


class TagService:
    """Assign keyword tags to job postings."""

    def __init__(self, custom_keywords: Iterable[str] | None = None) -> None:
        self.keywords = set(DEFAULT_KEYWORDS)
        if custom_keywords:
            self.keywords.update({kw.lower() for kw in custom_keywords})

    def tags_for(self, text: str) -> set[str]:
        return extract_keywords(text, self.keywords)


__all__ = ["TagService"]
