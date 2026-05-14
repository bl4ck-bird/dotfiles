---
name: docs-sync
description: Use when project documentation may need updates after code, architecture, scope, testing, security, or user-facing behavior changes.
---

# Docs Sync

Keep durable docs aligned with project state.

Triggered from `ship-check` Preconditions when behavior, architecture, testing, security, or
user-facing behavior changed. May also be invoked directly when user notes drift.
`code-quality-review` durable-docs-drift overlaps — that review flags drift *during code
review*; this skill *resolves* drift after acceptance.

## Check

Review changed files, identify durable concerns touched, decide whether any candidate doc
needs updates:

- `README.md`, `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, `CONTEXT-MAP.md`
- `docs/AGENT_WORKFLOW.md`, `docs/CURRENT.md`, `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`, `docs/DOMAIN_MODEL.md`, `docs/DATA_MODEL.md`
- `docs/SECURITY_MODEL.md`, `docs/TESTING_STRATEGY.md`
- `docs/DECISIONS/`, `docs/specs/`, `docs/plans/`, `docs/reviews/`
- feature specs and implementation plans

## Rules

- README stays high-level and user-facing.
- `CONTEXT.md` owns bounded-context vocabulary and canonical domain terms.
- Architecture, domain, data, security, testing rules live in focused docs.
- Specs and plans describe a single work item; not long-term source of truth.
- Remove stale claims instead of adding caveats around them.
- No placeholders, future-tense promises, or vague sync notes in `ready` docs.
- Scaffolded `stub` docs may contain TODOs. TODO claims are not project truth; non-TODO
  workflow, safety, and quality rules still apply.
- Promote docs from `stub` to `draft`/`ready` only when claims have been reviewed against the
  repo or confirmed by user.

## Common Triggers

Update docs when:

- Product goal, MVP boundary, or non-goals change.
- Domain term added, renamed, split, or deprecated.
- Domain invariant or workflow changes.
- New external dependency, runtime surface, adapter, or storage model introduced.
- Test commands, test strategy, or verification expectations change.
- Review finds a durable architecture, security, or data decision hidden only in chat.
- Active phase, acceptance artifact/source, plan, blocker, completed slice, verification
  evidence, or next action materially changes.

## Handoffs

Session about to be cleared → add/update handoff in `docs/reviews/`:

- current goal
- completed work
- decisions made
- verification evidence
- next safe action

Update `docs/CURRENT.md` with active phase and next recommended action when changed. Same
session continuing immediately → update once at end of phase, not after every step.

## Output

Report docs updated, docs intentionally left unchanged, and remaining documentation risks.
