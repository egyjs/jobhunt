"""Utility helpers for text normalization."""

from __future__ import annotations

import re
from typing import Iterable

WHITESPACE_PATTERN = re.compile(r"\s+")


def clean_whitespace(value: str) -> str:
    """Collapse repeated whitespace and strip leading/trailing spaces."""
    return WHITESPACE_PATTERN.sub(" ", value or "").strip()


def extract_keywords(text: str, keywords: Iterable[str]) -> set[str]:
    """Return any keywords that appear in the provided text."""
    text_lower = text.lower()
    return {keyword for keyword in keywords if keyword.lower() in text_lower}


__all__ = ["clean_whitespace", "extract_keywords"]
