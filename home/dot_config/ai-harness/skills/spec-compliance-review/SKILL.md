---
name: spec-compliance-review
description: Use when verifying implementation matches the acceptance artifact — nothing missing, nothing extra, no misunderstanding. Binary result (✅ Spec compliant / ❌ Issues found). Runs first, before code-quality-review.
---

# Spec Compliance Review

Verify implementation matches **exactly** what was requested. First review after each
implementation slice or task. Code quality, architecture, durable docs come next in
`code-quality-review`.

## Core Rule

**Read the code. Do not trust the implementer's report.**

## When To Use

- After each implemented slice or task, before `code-quality-review`.
- When a worker subagent reports DONE or DONE_WITH_CONCERNS — verify independently.
- Before declaring a task complete in `subagent-driven-development`, `executing-plans-inline`,
  or `test-driven-development`.

## Inputs

- Acceptance artifact (spec, PRD, issue, plan task, approved request).
- Implementer's report and actual diff (read both; diff overrides report).
- `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md` for project-local rules.

Missing diff or artifact path → ask. Do not infer from chat.

## What To Check

Three classes — no severity grading, only presence.

| Class | Definition |
| --- | --- |
| **Missing** | Acceptance criterion has no implementing code (or only partial implementation). |
| **Extra** | Code in diff not required by artifact — features, flags, abstractions, refactors, file moves, renames. |
| **Misunderstood** | Right feature, wrong semantics, wrong domain term, or wrong contract — diff matches letter but not intent. |

Domain term drift (synonym from outside `CONTEXT.md`) is a **Misunderstood** finding here.
Deeper DDD review is in `code-quality-review`.

## Scope Discipline

Stay inside supplied artifact and diff (see `using-bb-harness` Review Scope Guard). Code
quality, naming style, architecture, test design, docs drift belong in `code-quality-review` —
**not here**.

## Iteration

❌ → implementer fixes via `receiving-review`, same review re-runs. **Stop after 2 cycles** —
escalate to user. See `using-bb-harness` review-rules.

Advance to `code-quality-review` only when result is ✅.

## Output

Binary. No severity, no Coverage Matrix (lives in `code-quality-review`).

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

When running as subagent from `subagent-driven-development`, use template at
`subagent-driven-development/spec-compliance-reviewer-prompt.md`. Template restates Core Rule
and inlines a "do not trust the report" reminder.
