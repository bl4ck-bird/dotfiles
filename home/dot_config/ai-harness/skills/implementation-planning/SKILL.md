---
name: implementation-planning
description: Use when turning an approved spec, PRD, issue, or vertical slice into an implementation plan before editing code.
---

# Implementation Planning

Create an implementation plan a future agent or human can execute without guessing.

## Save Location

Save plans to:

```text
docs/plans/YYYY-MM-DD-<feature-or-slice>.md
```

Use the project's established location if it already has one.

## Reading Tiers

Always read:

- `AGENTS.md`
- `CONTEXT.md`
- `docs/AGENT_WORKFLOW.md`
- Relevant spec in `docs/specs/`
- Existing tests and package scripts

Read conditionally when relevant:

- `CONTEXT-MAP.md`: multiple bounded contexts, apps, packages, or external integrations.
- `docs/ARCHITECTURE.md`: boundaries, dependency direction, runtime surfaces, or module shape may change.
- `docs/DOMAIN_MODEL.md`: domain terms, invariants, entities, value objects, or workflows may change.
- `docs/DATA_MODEL.md`: persistence, migration, retention, deletion, backup, import, or export may change.
- `docs/SECURITY_MODEL.md`: auth, permissions, secrets, trust boundaries, sensitive data, deletion, or crypto may change.
- `docs/TESTING_STRATEGY.md`: verification commands, test levels, or test strategy may change.
- Relevant ADRs when decisions are hard to reverse or surprising.

Before writing the plan, confirm the spec had a primary review through `review-gate`, or record why planning is proceeding with accepted risk.

If product goal, domain terms, or acceptance criteria are unclear, run `critical-interview` or `domain-modeling` before writing the plan.

## Required Sections

Every plan must include:

```markdown
# <Feature> Implementation Plan

**Spec:** docs/specs/<file>.md
**Spec Review:** <review path or accepted-risk note>
**Goal:** <one sentence>
**Slice:** <vertical slice or issue id>
**Review Needs:** <architecture/test/security/docs/Codex>

## File Responsibility Map

| File | Create/Modify | Responsibility | Risk |
| --- | --- | --- | --- |

## Tasks

### Task 1: <small behavior>

- [ ] Step 1: Write failing behavior test
- [ ] Step 2: Run test and confirm expected failure
- [ ] Step 3: Implement minimal code
- [ ] Step 4: Run narrow verification
- [ ] Step 5: Refactor after green
- [ ] Step 6: Update docs or explain why not needed
- [ ] Step 7: Review checkpoint

## Verification

## Docs Impact

## Rollback / Recovery

## Open Risks
```

## Planning Rules

- Map files before tasks. File boundaries shape the plan.
- Use vertical slices. Avoid horizontal phases like "build DB", "build API", "build UI" unless the slice is purely infrastructure.
- Each task should be independently verifiable.
- For behavior changes, include TDD steps. Do not plan "write tests later".
- Include exact commands where known.
- Include expected failure and expected pass signals.
- Include docs impact for domain, architecture, testing, security, and user-facing behavior.
- Include review-gate checkpoints for risky or broad tasks.
- Include Codex second review for plans touching architecture, domain model, persistence, security, money, data loss, auth, crypto, deletion, sync, concurrency, or large diffs.

## File Size Planning

If a touched source file is already over 300 lines or likely to exceed 300 lines, include a split/responsibility note.

If a touched source file is over 600 lines, plan one of:

- scoped extraction before feature work
- explicitly documented exception
- narrow edit with follow-up refactor issue

## Self-Review

Before presenting the plan:

- Check every spec requirement maps to a task.
- Check every task has verification.
- Check no placeholder language remains.
- Check new names match `CONTEXT.md`.
- Check the plan does not introduce speculative abstractions.
- Check a human could inspect the plan without chat history.

## Output

Report:

- Plan path
- Slice count
- Highest-risk files
- Required reviews
- Recommended next command
- One next-phase question, such as whether to start the approved first slice
