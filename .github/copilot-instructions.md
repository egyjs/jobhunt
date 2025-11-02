# GitHub Copilot Repository Instructions

These notes orient AI assistants and contributors who touch this codebase.
They summarize the small but opinionated setup used for the job search agent.

---

## Quick Reference

1. Start with `/.ai/ARCHITECTURE.md` for the current module map and data flow.
2. Confirm conventions in `/.ai/CONVENTIONS.md` before editing Python or docs.
3. Check `/.ai/TICKETS.md` to see whether work has already been scheduled.
4. Use the feature spec templates in `/.ai/features/` when a change needs a full brief.

---

## Project Snapshot

**Type:** Python automation script that drives the `browser-use` agent to gather job postings from Indeed and save them to CSV.

**Primary entry point:** `main.py`

**Runtime:** Python 3.11+, with environment variables loaded from `.env`.

---

## Conventions

### Code Style
- Python formatting follows [PEP 8]; use `ruff format`/`ruff check` when available.
- Keep the orchestration logic in `main.py` declarative: define the high-level task string and agent configuration in one place.
- Prefer descriptive, multi-line docstrings for any new helpers or utilities.

### Testing & Verification
- There is no automated test suite yet. Validate changes by running `python main.py` and ensuring the agent can execute the workflow end-to-end without raising exceptions.
- When adding new automation behaviors, stub or mock network calls where practical so we can add tests later.

### Documentation
- Update `/.ai/ARCHITECTURE.md` whenever you move responsibilities between modules.
- Record planned or active work in `/.ai/TICKETS.md` before committing substantial changes.
- If you introduce a reusable browsing workflow, capture the requirements in a dated file under `/.ai/features/`.

---

## AI Workflow Expectations

1. **Clarify scope:** Confirm whether an existing ticket covers the task. If not, add one under "To Do" with acceptance criteria before coding.
2. **Plan first:** Outline the approach (e.g., update prompts, add helper modules, adjust CSV export) before editing files.
3. **Keep prompts auditable:** Document significant prompt changes in commit messages and, if complex, append rationale to the relevant feature spec.
4. **Regression check:** Run `python main.py` after modifications and summarize the observed behavior in your notes or PR description.
5. **Documentation sync:** Reflect any new behaviors or dependencies in the `.ai` docs as part of the same change.

---

## Security & Secrets

- Do **not** commit `.env` or any API keys. Store secrets locally only.
- Redact Personally Identifiable Information when copying job postings into tickets or docs.
- Review third-party tool updates before bumping versions.

---

## Getting Help

- Automation flow / architecture: `/.ai/ARCHITECTURE.md`
- Coding style & prompts: `/.ai/CONVENTIONS.md`
- Work queue: `/.ai/TICKETS.md`
- CI/CD expectations: `/.ai/ci_cd_instructions.md`

Keep this document current as the automation evolves. When in doubt, update the `.ai` references alongside your code changes.

---
