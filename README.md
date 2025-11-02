# JobApply AI Agent MVP

Autonomous agent that discovers, ranks, and prepares job applications across LinkedIn, Indeed, Glassdoor, and company career feeds. The MVP exposes a FastAPI backend with a lightweight dashboard for manual review or one-click application prep.

## Features
- 🔍 **Job Discovery:** pluggable scrapers for LinkedIn, Indeed RSS, Glassdoor, and custom company feeds with deduplication + keyword tagging.
- 🧠 **Matching Engine:** sentence-transformer embeddings to rank postings against your resume + LinkedIn profile.
- ✍️ **AI Tailoring:** OpenAI-powered resume bullet rewrites, cover letters, and job summaries with deterministic fallbacks.
- 📦 **Application Kit:** generates per-job resume & cover letter files and tracks submission status in SQLite.
- 📊 **Dashboard:** filterable UI to trigger fetch, review matches, and launch tailored applications.
- ⏰ **Scheduler:** APScheduler job that refreshes listings on an interval.

## Getting Started

### 1. Install dependencies
```bash
./setup.sh
```

### 2. Configure environment
Copy the sample configuration and update it with your secrets + preferences:
```bash
cp mvp.env .env
```
Key settings:
- `OPENAI_API_KEY` – optional; enables AI tailoring (fallback templates used if absent).
- `JOB_TITLES`, `JOB_LOCATIONS`, `JOB_TYPES` – search permutations.
- `COMPANY_FEEDS` – RSS/Atom feeds for company career pages.
- `PROFILE_JSON_PATH`, `RESUME_PDF_PATH` – candidate profile sources.

Place your resume PDF and profile JSON at the configured paths (defaults under `data/`).

### 3. Launch the API & dashboard
```bash
python main.py serve --host 0.0.0.0 --port 8000
```
Open [http://localhost:8000](http://localhost:8000) to access the dashboard.

### 4. CLI utilities
```bash
# Fetch jobs once and log match scores
python main.py fetch --limit 50

# Display ranked matches in the console
python main.py match --limit 25
```

## REST API
- `POST /api/jobs/fetch` → trigger discovery; returns counts per source.
- `GET /api/jobs/match` → list ranked jobs (`limit` query param supported).
- `POST /api/jobs/apply` → generate tailored resume + cover letter for the given `job_id`.

## Data Storage
- SQLite database at `data/jobapply.db` (configurable via `DATABASE_URL`).
- Generated artifacts saved to `data/applications/` with timestamped filenames.

## Development Notes
- The first run downloads the `sentence-transformers/all-MiniLM-L6-v2` model.
- Scraping endpoints rely on public pages; selectors may need adjustment if upstream markup shifts.
- When OpenAI credentials are missing, fallback templates ensure the workflow still produces artifacts.

## License
MIT
