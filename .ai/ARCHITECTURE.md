# Architecture Overview

The JobApply AI agent now runs as a FastAPI service with supporting worker utilities, consolidating job discovery, matching, and application prep.

---

## System Components

- **FastAPI entry (`app/main.py`):** exposes REST endpoints and serves the dashboard UI.
- **CLI (`main.py`):** wraps server start, one-off fetches, and match inspection.
- **Configuration (`app/config.py`):** loads environment settings from `.env`/`mvp.env` and normalizes search parameters.
- **Database (`app/database.py`, `app/models.py`):** SQLite via SQLAlchemy storing jobs, tags, and application records.
- **Service registry (`app/services/registry.py`):** wires shared services (job sources, embeddings, AI, tagging, profile loader).
- **Job sources (`app/services/job_sources/`):** async scrapers for Indeed RSS, LinkedIn guest API, Glassdoor search, and configurable company feeds.
- **Job fetcher (`app/services/job_fetcher.py`):** orchestrates provider calls, deduplicates postings, generates summaries, embeddings, and tags before persisting.
- **Matching engine (`app/services/matching.py`):** encodes resume/profile text, ranks jobs via cosine similarity + recency bonus.
- **Application workflow (`app/services/application_service.py`):** generates tailored resume/cover-letter artifacts and records application status.
- **AI helpers (`app/services/ai.py`):** OpenAI Responses API wrapper with fallback templates.
- **Profile loader (`app/services/profile.py`):** reads resume PDF + JSON profile for downstream services.
- **Scheduler (`app/scheduler.py`):** APScheduler job to periodically refresh listings.
- **Dashboard UI (`app/ui/*`):** Jinja template + vanilla JS for monitoring and manual actions.

---

## Data Flow

```text
python main.py serve → uvicorn loads app/main.py → FastAPI startup → ServiceRegistry + scheduler
POST /api/jobs/fetch → JobFetcher gathers providers → embeddings + summaries → SQLAlchemy persistence
GET /api/jobs/match → MatchingService ranks stored jobs → returns JSON for dashboard
POST /api/jobs/apply → ApplicationService tailors resume/cover letter → files saved in data/applications
```

---

## Key Decisions

### FastAPI Service
**Why:** Need REST + dashboard endpoints while keeping automation auditable.  
**Trade-offs:** Requires managing async fetchers and scheduler lifecycles explicitly.

### Sentence-Transformer Embeddings
**Why:** Local embeddings avoid per-call LLM cost for matching.  
**Trade-offs:** Larger dependencies and cold-start download time.

### OpenAI for Tailoring
**Why:** Produces high-quality customized materials.  
**Fallback:** Deterministic templates when API key absent ensure workflow continuity.

### Pluggable Job Sources
**Why:** Each board has bespoke HTML/feeds; modular providers simplify future adjustments.  
**Trade-offs:** HTML selectors may break with upstream changes; logging + graceful failure mitigate outages.

---

## Module Structure

```text
.
├── main.py                 # CLI entry
├── app/
│   ├── __init__.py         # create_app + scheduler wiring
│   ├── main.py             # FastAPI app instance
│   ├── api/routes.py       # REST endpoints
│   ├── config.py           # settings loader
│   ├── database.py         # SQLAlchemy engine/session helpers
│   ├── models.py           # ORM models
│   ├── schemas.py          # Pydantic response/request models
│   ├── services/
│   │   ├── registry.py     # service container
│   │   ├── ai.py           # OpenAI helpers
│   │   ├── embeddings.py   # sentence-transformer wrapper
│   │   ├── job_fetcher.py  # job ingestion orchestration
│   │   ├── matching.py     # similarity ranking
│   │   ├── application_service.py
│   │   ├── profile.py
│   │   ├── tagging.py
│   │   └── job_sources/
│   │       ├── base.py
│   │       ├── indeed.py
│   │       ├── linkedin.py
│   │       ├── glassdoor.py
│   │       └── company.py
│   ├── scheduler.py
│   ├── ui/
│   │   ├── router.py
│   │   ├── templates/dashboard.html
│   │   └── static/{dashboard.js,styles.css}
│   └── utils/text.py
├── data/                   # profile.json, applications/, resume placeholder
├── mvp.env                 # sample environment config
└── setup.sh                # install helper
```

---

## 🔧 Notes for AI Agents

1. Update job source modules or tagging vocab when adjusting discovery targets.
2. Keep OpenAI prompt changes documented in commit messages and feature specs.
3. When adding new persistence tables, update `models.py`, migrations (if introduced), and document them here.
4. Dashboard assets live under `app/ui`; coordinate JS & API contract changes.

**Last Updated:** 2025-02-16
