# Feature Spec: Autonomous JobApply MVP

## Overview
Build a minimum viable product that continuously sources, ranks, and applies to job postings on the user's behalf across LinkedIn, Indeed, Glassdoor, and selected company career pages. The MVP must expose a REST API, maintain persistent storage, and prepare tailored application materials.

## Goals
- Aggregate at least four job sources with deduplication and tagging.
- Persist jobs, resumes, and application status in a relational database.
- Provide REST endpoints for fetching, matching, and applying to jobs.
- Generate AI-personalized resumes, cover letters, and job summaries per application.
- Deliver a lightweight dashboard for manual review and triggering applications.

## Non-Goals
- Full production-grade scraping resilience.
- Complete automation of all third-party application flows (fallback to manual review acceptable).
- Multi-user tenancy beyond a single profile.

## Solution Outline
1. **Backend service (FastAPI):**
   - `/jobs/fetch`: trigger job discovery workflow.
   - `/jobs/match`: return ranked jobs by resume similarity.
   - `/jobs/apply`: initiate automatic or manual application preparation.
   - Serve a simple dashboard UI and static assets.
2. **Job sources abstraction:** asynchronous providers for LinkedIn, Indeed RSS, Glassdoor search pages, and configurable company career RSS feeds.
3. **Persistence:** SQLite database via SQLAlchemy models for jobs, tags, and applications.
4. **Matching engine:** Sentence-transformers embeddings with cosine similarity against resume text + LinkedIn JSON profile.
5. **AI helpers:** OpenAI-powered resume tailoring, cover letter drafting, and short job summaries with template fallbacks when no API key is present.
6. **Scheduler:** APScheduler background job to refresh listings daily.
7. **Artifacts:** store generated resumes and cover letters inside `data/applications/` with metadata logged.

## Acceptance Criteria
- Running `python main.py` launches the API server, scheduler, and logs.
- `/jobs/fetch` stores new listings and returns a summary count by source.
- `/jobs/match` returns JSON sorted by score with job details, tags, and summary text.
- `/jobs/apply` creates a tailored resume + cover letter files and records the application status.
- Dashboard page lists jobs with filters (source, tags, status) and buttons to fetch/match/apply.
- Documentation updated: README, ARCHITECTURE, CONVENTIONS (if needed), sample env `mvp.env`.

## Work Items
1. Define SQLAlchemy models, repositories, and database initialization utilities.
2. Implement job source providers (LinkedIn, Indeed RSS, Glassdoor, company feeds) with deduplication logic.
3. Build services for job fetching, matching, and application prep.
4. Create AI helper module for resume tailoring, cover letters, and summaries.
5. Expose FastAPI routes and static dashboard assets.
6. Add scheduler wiring and CLI entrypoints in `main.py`.
7. Update documentation, requirements, setup script, and provide sample environment file.

## Risks & Mitigations
- **Scraping instability:** Provide graceful fallbacks and logging when providers fail.
- **LLM dependence:** Include deterministic fallback templates when API key missing.
- **Performance:** Cache embeddings for stored jobs to avoid recomputation.

**Last Updated:** 2025-02-16
