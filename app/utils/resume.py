from __future__ import annotations

import logging
from pathlib import Path

from pypdf import PdfReader

logger = logging.getLogger(__name__)


def extract_text_from_pdf(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Resume not found at {path}")
    reader = PdfReader(str(path))
    text_parts = []
    for page in reader.pages:
        try:
            text_parts.append(page.extract_text() or "")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to extract text from resume page: %s", exc)
    return "\n".join(part.strip() for part in text_parts if part)


__all__ = ["extract_text_from_pdf"]
