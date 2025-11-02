# Coding Conventions & Patterns

Repository-wide norms for evolving the job-hunting automation script.
Keep this lean and update it when practices change.

---

## Code Style

- **Formatting:** Follow PEP 8. Run `ruff format` and `ruff check` if the tool is
  installed; otherwise keep lines under 100 characters and imports grouped as
  stdlib → third-party → local.
- **Async:** Keep FastAPI endpoints and schedulers non-blocking. Avoid long-running
  synchronous operations inside the event loop; offload heavy work to background
  tasks if needed.
- **Configuration:** Load environment variables through `dotenv` early and prefer
  `os.environ.get` with sensible defaults when adding new settings.
- **Prompt strings:** Store long, multi-step prompts as triple-quoted strings and
  keep numbered steps for clarity.

---

## Architecture Patterns

- **API-first orchestration:** `main.py` should remain a thin wrapper around the
  FastAPI app. Implement business logic in services/workflows to keep routes
  declarative and testable.
- **Job source adapters:** Implement new sources by adhering to the
  `JobFetcher` protocol under `app/services/job_sources/`.
- **Persistence:** Prefer SQLModel migrations via schema updates; document any
  breaking changes in the architecture notes.

---

## Common Gotchas

- ⚠️ Forgetting to call `load_dotenv()` prevents the agent from authenticating
  with OpenAI; ensure it runs before creating `ChatOpenAI`.
- ⚠️ Keep prompts concise—overly long instructions can cause the agent to time
  out. Move context into comments or docs if needed.
- ⚠️ When changing the target site, verify selectors/actions remain compatible
  with the `browser-use` toolset.

---

## Testing Conventions

- Run `python main.py` to start the API and ensure endpoints respond.
- Use the sample data under `data/sample_jobs/` for deterministic manual tests.
- Capture database snapshots or exported JSON when validating deduplication or
  application workflow changes.
- Document manual test steps in tickets or feature specs so runs are repeatable.

---

## Documentation Requirements

- Update `/.ai/ARCHITECTURE.md` whenever you add modules or tools.
- Log new tasks or bug fixes in `/.ai/TICKETS.md` before starting work.
- Add or update feature specs under `/.ai/features/` for any sizeable prompt or
  workflow change.

---

## Security Guidelines

- Never commit `.env` or API keys.
- Scrub scraped job data before sharing outside the repository—remove email
  addresses or personal identifiers.
- When capturing screenshots, store them outside version control unless
  explicitly needed for documentation.

---

## 🤖 For AI Agents

1. Read the relevant ticket and feature spec before touching code.
2. Follow the test conventions above and record the outcome in your notes.
3. If you invent a new convention (naming, folder layout, prompt template), add
   it here so the next contributor understands the decision.

**Last Updated:** 2025-02-15
