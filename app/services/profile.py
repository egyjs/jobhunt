"""Load and normalize candidate profile information."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PyPDF2 import PdfReader

from ..config import Settings
from ..utils.text import clean_whitespace


@dataclass(slots=True)
class UserProfile:
    """Represents the candidate's resume and LinkedIn profile data."""

    resume_text: str
    profile_json: dict

    @property
    def combined_text(self) -> str:
        profile_sections = "\n".join(
            clean_whitespace(str(value)) for value in self.profile_json.values() if isinstance(value, (str, list, dict))
        )
        return clean_whitespace(self.resume_text + "\n" + profile_sections)

    @property
    def summary(self) -> str:
        summary = self.profile_json.get("summary")
        if isinstance(summary, str) and summary.strip():
            return clean_whitespace(summary)
        return self.resume_text.splitlines()[0] if self.resume_text else "Experienced professional"


class ProfileLoader:
    """Load resume and profile data from disk."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def load(self) -> UserProfile:
        resume_text = self._read_pdf(Path(self.settings.resume_pdf_path))
        profile_json = self._read_json(Path(self.settings.profile_json_path))
        return UserProfile(resume_text=resume_text, profile_json=profile_json)

    def _read_pdf(self, path: Path) -> str:
        if not path.exists():
            return ""
        reader = PdfReader(str(path))
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        return clean_whitespace("\n".join(texts))

    def _read_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        return json.loads(path.read_text())


__all__ = ["ProfileLoader", "UserProfile"]
