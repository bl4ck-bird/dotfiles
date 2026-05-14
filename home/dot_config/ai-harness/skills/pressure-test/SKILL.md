---
name: pressure-test
description: Use when a product idea, feature, architecture, spec, or plan needs pressure-testing before documentation or implementation. Assumes goal/direction is set — run product-discovery first if MVP or non-goals are unclear.
---

# Pressure Test

Pressure-test the idea before turning it into a spec or code.

## Core Rule

Ask one question at a time. Include your recommended answer or tradeoff so the user is not
designing from a blank page.

## What To Challenge

- Product goal — what problem is actually being solved?
- User — who cares enough to use this?
- MVP — smallest useful behavior?
- Non-goals — what should not be built now?
- Success — how will we know the slice worked?
- Domain terms — which words are overloaded or ambiguous?
- Edge cases — what inputs, states, workflows break assumptions?
- Data — what must be stored, derived, migrated, deleted, protected?
- UX — user's repeated workflow, not only first happy path?
- Architecture — what boundary or dependency decision is hard to reverse?
- Tests — what behavior proves this is done?
- Review — what deserves independent second review?

## Use Codebase Evidence

If a question can be answered by reading the repo, inspect instead of asking.

- Existing domain terms in `CONTEXT.md` or `docs/DOMAIN_MODEL.md`
- Existing package structure
- Existing tests and commands
- Established UI patterns
- Prior durable decisions

## Stop Condition

- Product goal, MVP, non-goals, success criteria clear enough for a spec.
- Domain terms resolved or marked as open questions.
- Risky tradeoffs identified.
- Next artifact obvious: `CONTEXT.md`, acceptance artifact, durable decision, or
  implementation plan.

## Output

When done, summarize:

- Resolved decisions
- Recommended product direction
- Open questions
- Risks
- Suggested next skill
- Docs to update

Do not create a long spec here. Use `write-spec` next.
