---
name: spec-review
description: Use when reviewing a feature spec, PRD, acceptance criteria, MVP scope, or vertical slices before durable planning.
---

# Spec Review

Review a spec, PRD, or unclear acceptance artifact before durable planning. Keep the review focused
on product clarity, scope, acceptance criteria, and slice quality.

Skip this skill for small or already-clear tasks when an issue, review finding, or user-approved
request already contains an Acceptance Brief quality source and no
product/domain/API/data/security/user-workflow decision is being made. Record that reason in the
plan instead.

## Inputs

Read:

- `AGENTS.md`, `CONTEXT.md`, and `docs/CURRENT.md`
- `docs/ROADMAP.md` when product scope or milestones matter
- relevant `docs/specs/<spec>.md`, PRD, issue, review finding, or accepted task
- `docs/DOMAIN_MODEL.md`, `docs/DATA_MODEL.md`, or `docs/SECURITY_MODEL.md` when the spec touches
  those surfaces

## Checks

- Goal, problem, users, MVP, and non-goals are explicit.
- Acceptance criteria are testable and not merely implementation notes.
- Lightweight acceptance sources include every Acceptance Brief Field (see `write-spec`).
- Domain terms match `CONTEXT.md` and domain docs.
- Vertical slices deliver reviewable behavior, not horizontal layers.
- AFK/HITL labels are realistic.
- Testing and docs impact are named.
- Open questions block planning only when they affect behavior, data, security, UX, or scope.

## Second Review

Use `second-review` optionally when the artifact changes product direction, MVP boundary,
data/security behavior, architecture direction, money, deletion, sync, or external integration
behavior. Require it only when missing an issue could cause security, data-loss, money, auth,
crypto, deletion, or core architecture harm. Use the host agent's Codex integration when available.

## Output

Lead with findings:

```text
Findings
- [P1] <issue>
  Impact:
  Evidence:
  Suggested fix:

Review Result
- Pass / Pass with follow-ups / Blocked
- Second review: required/not required
```

If the result is `Blocked` or has P0/P1 findings, fix the artifact in `write-spec` (Edit-On-
Review mode) and re-run `spec-review` on the changed artifact. Only proceed to `write-plan` when
the result is `Pass` or `Pass with follow-ups`. See `bb-workflow` Review Iteration Pattern.

For substantial reviews, save the record in `docs/reviews/YYYY-MM-DD-<topic>-spec-review.md`.
