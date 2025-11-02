# Coding Conventions & Patterns

Repository-wide norms for evolving the job-hunting automation script.
Keep this lean and update it when practices change.

---

## Code Style

- **Formatting:** Follow PEP 8. Run `ruff format` and `ruff check` if the tool is
  installed; otherwise keep lines under 100 characters and imports grouped as
  stdlib → third-party → local.
- **Async:** Use `asyncio`/`await` for any browser interactions. Avoid blocking
  calls inside the event loop.
- **Configuration:** Load environment variables through `dotenv` early and prefer
  `os.environ.get` with sensible defaults when adding new settings.
- **Prompt strings:** Store long, multi-step prompts as triple-quoted strings and
  keep numbered steps for clarity.

---

## Architecture Patterns

- **Single orchestrator module:** `main.py` owns agent setup. Extract helper
  modules only when logic becomes reusable across tasks.
- **Tool extensions:** When adding custom `browser_use` tools, place them in a
  dedicated module under `tools/` and document them in `ARCHITECTURE.md`.
- **CSV/IO helpers:** Centralize file-writing helpers so repeated workflows share
  consistent CSV schemas.

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

- Run `python main.py` in a controlled environment to verify the workflow.
- When feasible, capture mock responses or sample CSV output to compare against
  expected schemas.
- Document manual test steps in tickets or feature specs so runs are repeatable.

---

## Runtime Workflow

- Start the service with `python main.py serve` and test REST endpoints via the dashboard or curl.
- For one-off ingestion, run `python main.py fetch` which also logs top matches.
- Keep SQLite-compatible migrations in sync if future tooling is introduced.

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

**Last Updated:** 2025-02-16
