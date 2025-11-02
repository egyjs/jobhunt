"""Database configuration and utilities."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings


settings = get_settings()
engine = create_engine(settings.database_url, echo=False)


def init_db() -> None:
    """Create database tables if they do not exist."""

    SQLModel.metadata.create_all(engine)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a transactional scope for database operations."""

    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:  # pragma: no cover - best effort rollback
        session.rollback()
        raise
    finally:
        session.close()


__all__ = ["engine", "init_db", "session_scope"]

