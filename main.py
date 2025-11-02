from __future__ import annotations

import uvicorn

from app.config import get_settings
from app.logging_config import configure_logging


def run() -> None:
    configure_logging()
    settings = get_settings()
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run()
