"""Command-line entry point for running the JobApply AI Agent MVP."""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

import uvicorn
from dotenv import load_dotenv

from app.api.main import app as fastapi_app


load_dotenv()


async def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Start the FastAPI server with uvicorn."""

    config = uvicorn.Config(fastapi_app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_server())


if __name__ == "__main__":
    main()

