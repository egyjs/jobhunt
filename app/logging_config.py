from __future__ import annotations

import logging
from logging.config import dictConfig


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "encoding": "utf-8",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}


def configure_logging() -> None:
    from .config import get_settings

    settings = get_settings()
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    LOGGING_CONFIG["handlers"]["file"]["filename"] = str(settings.logs_dir / "applications.log")
    dictConfig(LOGGING_CONFIG)


__all__ = ["configure_logging"]
