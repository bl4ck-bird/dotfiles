---
name: ship-check
description: Use when preparing to hand off, commit, merge, open a PR, or release after implementation and focused reviews.
---

# Ship Check

Run a final readiness pass before handing work back or shipping it.

## Preconditions

Before ship-check, substantial work should have:

- Acceptance artifact with acceptance criteria: spec, PRD, issue, review finding, or approved task.
- Primary spec review for full specs/PRDs, or a recorded reason why separate spec review was unnecessary.
- Implementation plan or clear small-task rationale.
- TDD or regression coverage where behavior changed.
- Focused review findings resolved or explicitly accepted.
- `docs-sync` considered.

## Checklist

1. Inspect `git status` and confirm the change set is scoped to the request.
2. Read the relevant diff and ensure no unrelated user changes were reverted.
3. Run the narrowest meaningful tests, type checks, linters, or build checks available.
4. Confirm docs sync was considered for changed behavior, architecture, tests, and security.
5. Confirm `docs/CURRENT.md` reflects the final current phase, blocker status, last verification, and next action when substantial work changed state.
6. Confirm `implementation-review`, `architecture-review`, `docs-review`, and `security-review` were run or explicitly not needed.
7. Run or request `second-review` for required high-risk changes, or note why optional independent review is not needed.
8. Confirm no source file crossed the 300/600 line thresholds without review.
9. Confirm validation was not gamed by weakening assertions, narrowing coverage, skipping relevant checks, or changing tests to match broken behavior.
10. Summarize the result with verification evidence and residual risk.

If independent review is required but unavailable, do not silently pass. Record the unavailable reason, compensating review, accepted risk, and whether the user explicitly accepted shipping without it.

If relevant checks already failed before this work, state that clearly and do not attribute them to your change. If a check fails after your change, make one targeted fix when the cause is clear; otherwise stop and report the failure with evidence.

## Output

Keep the final report short:

- What changed
- What was verified
- Focused reviews completed
- Independent review status
- Docs updated or intentionally unchanged
- What remains risky or unverified

## Do Not Ship If

- Required checks fail.
- The implementation does not match the accepted behavior.
- A P0/P1 review finding is unresolved.
- Validation was weakened or skipped to make the result look green.
- The final answer would need to hide uncertainty.
