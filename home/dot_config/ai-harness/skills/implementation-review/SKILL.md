---
name: implementation-review
description: Use when reviewing an implementation diff, completed slice, tests, docs impact, or review-fix pass before handoff or shipping.
---

# Implementation Review

Review a completed slice or diff against the accepted artifact and plan. This is the default
post-implementation review before docs sync or ship check.

Scope: acceptance compliance, scope/churn, test signal, obvious code-quality smells. Defer deeper
DDD/SOLID/file-size findings to `architecture-review`, deeper test-design findings to
`test-review`, and deeper auth/data-loss findings to `security-review`.

## Inputs

Read:

- `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`
- relevant acceptance artifact, review record when applicable, plan, and plan review
- changed file list or diff
- test and verification output

## Checks

- Diff scope matches the approved plan and does not include unrelated churn.
- Behavior matches acceptance criteria.
- Tests prove public behavior, user-visible flows, or domain invariants.
- Edge cases, regressions, and failure paths are covered or explicitly accepted.
- No silent failures: swallowed exceptions, broad catches without re-raise, or fallbacks that mask
  upstream errors.
- Architecture, DDD/SOLID, file-size, and complexity rules are still satisfied.
- Security/data/docs impacts were reviewed with the appropriate focused skill when relevant.
- Review findings were fixed, deferred, or accepted with a reason.

## Follow-On Reviews

- Use `architecture-review` for maintainability or boundary concerns.
- Use `test-review` when acceptance depends on test quality or verification is weak.
- Use `security-review` for sensitive surfaces.
- Use `docs-review` when durable docs changed or may have drifted.
- Use `second-review` for broad, risky, or hard-to-inspect diffs.

## Output

Lead with findings and end with:

- Review result: pass, pass with follow-ups, or blocked
- Verification evidence reviewed
- Required fixes before `ship-check`
- Residual risk

For substantial reviews, save the record in
`docs/reviews/YYYY-MM-DD-<topic>-implementation-review.md`.
