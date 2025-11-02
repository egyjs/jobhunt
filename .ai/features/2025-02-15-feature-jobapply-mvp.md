# Feature Spec — JobApply MVP

**Date:** 2025-02-15
**Owner:** JobApply AI Agent
**Related Ticket:** TICKET-001

---

## Problem Statement

The current repository only runs a `browser-use` prompt that scrapes five roles from
Indeed and saves them to CSV. We need a production-ready MVP that can autonomously
discover roles across major boards, score them against the candidate profile, and
generate application materials that can be submitted automatically or reviewed
manually.

## Goals & Non-Goals

### Goals
- Support multi-source job discovery (LinkedIn, Indeed, Glassdoor, configurable
  company feeds) with deduplication.
- Persist structured job data, application state, and AI-generated assets in a
  database-backed backend.
- Provide REST endpoints for fetching, matching, and applying so other clients
  (CLI, dashboard, automations) can integrate.
- Implement an AI-assisted matching engine using resume/profile data.
- Generate tailored resumes and cover letters per job and store them alongside
  application records.
- Ship a simple Next.js dashboard for browsing jobs and initiating applications.
- Supply sample configuration via `mvp.env` and document the new architecture.

### Non-Goals
- Full browser automation for site-specific forms (beyond scoped hooks in the
  application workflow).
- Complex multi-tenant account management.
- Guaranteeing delivery to proprietary APIs that require authentication tokens
  (the MVP will focus on publicly accessible listings or configurable feeds).

## Proposed Solution

1. **Backend Foundation**
   - Introduce a FastAPI application (`jobhunt/app/main.py`) with routers for job
     fetching, matching, and applying.
   - Use SQLModel + SQLite for persistence (`jobhunt/app/models.py`), storing job
     postings, sources, and application records.
   - Configure settings via `pydantic-settings` with defaults drawn from `mvp.env`.

2. **Job Discovery Layer**
   - Create async fetcher classes per source under `jobhunt/app/services/fetchers/`.
   - Aggregate results through a `JobDiscoveryService` that normalizes fields and
     deduplicates by `(source, external_id)`.
   - Support fallback parsing for company pages driven by config-supplied RSS or
     sitemap URLs.

3. **Matching Engine**
   - Parse the candidate resume PDF (via `pypdf`) and profile JSON to produce a
     consolidated skill/profile corpus.
   - Implement TF-IDF cosine similarity to rank job descriptions. Optionally use
     OpenAI embeddings when an API key is supplied.

4. **Application Workflow**
   - Generate tailored resume bullet highlights and cover letters using OpenAI GPT
     (with deterministic fallback templates when no key is configured).
   - Persist generated documents under `storage/applications/<job_id>/` and update
     `Application` records with status (`pending`, `applied`, etc.).
   - Log each attempt to `logs/applications.log`.

5. **Scheduler & Automation**
   - Use APScheduler to run periodic fetch tasks according to config-driven search
     terms.
   - Provide manual trigger endpoints for immediate fetch/application requests.

6. **Dashboard UI**
   - Scaffold a Next.js 14+ app under `/dashboard` that consumes the REST API,
     offering filters, job detail modals, and an "Apply" button that posts to
     `/jobs/apply`.

7. **Documentation & Tooling**
   - Update README with setup/run instructions for backend and dashboard.
   - Add `mvp.env` describing required environment variables.
   - Refresh `ARCHITECTURE.md` to reflect the new multi-module layout and backend.

## Risks & Mitigations
- **HTML instability:** keep scraper selectors resilient and log failures; allow
  manual seed JSON ingestion to unblock development.
- **Rate limits/blocks:** randomize User-Agent headers and stagger requests; allow
  config to reduce frequency.
- **AI dependency:** fallback to deterministic templates when OpenAI keys are
  unavailable.
- **PDF parsing accuracy:** support manual overrides by storing the parsed resume
  text for review in storage.

## Testing Strategy
- Unit-test critical services (fetchers, matcher, application workflow) with
  mocked HTTP responses and sample HTML fixtures.
- Smoke-test the FastAPI endpoints via `pytest` or `httpx.AsyncClient` test client.
- Manual end-to-end verification: run scheduler, open dashboard, trigger fetch,
  inspect database rows, and review generated application package.

## Open Questions
- Which automated submission targets should be prioritized post-MVP?
- Should we support multiple candidate profiles in v1 or wait for follow-up work?

