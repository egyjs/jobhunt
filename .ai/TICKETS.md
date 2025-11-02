# Tickets (JIRA-Style)

Repository work log for the job-search automation agent.
Only add or update tickets when a human stakeholder requests new work.

---

## 🔥 In Progress

### TICKET-001: Build autonomous job application MVP
**Status:** In Progress
**Type:** Epic

**Summary:** Deliver the multi-source job discovery, matching, and auto-application MVP that coordinates
LinkedIn, Indeed, Glassdoor, and company career pages. Provide persistence, AI-assisted tailoring, and a
dashboard-ready API so the agent can continuously pursue relevant opportunities.

**Acceptance Criteria:**
- REST API exposes `/jobs/fetch`, `/jobs/match`, and `/jobs/apply` endpoints with documented payloads.
- Job data persists to a relational store with deduplication across sources.
- Matching engine ranks jobs using resume/profile similarity and exposes scores.
- Resume/cover letter tailoring outputs per-job artifacts saved locally.
- Application workflow tracks status transitions and logs outcomes.
- Documentation updated (README, architecture, conventions/spec) with new workflows and configuration.
- Manual run of `python main.py` boots the API server and background scheduler without errors.

**Notes:** Coordinate feature specification updates under `.ai/features/` to capture workflow details and testing
scenarios.
---

## 📋 To Do (Ready for Development)

_No scheduled work. Add a ticket here when a stakeholder prioritizes a task._

---

## 🗂️ Backlog (Not Yet Prioritized)

_No backlog items recorded._

---

## ✅ Done

### TICKET-000: Initialize automation scaffold
**Status:** Done
**Completed:** 2025-02-15
**Type:** Task

**Notes:** Added the initial `browser-use` powered script (`main.py`) and documentation scaffolding.

---

## 🤖 Usage Guide

1. Check this file before starting work; do not assume you can self-assign tasks.
2. Create tickets using incremental IDs (e.g., TICKET-001) when stakeholders ask
   for new features or fixes. Capture acceptance criteria alongside manual test
   steps when possible.
3. Link to dated specs in `/.ai/features/` for multi-step workflows.
4. Move completed tickets to the **Done** section with the actual completion
   date and a short summary of the delivered change.

**Last Updated:** 2025-02-15
