"""Database configuration and session utilities."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import get_settings

Base = declarative_base()


def _create_engine():
    settings = get_settings()
    connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    return create_engine(settings.database_url, future=True, connect_args=connect_args)


ENGINE = _create_engine()
SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, expire_on_commit=False, future=True)


def init_db() -> None:
    """Create database tables if they do not exist."""
    from . import models  # noqa: F401  # ensure metadata import

    Base.metadata.create_all(bind=ENGINE)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:  # pragma: no cover - ensures rollback on failure
        session.rollback()
        raise
    finally:
        session.close()


__all__ = ["Base", "SessionLocal", "session_scope", "init_db"]
