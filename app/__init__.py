"""Application bootstrap for the JobApply MVP."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router as api_router
from .config import get_settings
from .database import init_db
from .scheduler import build_scheduler
from .services.registry import ServiceRegistry
from .ui.router import register_ui


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()
    init_db()

    services = ServiceRegistry(settings=settings)

    app = FastAPI(
        title="JobApply AI Agent",
        description="Autonomous agent that sources, matches, and applies to jobs.",
        version="0.1.0",
    )
    app.state.settings = settings
    app.state.services = services

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")
    register_ui(app)

    scheduler = build_scheduler(services.job_fetcher, settings)

    @app.on_event("startup")
    async def on_startup() -> None:  # pragma: no cover - FastAPI lifecycle
        if settings.scheduler_enabled:
            scheduler.start()

    @app.on_event("shutdown")
    async def on_shutdown() -> None:  # pragma: no cover - FastAPI lifecycle
        if scheduler.running:
            scheduler.shutdown()

    return app


__all__ = ["create_app"]
