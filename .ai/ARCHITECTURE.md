# Architecture Overview

Automation agent that uses the `browser-use` toolkit to collect job listings.
The repository intentionally keeps the surface area small so the runtime
configuration stays easy to audit.

---

## System Components

- **Command-line entry (`main.py`):** Defines the natural-language task, configures
  the `browser_use.Agent`, and executes the asynchronous run loop.
- **Tools (`browser_use.Tools`):** Provides scraping, extraction, and file-writing
  actions that the agent can call while browsing.
- **Language model (`ChatOpenAI`):** Orchestrates reasoning over the browsing
  session. The model name can be overridden via environment variables.
- **Environment configuration:** `.env` file supplies credentials (e.g., OpenAI
  key) that `browser-use` and `ChatOpenAI` read at startup.

---

## Data Flow

```text
Developer invokes `python main.py`
        ↓
Environment variables load via `dotenv`
        ↓
`Agent` receives the multi-step job-scraping task prompt
        ↓
Agent drives a headless browser session using `browser-use` actions
        ↓
Extracted data is saved to `job_postings.csv` through the provided file tool
```

---

## Key Decisions

### Why `browser-use`?
**Problem:** Need reliable, scriptable browsing for job-search automation.
**Solution:** Adopted the `browser-use` toolkit because it exposes high-level
agent abstractions and built-in extract/write actions.
**Trade-off:** Requires alignment with the toolkit's async APIs and dependency
on the provider's browser automation reliability.

### Why a single-module layout?
**Problem:** Keep experimentation nimble while the workflow is evolving.
**Solution:** Place orchestration logic in `main.py` and rely on rich prompt
engineering rather than many helper modules.
**Trade-off:** Fewer seams for unit tests today; expand into packages when we
add persistent state or multiple tasks.

---

## Module Structure

```text
.
├── main.py              # Entry point configuring and running the agent
├── .ai/                 # Project documentation for humans and AI assistants
└── .github/             # GitHub-specific guidance
```

---

## 🔧 For AI Agents

1. Keep this file up to date when you split `main.py` into submodules or add
   persistent storage/output layers.
2. Note any new external integrations (APIs, message queues, etc.) here so
   future contributors can trace dependencies quickly.
3. Record the reasoning behind prompt or tool changes that materially affect
   how the agent navigates.

**Last Updated:** 2025-02-15
