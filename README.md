# JobApply AI Agent MVP

Autonomous job application agent that discovers, ranks, and prepares tailored applications for Laravel-focused roles.

## Features

- Multi-source job discovery across LinkedIn, Indeed, Glassdoor, and company career pages (backed by interchangeable
  fetchers – static JSON data ships for the MVP).
- Persistence using SQLite/SQLModel with deduplication across sources.
- Matching engine leveraging TF-IDF similarity between the user's resume/profile and job descriptions.
- Resume and cover letter tailoring that generates per-job artifacts saved under `output/`.
- REST API endpoints (`/jobs/fetch`, `/jobs/match`, `/jobs/apply`) suitable for dashboard integration.
- Background scheduler that refreshes job listings at a configurable cadence.

## Quick Start

### Prerequisites

- Python 3.11+
- (Optional) OpenAI API key if you plan to swap the heuristics for LLM-powered tailoring

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Copy the MVP environment template and adjust values
cp mvp.env .env
```

Add your resume PDF to `data/resume.pdf` (or point `RESUME_PDF_PATH` to another location) and update
`data/user_profile.json` with your current experience/skills.

### Run the API server

```bash
python main.py
```

The FastAPI server starts on `http://localhost:8000` and boots a background scheduler that refreshes job postings on
the configured interval.

### REST Workflows

Use any HTTP client (curl, HTTPie, Postman) to interact with the API:

```bash
# Fetch and store job listings from all sources
curl -X POST http://localhost:8000/jobs/fetch

# Retrieve ranked matches (top 25 by default)
curl http://localhost:8000/jobs/match

# Prepare an application package for job id 1
curl -X POST http://localhost:8000/jobs/apply -H 'Content-Type: application/json' -d '{"job_id": 1, "auto_submit": false}'
```

Generated resumes and cover letters are written to `output/resumes/` and `output/cover_letters/` respectively. The
database `jobhunt.db` keeps a record of postings and application states.

## Configuration

Key environment variables (see `mvp.env` for a full list):

- `JOB_TITLES`, `LOCATIONS`, `JOB_TYPES` – comma-separated search parameters.
- `FETCH_LIMIT` – number of jobs per source per run.
- `COMPANY_CAREER_PAGES` – optional URLs for direct career-site monitoring.
- `SCHEDULER_INTERVAL_MINUTES` – background refresh interval.
- `RESUME_PDF_PATH`, `PROFILE_JSON_PATH` – customize where resume/profile data is loaded from.

## Roadmap

- Replace static JSON feeds with live scrapers or API integrations per job board.
- Integrate LLM-powered resume/cover-letter rewriting when API access is available.
- Add a lightweight dashboard (Next.js) that consumes the REST API for monitoring and manual review.
- Automate form submissions with Playwright/Puppeteer workflows for full end-to-end applications.

## Troubleshooting

- Ensure `jobhunt.db` is writable; remove the file if you need a clean slate.
- Missing resume text? Confirm the PDF path in `.env` or provide a plaintext fallback.
- When extending fetchers, update `.ai/ARCHITECTURE.md` and create specs under `.ai/features/` for new workflows.
