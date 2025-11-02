# Feature: Autonomous Job Application MVP

**Date:** 2025-02-17
**Status:** In Progress
**Priority:** High
**Related Ticket:** TICKET-001

---

## Overview

Deliver an automation workflow that continuously discovers roles across major job boards, ranks them against the
user profile, and prepares or submits tailored applications.

**User Story**
As an automation maintainer, I want the agent to orchestrate end-to-end job discovery, matching, and application
preparation so that the user can apply to high-fit opportunities with minimal manual effort.

---

## Behavior Specification

### Scenario 1: Fetch job postings from multiple sources

```gherkin
Given the environment is configured with role keywords and target locations
And the FastAPI server is running
When a client calls the `/jobs/fetch` endpoint
Then the workflow should query LinkedIn, Indeed, Glassdoor, and configured company career pages
And deduplicate the returned listings by company, title, and location
And persist the normalized results to the relational database with tagged skills
```

### Scenario 2: Rank postings against the user profile

```gherkin
Given the database contains job postings and a stored user profile with resume text
When a client calls the `/jobs/match` endpoint
Then the workflow should compute similarity scores between the profile and each job description
And return the highest-ranked opportunities along with human-readable summaries
```

### Scenario 3: Prepare an application package

```gherkin
Given a job posting with a high similarity score
When a client calls the `/jobs/apply` endpoint for that job
Then the workflow should generate a tailored resume variant and cover letter artifact
And mark the job as "Applied" with a log entry capturing the output file paths
And expose the updated application status through the API
```

### Scenario 4: Handle downstream automation gaps

```gherkin
Given a target job board lacks a supported automation path
When the workflow cannot submit the application automatically
Then it should mark the job as "Pending Manual Review"
And include the generated documents and application URL in the response payload
```

---

## Acceptance Criteria

- [ ] Agent instructions updated in `main.py` and supporting modules to expose FastAPI workflows.
- [ ] Database schema stores job postings, tags, and application status transitions.
- [ ] Fetch pipeline supports multiple source providers with deduplication.
- [ ] Matching engine computes similarity scores using embeddings or vectorization.
- [ ] Tailored resume and cover letter artifacts saved per job.
- [ ] REST endpoints documented and returning structured JSON.
- [ ] Manual run of `python main.py` verified.
- [ ] Architecture and README updated to describe the MVP.

---

## Test Strategy

- **Manual:** Trigger `/jobs/fetch`, `/jobs/match`, and `/jobs/apply` sequentially against the local server and inspect
  database contents plus generated artifacts in the `output/` directory.
- **Automated (future):** Add integration tests using `httpx.AsyncClient` to exercise FastAPI endpoints and mock source
  providers for deterministic responses.

---

## Technical Notes

- Dependencies: FastAPI, SQLModel, httpx, scikit-learn, python-dotenv, pypdf, uvicorn.
- Environment variables captured in `mvp.env` for search parameters and API keys.
- Follow-up: Implement real scraping/adapters for each job board and integrate with a headless browser automation
  runner for full submission automation.

---

## 🤖 For AI Agents

1. Keep this spec aligned with the evolving prompt instructions and automation coverage.
2. Record limitations or fallback behaviors (e.g., unsupported form fields) in the notes above as they arise.
3. Update status when the MVP ships and archive manual test logs under `output/logs/` if needed.

**Last Updated:** 2025-02-17

