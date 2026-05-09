---
name: plan-review
description: Use when reviewing an implementation plan before code execution, especially file responsibility, vertical slices, TDD steps, verification, docs impact, or risk.
---

# Plan Review

Review a non-trivial implementation plan before editing code. The goal is to catch vague tasks, oversized slices, missing tests, and architecture drift early without turning clear small tasks into process work.

## Inputs

Read:

- `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`, and `docs/AGENT_WORKFLOW.md`
- relevant acceptance artifact and its review record when applicable
- `docs/plans/<plan>.md`
- architecture, domain, data, security, testing docs when the plan touches those concerns

## Checks

- Acceptance source is named.
- Spec review exists for a full spec or PRD, or the plan explains why a separate spec review is unnecessary.
- Every acceptance criterion maps to at least one task or explicit non-goal.
- The plan links to the acceptance artifact instead of restating it at length.
- File responsibility map is specific enough to constrain edits.
- Tasks are vertical, small, and independently verifiable.
- Behavior changes use `behavior-tdd` with expected RED/GREEN signals.
- Verification commands are exact where known.
- Docs impact and rollback/recovery are named.
- DDD/SOLID, file-size, security, data-loss, and dependency risks are surfaced.

## Follow-On Reviews

- Use `architecture-review` for boundary, DDD, SOLID, or file-size concerns.
- Use `security-review` for auth, secrets, crypto, deletion, sensitive data, or destructive operations.
- Use `second-review` optionally for risky, broad, weakly tested, or security-sensitive plans. Require it for high-risk security, data-loss, money, auth, crypto, deletion, or core architecture plans.

## Output

Lead with findings and end with:

- Review result: pass, pass with follow-ups, or blocked
- Required fixes before `execute-plan`
- Required follow-on reviews

For substantial reviews, save the record in `docs/reviews/YYYY-MM-DD-<topic>-plan-review.md`.
