# Tickets (JIRA-Style)

Repository work log for the job-search automation agent.
Only add or update tickets when a human stakeholder requests new work.

---

## 🔥 In Progress

### TICKET-001: Ship autonomous job-application MVP
**Status:** In Progress
**Type:** Feature
**Spec:** [.ai/features/2025-02-16_feature_jobapply_mvp.md](../.ai/features/2025-02-16_feature_jobapply_mvp.md)

**Acceptance Criteria:**
- Implements FastAPI service with `/jobs/fetch`, `/jobs/match`, `/jobs/apply`.
- Schedules daily discovery job and persists postings + applications.
- Generates tailored resume and cover letter assets per application.
- Updates docs and setup instructions for the MVP workflow.


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

**Last Updated:** 2025-02-16
