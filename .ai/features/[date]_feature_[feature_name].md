# Feature: [Concise Title]

Use this template to capture requirements for new browsing workflows or major
prompt updates. Create a copy, rename it `YYYY-MM-DD_feature_short-name.md`, and
link it from the relevant ticket.

**Date:** [YYYY-MM-DD]
**Status:** [Not Started | In Progress | Completed]
**Priority:** [High | Medium | Low]
**Related Ticket:** TICKET-XXX

---

## Overview

[1-2 sentences on the outcome and why it matters.]

**User Story**
As an automation maintainer, I want [goal], so that [benefit].

---

## Behavior Specification

Describe the agent's workflow using Gherkin so tests/manual checks can follow it.

### Scenario 1: [Primary success case]

```gherkin
Given the environment is configured with valid API keys
And the target site is reachable
When the agent runs the "[task summary]" prompt
Then it should [expected output]
And save results to [file or artifact]
```

### Scenario 2: [Important error/edge case]

```gherkin
Given [precondition]
When [action]
Then [expected safeguard or fallback]
```

Add more scenarios as needed for pagination, filtering, alternate data sources,
etc.

---

## Acceptance Criteria

- [ ] Agent instructions updated in `main.py`
- [ ] CSV/schema changes documented and handled
- [ ] Manual run of `python main.py` verifies success criteria
- [ ] Screenshots or logs archived if required
- [ ] Documentation updated (tickets, conventions, architecture)

---

## Test Strategy

- **Manual:** Document the exact parameters and expected artifacts.
- **Automated (future):** Outline how to mock browser interactions or assert CSV
  contents if we add unit tests.

When automated tests exist, reference their file paths here.

---

## Technical Notes

- Dependencies or API endpoints touched
- New environment variables and defaults
- Follow-up clean-up tasks, if any

---

## 🤖 For AI Agents

1. Update this spec as you refine the prompt or workflow; keep it synchronized
   with the ticket.
2. Record observations from dry runs (timeouts, selectors, flaky pages) so future
   maintainers know the risks.
3. Mark the status and completion date once the ticket ships.

**Last Updated:** 2025-02-15
