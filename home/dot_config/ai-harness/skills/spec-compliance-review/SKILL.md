---
name: spec-compliance-review
description: Use when verifying implementation matches the acceptance artifact — nothing missing, nothing extra, no misunderstanding. Binary result (✅ Spec compliant / ❌ Issues found). Runs first, before code-quality-review.
---

# Spec Compliance Review

Verify the implementation matches **exactly** what was requested. First review after
each implementation slice or task. Code quality, architecture, and durable docs come
next in `code-quality-review`.

## Core Rule

**Read the code. Do not trust the implementer's report.**

## When To Use

- After each implemented slice or task, before `code-quality-review`.
- When a worker subagent reports DONE or DONE_WITH_CONCERNS — verify independently.
- Before declaring a task complete in `subagent-driven-development`,
  `executing-plans-inline`, or `test-driven-development`.

## Inputs

- The acceptance artifact (spec, PRD, issue, plan task, or approved request).
- The implementer's report and the actual diff (read both; the diff overrides the
  report).
- `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md` for project-local rules.

If a diff or artifact path is missing, ask for it. Do not infer from chat.

## What To Check

Three classes of finding — no severity grading at this stage, only presence.

| Class | Definition |
| --- | --- |
| **Missing** | An acceptance criterion has no implementing code (or has only partial implementation). |
| **Extra** | Code in the diff that is not required by the acceptance artifact — features, flags, abstractions, refactors, file moves, renames. |
| **Misunderstood** | The right feature implemented with wrong semantics, wrong domain term, or wrong contract — diff matches the criterion's letter but not its intent. |

Domain term drift (using a synonym from outside `CONTEXT.md`) is a **Misunderstood**
finding here. The deeper DDD review is in `code-quality-review`.

## Scope Discipline

Stay inside the supplied artifact and diff (see `using-bb-harness` Review Scope
Guard). Code quality, naming style, architecture, test design, and docs drift belong
in `code-quality-review` — **not here**.

## Iteration

If ❌, the implementer fixes via `receiving-review` and the same review re-runs.
**Stop after 2 cycles** — escalate to the user. See `using-bb-harness` review-rules.

Only advance to `code-quality-review` when the result is ✅.

## Output

Binary. No severity, no Coverage Matrix (that lives in `code-quality-review`).

```text
Result: ✅ Spec compliant
- Acceptance criteria covered: <list>
- Files inspected: <list>
- Verification evidence read: <commands run / outputs read>
```

or

```text
Result: ❌ Issues found
- Missing: <criterion> (no code at <file:line>)
- Extra: <behavior> (not in artifact)
- Misunderstood: <criterion> at <file:line> — <why>
- Next: implementer fixes; re-run spec-compliance-review.
```

## Subagent Dispatch

When running this review as a subagent from `subagent-driven-development`, use the
template at `subagent-driven-development/spec-compliance-reviewer-prompt.md`. The
template restates the Core Rule and inlines a "do not trust the report" reminder.
