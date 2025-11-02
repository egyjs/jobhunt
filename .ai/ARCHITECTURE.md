# Architecture Overview

Autonomous job-application MVP composed of a FastAPI backend, scheduled job fetch
workflows, and AI-assisted document generators. The original single-file
`browser-use` script has been refactored into modular services to support
multi-source discovery, ranking, and application preparation.

---

## System Components

- **FastAPI application (`app/api/main.py`):** Exposes REST endpoints for fetching
  jobs, computing matches, and preparing applications. Registers background
  scheduler hooks during startup/shutdown.
- **Scheduler (`app/scheduler.py`):** Periodically runs the fetch workflow based
  on the configured interval to keep the job database fresh.
- **Job source adapters (`app/services/job_sources/`):** Provide interchangeable
  fetchers per platform. The MVP includes static JSON-backed providers, ready to
  be swapped with live scrapers or APIs.
- **Persistence layer (`app/database.py`, `app/models.py`):** SQLModel-based
  ORM storing job postings, applications, and the user profile in SQLite.
- **Matching & application services (`app/services/*.py`):** Handle TF-IDF
  similarity scoring, resume/cover-letter tailoring, and summary generation.
- **Workflows (`app/workflows/`):** High-level orchestration modules invoked by
  API routes or the scheduler.
- **Configuration (`app/config.py`):** Loads environment-driven settings,
  ensuring output directories exist and centralizing search parameters.

---

## Data Flow

```text
Developer invokes `python main.py`
        ↓
Environment variables load via `dotenv`
        ↓
FastAPI app boots and scheduler starts in the background
        ↓
`/jobs/fetch` orchestrates all job source adapters (dedupe + persist)
        ↓
`/jobs/match` scores jobs against stored profile/resume
        ↓
`/jobs/apply` generates tailored artifacts and updates application status
        ↓
Artifacts and logs written to `output/`, state persisted in SQLite
```

---

## Key Decisions

### Why FastAPI + SQLModel?
**Problem:** The project needs an auditable API layer, persistence, and a clear
extension path for automation beyond a single script.
**Solution:** FastAPI offers lightweight REST routing while SQLModel keeps the
ORM succinct. Both integrate cleanly with async workflows and are easy to test.
**Trade-off:** Requires more project structure and dependencies compared to the
original single-file script, but gains scalability and observability.

### Why static JSON fetchers for the MVP?
**Problem:** Demonstrate architecture without committing to brittle scraping in
this iteration.
**Solution:** Ship with deterministic JSON-backed fetchers that exercise the
storage/matching/application pipelines. Real scrapers can implement the same
protocols later.
**Trade-off:** Out-of-the-box setup uses mock data; live integrations remain a
follow-up task.

---

## Module Structure

```text
.
├── main.py                 # CLI entry booting FastAPI + scheduler
├── app/
│   ├── api/                # FastAPI app factory and routes
│   ├── services/           # Domain services (matching, tailoring, fetchers)
│   ├── workflows/          # Orchestrated workflows used by routes/scheduler
│   ├── scheduler.py        # Background fetch scheduler
│   ├── config.py           # Pydantic settings management
│   ├── database.py         # SQLModel engine/session helpers
│   └── models.py           # ORM models for jobs/applications/profile
├── data/                   # Sample jobs and user profile JSON
├── output/                 # Generated resumes, cover letters, logs
└── .ai/                    # Project documentation for humans and AI assistants
```

---

## 🔧 For AI Agents

1. Update this file when adding new job source adapters or automation
   capabilities (e.g., live scraping, auto-form submission).
2. Document new background tasks, queues, or external integrations so future
   contributors can reason about side effects easily.
3. Maintain the workflow diagrams to reflect how API endpoints orchestrate
   services.

**Last Updated:** 2025-02-15
