---
name: docs-sync
description: Use when project documentation may need updates after code, architecture, scope, testing, security, or user-facing behavior changes.
---

# Docs Sync

Keep durable docs aligned with the project state.

## Check

Review changed files, identify the durable concerns they touched, and decide whether any of these candidate docs need updates. This is not a mandatory checklist:

- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `CONTEXT.md`
- `CONTEXT-MAP.md`
- `docs/AGENT_WORKFLOW.md`
- `docs/CURRENT.md`
- `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/DOMAIN_MODEL.md`
- `docs/DATA_MODEL.md`
- `docs/SECURITY_MODEL.md`
- `docs/TESTING_STRATEGY.md`
- `docs/DECISIONS/`
- `docs/specs/`
- `docs/plans/`
- `docs/reviews/`
- feature specs and implementation plans

## Rules

- README stays high-level and user-facing.
- `CONTEXT.md` owns bounded-context vocabulary and canonical domain terms.
- Architecture, domain, data, security, and testing rules live in focused docs.
- Specs and plans describe a single work item; they are not the long-term source of truth.
- Remove stale claims instead of adding caveats around them.
- Do not leave placeholders, future-tense promises, or vague sync notes in `ready` docs.
- Scaffolded `stub` docs may contain TODOs. TODO claims are not project truth; non-TODO workflow, safety, and quality rules still apply.
- Promote docs from `stub` to `draft` or `ready` only when the claims have been reviewed against the repo or confirmed by the user.

## Common Triggers

Update docs when:

- Product goal, MVP boundary, or non-goals change.
- A domain term is added, renamed, split, or deprecated.
- A domain invariant or workflow changes.
- A new external dependency, runtime surface, adapter, or storage model is introduced.
- Test commands, test strategy, or verification expectations change.
- Review finds a durable architecture, security, or data decision hidden only in chat.
- The active phase, active acceptance artifact/source, active plan, blocker, completed slice, verification evidence, or next action materially changes.

## Handoffs

When the session is about to be cleared, add or update a handoff in `docs/reviews/`:

- current goal
- completed work
- decisions made
- verification evidence
- next safe action

Also update `docs/CURRENT.md` with the active phase and next recommended action when those fields changed. If the same session continues immediately, update once at the end of the phase instead of churning the file after every small step.

## Output

Report docs updated, docs intentionally left unchanged, and any documentation risks that remain.
