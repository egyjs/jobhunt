from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from .config import get_settings


settings = get_settings()
engine = create_engine(settings.database_url, echo=False, future=True)


def init_db() -> None:
    """Create database tables if they do not exist."""

    SQLModel.metadata.create_all(engine)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""

    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session() -> Generator[Session, None, None]:
    with session_scope() as session:
        yield session


__all__ = ["engine", "init_db", "session_scope", "get_session"]
