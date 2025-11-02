"""Dashboard UI routes."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


def register_ui(app: FastAPI) -> None:
    templates = Jinja2Templates(directory="app/ui/templates")
    app.mount("/static", StaticFiles(directory="app/ui/static"), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request) -> HTMLResponse:
        settings = request.app.state.settings
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "refresh_seconds": settings.dashboard_refresh_seconds},
        )


__all__ = ["register_ui"]
