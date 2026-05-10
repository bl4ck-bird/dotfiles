---
name: pressure-test
description: Use when a product idea, feature, architecture, spec, or plan needs pressure-testing before documentation or implementation.
---

# Pressure Test

Pressure-test the idea before turning it into a spec or code.

## Core Rule

Ask one question at a time. For each question, include your recommended answer or tradeoff so the
user is not forced to design from a blank page.

## What To Challenge

- Product goal: what problem is actually being solved?
- User: who cares enough to use this?
- MVP: what is the smallest useful behavior?
- Non-goals: what should not be built now?
- Success: how will we know the slice worked?
- Domain terms: which words are overloaded or ambiguous?
- Edge cases: what inputs, states, or workflows break assumptions?
- Data: what must be stored, derived, migrated, deleted, or protected?
- UX: what is the user's repeated workflow, not only the first happy path?
- Architecture: what boundary or dependency decision is hard to reverse?
- Tests: what behavior proves this is done?
- Review: what deserves independent second review?

## Use Codebase Evidence

If a question can be answered by reading the repo, inspect the repo instead of asking the user.

Examples:

- Existing domain terms in `CONTEXT.md` or `docs/DOMAIN_MODEL.md`
- Existing package structure
- Existing tests and commands
- Established UI patterns
- Prior durable decisions

## Stop Condition

Stop when:

- Product goal, MVP, non-goals, and success criteria are clear enough for a spec.
- Domain terms are either resolved or marked as open questions.
- Risky tradeoffs are identified.
- The next artifact is obvious: `CONTEXT.md`, acceptance artifact, durable decision, or
  implementation plan.

## Output

When the interview is done, summarize:

- Resolved decisions
- Recommended product direction
- Open questions
- Risks
- Suggested next skill
- Docs to update

Do not create a long spec in this skill. Use `write-spec` next.
