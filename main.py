"""Command-line entry point for the JobApply AI agent."""

from __future__ import annotations

import argparse
import asyncio
import logging

import uvicorn

from app.config import get_settings
from app.services.registry import ServiceRegistry


logger = logging.getLogger("jobapply")


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def serve(host: str, port: int, reload: bool = False) -> None:
    configure_logging()
    uvicorn.run("app.main:app", host=host, port=port, reload=reload, factory=False)


def build_registry() -> ServiceRegistry:
    settings = get_settings()
    return ServiceRegistry(settings=settings)


async def run_fetch_once(registry: ServiceRegistry) -> None:
    configure_logging()
    counts = await registry.job_fetcher.fetch_all()
    logger.info("Manual fetch completed: %s", counts)


async def run_match(registry: ServiceRegistry, limit: int) -> None:
    configure_logging()
    results = await registry.matching.match(limit=limit)
    for result in results:
        logger.info("%.2f - %s at %s", result.score, result.job.title, result.job.company)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="JobApply AI Agent CLI")
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve", help="Start the API server")
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8000)
    serve_parser.add_argument("--reload", action="store_true")

    fetch_parser = subparsers.add_parser("fetch", help="Fetch jobs once")
    fetch_parser.add_argument("--limit", type=int, default=50, help="Maximum matches to display after fetch")

    match_parser = subparsers.add_parser("match", help="Show ranked jobs")
    match_parser.add_argument("--limit", type=int, default=25)

    parser.set_defaults(command="serve")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "serve":
        serve(args.host, args.port, args.reload)
        return

    registry = build_registry()
    if args.command == "fetch":
        asyncio.run(run_fetch_once(registry))
        asyncio.run(run_match(registry, args.limit))
        return
    if args.command == "match":
        asyncio.run(run_match(registry, args.limit))
        return


if __name__ == "__main__":
    main()
