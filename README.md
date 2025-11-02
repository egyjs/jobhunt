# JobApply AI MVP

Autonomous job application agent that discovers roles across LinkedIn, Indeed, Glassdoor,
and company career feeds, ranks them against the candidate profile, and prepares
AI-tailored application packages (resume + cover letter). A FastAPI backend powers
REST endpoints and a lightweight Next.js dashboard for manual review and automation.

## Features

- 🔍 **Job discovery** across LinkedIn, Indeed, Glassdoor, and configurable company feeds.
- 🗃️ **SQLite persistence** for job postings, sources, and application history via SQLModel.
- 🤝 **Matching engine** using TF-IDF similarity between job descriptions and the
  candidate's resume/profile.
- 📝 **AI-tailored resume highlights & cover letters** leveraging OpenAI (with
  deterministic fallbacks when no API key is configured).
- 🤖 **Application workflow** that stores generated materials and tracks status.
- 📆 **APScheduler** background job to refresh listings on a configurable cadence.
- 🖥️ **Next.js dashboard** to browse matches and trigger application packages.

## Project Structure

```
.
├── app/
│   ├── api/                # FastAPI routes and app wiring
│   ├── config.py           # Pydantic settings + env loading
│   ├── database.py         # SQLModel engine/session helpers
│   ├── logging_config.py   # Console + file logging setup
│   ├── models.py           # SQLModel ORM models
│   ├── repositories.py     # Persistence helpers
│   ├── schemas.py          # Pydantic response/request schemas
│   ├── services/           # Discovery, matching, application services
│   └── utils/              # Resume/profile parsing utilities
├── dashboard/              # Next.js 14 dashboard
├── profiles/               # Sample profile JSON + resume PDF
├── storage/                # Generated application artifacts
├── logs/                   # Application logs
├── mvp.env                 # Example environment configuration
└── main.py                 # Uvicorn entry point for the API
```

## Prerequisites

- Python 3.11+
- Node.js 18+ (for the dashboard)
- Optional: OpenAI API key for high-quality tailoring

## Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Copy environment template and customize values
cp mvp.env .env
# edit .env to set OPENAI_API_KEY and job search parameters

# 3. Initialize the database & run the API (creates tables on startup)
python main.py
```

The API starts on `http://0.0.0.0:8000` by default. APScheduler automatically kicks off
background fetches using the search terms from settings. Trigger manual fetches via the
`/jobs/fetch` endpoint if you want immediate results.

## REST API

| Endpoint        | Method | Description |
| --------------- | ------ | ----------- |
| `/jobs/fetch`   | POST   | Fetch new jobs across all sources and persist them |
| `/jobs/match`   | GET    | Return ranked job matches for the candidate |
| `/jobs/apply`   | POST   | Generate a tailored resume + cover letter for a job |

Use tools like `curl`, `httpie`, or the dashboard to interact with the endpoints.

## Dashboard

```bash
cd dashboard
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_BASE` in a `.env.local` file (defaults to `http://localhost:8000`).
The dashboard lists the best matches, highlights the similarity score, and allows
one-click generation of application packages for manual review.

## Logs & Output

- Generated resumes and cover letters: `storage/applications/<job_id>/`
- Application log stream: `logs/applications.log`
- SQLite database: `jobhunt.db` (configurable via `DATABASE_URL`)

## Testing & Validation

- Run `python main.py` and observe the scheduler log output.
- Manually trigger a fetch:
  ```bash
  curl -X POST http://localhost:8000/jobs/fetch -H "Content-Type: application/json" \
       -d '{"terms": ["Laravel Developer"], "locations": ["Remote"], "limit": 25}'
  ```
- Inspect matches:
  ```bash
  curl http://localhost:8000/jobs/match
  ```
- Prepare an application:
  ```bash
  curl -X POST http://localhost:8000/jobs/apply -H "Content-Type: application/json" \
       -d '{"job_id": 1, "auto_submit": false}'
  ```

## Security Notes

- Never commit real credentials—use `.env` (gitignored) for secrets.
- Review third-party site terms before running large-scale scraping jobs.
- Update the OpenAI prompt templates responsibly; generated documents are stored locally.

## Roadmap

- Automate browser submissions via Playwright/Puppeteer for supported forms.
- Add email/Telegram notifications for status changes.
- Extend matching with vector databases and multi-profile support.
