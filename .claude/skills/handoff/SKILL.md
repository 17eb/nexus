---
name: handoff
description: Write docs/handoff.md so a fresh session can pick up this work.
disable-model-invocation: true
---

# Handoff

Write `planning-docs/handoff.md` for a session that has zero context. Overwrite
the file if it exists — git keeps the history.

First run `git status` and `git diff --stat` so the file list is accurate
rather than recalled.

## Sections

- **Goal** — what we're building and the acceptance criteria
- **Current state** — what works, what's broken, what's untested
- **Key decisions** — and *why*, not just what
- **Files changed** — by path, one line each on what changed and why
- **Dead ends** — what we tried that failed, so nobody retries it
- **Next steps** — in order
- **Commands** — build, test, run

## Rules

- Reference file paths; don't paste code. The next session can read files.
- Only record what you verified. If you didn't run the tests, say untested.
- Flag anything you're unsure about rather than smoothing it over.
- Be terse. This is a briefing, not a report.