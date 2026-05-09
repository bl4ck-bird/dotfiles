---
name: docs-review
description: Use when reviewing durable project docs, handoff notes, acceptance artifacts, plans, decision records, README changes, or checking documentation drift after implementation.
---

# Docs Review

Review whether durable docs reflect the current product, architecture, workflow, and implementation
state.

## Inputs

Read the changed docs plus the artifacts they claim to summarize:

- `docs/CURRENT.md`
- relevant acceptance artifacts, plans, reviews, decision records, and source files
- `CONTEXT.md`, `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/DOMAIN_MODEL.md`,
  `docs/DATA_MODEL.md`, `docs/SECURITY_MODEL.md`, or `docs/TESTING_STRATEGY.md` when touched

## Checks

- Claims are backed by code, tests, decisions, or explicit user confirmation.
- Stub/TODO text is not treated as project truth.
- Current phase, active acceptance artifact/source, blockers, verification, and next action are
  accurate in `docs/CURRENT.md`.
- Acceptance artifacts, plans, reviews, and decision records do not duplicate or contradict durable
  docs.
- README remains user-facing and high-level.
- Setup commands match package scripts, project docs, or verified tool behavior.

## Output

Lead with findings and end with:

- docs pass, pass with follow-ups, or blocked
- docs updated or intentionally unchanged
- residual drift risk

For substantial reviews, save the record in `docs/reviews/YYYY-MM-DD-<topic>-docs-review.md`.
