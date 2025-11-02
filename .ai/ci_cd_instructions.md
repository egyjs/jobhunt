# CI/CD Instructions

The project does not yet ship with a full CI/CD pipeline. This guide clarifies
what automation exists today and which commands are safe for AI agents to run.

---

## Pipeline Overview

```text
Manual workflow only:
1. Install dependencies (pip + browser-use extras)
2. Set environment variables in `.env`
3. Run `python main.py` locally to execute the job-scraping agent
4. Review generated CSV/screenshot artifacts manually
```

When the project grows, document GitHub Actions or other CI jobs here.

---

## Quality Gates

- **Runtime sanity check:** `python main.py` should complete the multi-step task
  without raising exceptions.
- **Formatting (optional but encouraged):** `ruff check` and `ruff format --check`
  must pass when the tool is available.

---

## Commands Reference

### Safe for AI to Run ✅
```bash
python main.py          # Execute the browsing workflow locally
ruff check              # Static analysis (if Ruff is installed)
ruff format --check     # Formatting validation
```

### Requires Human Approval ❌
```bash
pip install --upgrade browser-use
pip install --upgrade openai
# Any command that deploys code or pushes to protected branches
```

---

## Environment Variables

Create a `.env` file (never commit it) with at minimum:

```bash
OPENAI_API_KEY=sk-...
BROWSER_USE_HEADLESS=true  # optional, defaults to toolkit settings
OUTPUT_DIR=./artifacts     # optional override for generated files
```

Document new variables here when you introduce them.

---

## 🤖 For AI Agents

- Verify `.env` is populated locally before running the workflow.
- Summarize command output in PR descriptions so humans can review run results.
- Do not modify deployment tooling without explicit approval; document proposed
  changes in a ticket first.

**Last Updated:** 2025-02-15
