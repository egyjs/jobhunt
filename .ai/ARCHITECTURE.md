# Architecture Overview

The MVP now ships a full-stack JobApply agent: a FastAPI backend orchestrating job
scraping, ranking, and application preparation, plus a Next.js dashboard for human-in-
the-loop review.

---

## System Components

- **FastAPI app (`app/api/main.py`)** — Exposes `/jobs/fetch`, `/jobs/match`, and
  `/jobs/apply` endpoints and boots the APScheduler background fetcher.
- **Configuration (`app/config.py`)** — Loads environment variables (see `mvp.env`) and
  ensures storage/log directories exist.
- **Persistence (`app/database.py`, `app/models.py`, `app/repositories.py`)** — SQLModel
  models for sources, postings, applications, and resume index text. Repositories handle
  dedupe and CRUD flows.
- **Job discovery services (`app/services/job_discovery.py` + fetchers)** — Async
  fetchers for LinkedIn, Indeed, Glassdoor, and company feeds using `httpx` + `bs4`.
- **Matching engine (`app/services/matcher.py`)** — Generates TF-IDF vectors from the
  candidate corpus (resume PDF + profile JSON) and scores postings.
- **Application workflow (`app/services/application.py`)** — Produces tailored resume
  highlights/cover letters (OpenAI-backed when available) and stores results.
- **Scheduler (`app/services/scheduler.py`)** — APScheduler interval job that refreshes
  listings using configured search terms.
- **Dashboard (`dashboard/`)** — Next.js 14 app using SWR to show ranked jobs and
  trigger application packages.

---

## Data Flow

```text
User hits REST endpoint or scheduler triggers fetch
        ↓
Discovery service gathers postings from each fetcher (LinkedIn/Indeed/Glassdoor/feeds)
        ↓
SQLModel repository deduplicates and persists job postings
        ↓
Matcher computes similarity scores vs. resume/profile corpus
        ↓
Application service generates resume + cover letter files and logs status
        ↓
Dashboard/API consumers read from the database and storage directories
```

---

## Key Decisions

### FastAPI + SQLModel backend
- **Rationale:** We needed persistent state, background scheduling, and a clean REST API
  for future automations.
- **Trade-offs:** Increased complexity vs. the original single-script approach; requires
  dependency management for HTTP scraping and ML libraries.

### TF-IDF matcher with OpenAI fallback
- **Rationale:** Provides deterministic, offline-friendly scoring while still allowing
  richer AI tailoring when an OpenAI key exists.
- **Trade-offs:** TF-IDF may miss nuanced semantic matches; future work can swap in
  embeddings or vector databases.

### Next.js dashboard
- **Rationale:** Gives stakeholders a simple UI to browse matches and manually trigger
  applications, enabling a human-in-the-loop workflow for early releases.
- **Trade-offs:** Requires Node.js toolchain; remains minimal (SWR + client components).

---

## Module Structure

```text
app/
  api/main.py             # FastAPI app & scheduler startup
  api/routes/jobs.py      # REST endpoints for job fetch/match/apply
  config.py               # Pydantic settings + env parsing
  database.py             # SQLModel engine + session helpers
  logging_config.py       # Console/file log configuration
  models.py               # SQLModel ORM tables
  repositories.py         # Persistence helpers and dedupe logic
  schemas.py              # Pydantic request/response models
  services/
    application.py        # Tailored resume/cover-letter workflow
    generation.py         # OpenAI-backed text generation helpers
    job_discovery.py      # Aggregates fetchers and persists postings
    matcher.py            # TF-IDF matching against profile corpus
    scheduler.py          # APScheduler interval job
    fetchers/             # Source-specific scraping modules
  utils/
    profile.py            # Load/flatten profile JSON
    resume.py             # Extract text from PDF resume
main.py                   # Uvicorn entry point
```

---

## 🔧 For AI Agents

1. Update this document when adding new services (e.g., automated form submission).
2. Log new job sources or data stores so future maintainers can trace dependencies.
3. Record significant prompt/template updates in the relevant service module and
   mention them in commit messages/PR descriptions.

**Last Updated:** 2025-02-15
