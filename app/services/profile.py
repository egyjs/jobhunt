"""Utilities for loading and persisting the user's profile and resume."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from pypdf import PdfReader
from sqlmodel import select

from app.config import get_settings
from app.database import session_scope
from app.models import UserProfile


def extract_pdf_text(path: Path) -> str:
    """Extract raw text from a PDF file."""

    if not path.exists():
        return ""
    try:
        reader = PdfReader(path)
    except Exception:  # pragma: no cover - depends on external file contents
        return ""
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def load_profile_from_json(path: Path) -> Optional[UserProfile]:
    """Load profile data from JSON and merge into persistence."""

    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    settings = get_settings()
    resume_text = extract_pdf_text(settings.resume_pdf_path)

    with session_scope() as session:
        existing = session.exec(select(UserProfile)).first()
        if existing:
            existing.full_name = payload.get("full_name", existing.full_name)
            existing.headline = payload.get("headline", existing.headline)
            existing.summary = payload.get("summary", existing.summary)
            existing.experience = payload.get("experience", existing.experience)
            existing.skills = payload.get("skills", existing.skills)
            existing.resume_text = resume_text or existing.resume_text
            existing.updated_at = datetime.utcnow()
            profile = existing
        else:
            profile = UserProfile(
                full_name=payload.get("full_name", ""),
                headline=payload.get("headline"),
                summary=payload.get("summary"),
                experience=payload.get("experience"),
                skills=payload.get("skills", []),
                resume_text=resume_text,
            )
            session.add(profile)
    return profile


__all__ = ["extract_pdf_text", "load_profile_from_json"]

