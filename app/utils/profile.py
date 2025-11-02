from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_profile(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Profile JSON not found at {path}")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def flatten_profile(profile: Dict[str, Any]) -> str:
    parts: list[str] = []
    for key, value in profile.items():
        if isinstance(value, dict):
            parts.append(flatten_profile(value))
        elif isinstance(value, list):
            parts.append("\n".join(str(item) for item in value))
        else:
            parts.append(str(value))
    return "\n".join(part for part in parts if part)


__all__ = ["load_profile", "flatten_profile"]
