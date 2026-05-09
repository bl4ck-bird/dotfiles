---
name: write-plan
description: Use when turning a reviewed acceptance artifact, PRD, issue, review finding, or vertical slice into a compact implementation plan before editing code.
---

# Write Plan

Create a compact implementation plan a future agent or human can execute without guessing. The plan should constrain the work; it should not duplicate the acceptance artifact or become line-by-line code prose.

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
- `docs/CURRENT.md`
- `docs/AGENT_WORKFLOW.md`
- Reviewed acceptance artifact: spec, PRD, issue, review finding, or approved task
- Existing tests and package scripts

Read conditionally when relevant:

- `CONTEXT-MAP.md`: multiple bounded contexts, apps, packages, or external integrations.
- `docs/ARCHITECTURE.md`: boundaries, dependency direction, runtime surfaces, or module shape may change.
- `docs/DOMAIN_MODEL.md`: domain terms, invariants, entities, value objects, or workflows may change.
- `docs/DATA_MODEL.md`: persistence, migration, retention, deletion, backup, import, or export may change.
- `docs/SECURITY_MODEL.md`: auth, permissions, secrets, trust boundaries, sensitive data, deletion, or crypto may change.
- `docs/TESTING_STRATEGY.md`: verification commands, test levels, or test strategy may change.
- Relevant durable decisions when decisions are hard to reverse or surprising.

Before writing the plan, confirm the acceptance artifact was reviewed at the right weight:

- Full spec or PRD: `spec-review`, unless accepted risk is recorded.
- Clear issue, review finding, or approved user task: record the acceptance source, testable acceptance criteria, and why a separate spec review is unnecessary. If the request only exists in chat, add an `Approved Request Anchor` section with the request summary, approved scope, acceptance criteria, non-goals or stop conditions, and date.
- High-risk work: consider `second-review`; require it for high-risk security, data-loss, money, auth, crypto, deletion, or core architecture changes.

If product goal, domain terms, or acceptance criteria are unclear, run `pressure-test` or `domain-modeling` before writing the plan.

## Required Sections

Every plan must include:

```markdown
# <Feature> Implementation Plan

**Acceptance Source:** <spec/issue/review/user-approved task>
**Acceptance Review:** <spec-review path / accepted-risk note / why separate spec review is unnecessary>
**Goal:** <one sentence>
**Slice:** <vertical slice or issue id>
**Review Needs:** <architecture/test/security/docs/Codex>

## Approved Request Anchor

Required only when the acceptance source exists only in chat.

- Date:
- Request summary:
- Approved scope:
- Acceptance criteria:
- Non-goals / stop conditions:

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

- Keep plans compact. Link to the acceptance artifact instead of restating it.
- Map files before tasks. File boundaries shape the plan.
- Use vertical slices. Avoid horizontal phases like "build DB", "build API", "build UI" unless the slice is purely infrastructure.
- Each task should be independently verifiable.
- For behavior changes, include TDD steps. Do not plan "write tests later".
- Include exact commands where known.
- Include expected failure and expected pass signals.
- Include docs impact for domain, architecture, testing, security, and user-facing behavior.
- Include focused review checkpoints only for the concerns the task actually touches.
- Read `second-review` when deciding review needs. Follow its Required / Strongly Consider rules, including hard-to-inspect work or weak verification that could hide P0/P1 issues. Do not add optional Codex review by default; record why it is required, strongly considered, or not needed for this plan.

## File Size Planning

If a touched source file is already over 300 lines or likely to exceed 300 lines, include a split/responsibility note.

If a touched source file is over 600 lines, plan one of:

- scoped extraction before feature work
- explicitly documented exception
- narrow edit with follow-up refactor issue

## Self-Review

Before presenting the plan:

- Check every acceptance requirement maps to a task.
- Check every task has verification.
- Check no placeholder language remains.
- Check new names match `CONTEXT.md`.
- Check the plan does not introduce speculative abstractions.
- Check the plan does not copy large sections from the acceptance artifact.
- Check a human could inspect the plan without chat history.

## Output

Report:

- Plan path
- Slice count
- Highest-risk files
- Required reviews
- Recommended next command
- One next-phase question, such as whether to start the approved first slice
