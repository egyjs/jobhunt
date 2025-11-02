"""Repository helpers for application workflow."""

from __future__ import annotations

from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Application


class ApplicationRepository:
    """Persist application state and artifacts."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, payload: dict) -> Application:
        application = Application(**payload)
        self.session.add(application)
        return application

    def list_by_status(self, statuses: Iterable[str]) -> list[Application]:
        stmt = select(Application).where(Application.status.in_(tuple(statuses)))
        return list(self.session.execute(stmt).scalars().all())

    def get(self, application_id: int) -> Application | None:
        return self.session.get(Application, application_id)


__all__ = ["ApplicationRepository"]
