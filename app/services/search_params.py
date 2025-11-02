from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DiscoveryParams:
    terms: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    job_types: List[str] = field(default_factory=list)
    remote_only: Optional[bool] = None
    salary_min: Optional[int] = None


__all__ = ["DiscoveryParams"]
