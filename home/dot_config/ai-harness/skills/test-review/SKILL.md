---
name: test-review
description: Use when reviewing whether tests and verification prove accepted behavior, edge cases, regressions, and domain invariants without overfitting implementation details.
---

# Test Review

Review whether the tests and verification evidence prove the accepted behavior.

Use this when:

- acceptance depends on test quality
- verification is weak, broad, flaky, slow, expensive, or heavily mocked
- substantial behavior changed
- a bug fix needs regression proof
- a plan or diff claims coverage without clear evidence

## Inputs

Read:

- `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`, and `docs/TESTING_STRATEGY.md` when present
- the acceptance artifact and plan
- changed tests and changed production files
- test output, coverage notes, or manual verification evidence

## Checks

- Tests map to acceptance criteria, edge cases, and explicit non-goals.
- Behavior is tested through public interfaces, user-visible flows, or stable domain boundaries.
- Regression tests fail before the fix when a bug is being fixed.
- Assertions prove behavior rather than private helper details or incidental structure.
- Mocks do not remove the behavior under test.
- Slow, flaky, or expensive tests have a focused alternative or a recorded reason.
- Manual/browser verification is used only when automation cannot cover the behavior well.
- Verification commands and expected signals are recorded in the plan or final report.

## Output

Lead with findings and end with:

- Review result: pass, pass with follow-ups, or blocked
- Acceptance criteria covered
- Gaps or residual risk
- Required fixes before `ship-check`

For substantial reviews, save the record in `docs/reviews/YYYY-MM-DD-<topic>-test-review.md`.
