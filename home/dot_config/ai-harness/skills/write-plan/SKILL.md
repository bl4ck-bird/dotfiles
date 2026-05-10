---
name: write-plan
description: Use when turning a reviewed acceptance artifact, PRD, issue, review finding, or vertical slice into a compact implementation plan before editing code.
---

# Write Plan

Create a compact implementation plan a future agent or human can execute without guessing. The plan
should constrain the work; it should not duplicate the acceptance artifact or become line-by-line
code prose.

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
- `docs/ARCHITECTURE.md`: boundaries, dependency direction, runtime surfaces, or module shape may
  change.
- `docs/DOMAIN_MODEL.md`: domain terms, invariants, entities, value objects, or workflows may
  change.
- `docs/DATA_MODEL.md`: persistence, migration, retention, deletion, backup, import, or export may
  change.
- `docs/SECURITY_MODEL.md`: auth, permissions, secrets, trust boundaries, sensitive data, deletion,
  or crypto may change.
- `docs/TESTING_STRATEGY.md`: verification commands, test levels, or test strategy may change.
- Relevant durable decisions when decisions are hard to reverse or surprising.

Before writing the plan, confirm the acceptance artifact was reviewed at the right weight:

- Full spec or PRD: `spec-review`, unless an explicit accepted-risk record exists.
- Clear issue, review finding, or approved user task: record the acceptance source and the
  Acceptance Brief Fields (see `write-spec`). If the request only exists in chat, add an
  `Approved Request Anchor` section with those fields and date.
- High-risk work: consider `second-review`; require it when the change touches a High-Risk Surface
  (see `second-review`).

If product goal, domain terms, or acceptance criteria are unclear, run `pressure-test` or
`domain-modeling` before writing the plan.

Accepted-risk records may skip a normal gate only when explicitly approved by the user or already
present in an approved plan. Record:

- skipped gate
- reason
- risk that could be missed
- compensating check
- user acceptance
- follow-up or expiry

## Required Sections

Every plan must include:

```markdown
# <Feature> Implementation Plan

**Acceptance Source:** <spec/issue/review/user-approved task>
**Acceptance Review:** <spec-review path / explicit accepted-risk record / why separate spec review is unnecessary>
**Goal:** <one sentence>
**Slice:** <vertical slice or issue id>
**Review Needs:** <architecture/test/security/docs/second-review>

## Approved Request Anchor

Required only when the acceptance source exists only in chat. Include:

- Date:
- Request summary:
- Approved scope:
- Acceptance Brief Fields (see `write-spec`).

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

## Commit / Stack Strategy

Required for non-trivial work. Choose one:

- No commit unless the user asks after `ship-check`.
- Single commit after `ship-check`.
- One commit per completed vertical slice.
- Stacked branches or PRs, with branch order and review audience named.

## Rollback / Recovery

## Open Risks
```

## Planning Rules

- Keep plans compact. Link to the acceptance artifact instead of restating it.
- Map files before tasks. File boundaries shape the plan.
- Use vertical slices. Avoid horizontal phases like "build DB", "build API", "build UI" unless the
  slice is purely infrastructure.
- Each task should be independently verifiable.
- For behavior changes, include TDD steps. Do not plan "write tests later".
- Include exact commands where known.
- Include expected failure and expected pass signals.
- Include docs impact for domain, architecture, testing, security, and user-facing behavior.
- Include commit/stack strategy, but do not authorize commit, push, PR, or stack operations
  unless the user or project-local instructions already approved them.
- Include focused review checkpoints only for the concerns the task actually touches.
- Decide `second-review` need per its Required / Strongly Consider rules. Do not add it by default;
  record why it is required, strongly considered, or not needed for this plan.
- Include `test-review` when tests are weak, heavily mocked, flaky, missing acceptance coverage, or
  central to the acceptance risk.

## File Size Planning

Apply the file/function size thresholds defined in `architecture-review` (File And Complexity
Thresholds). When a touched file is at or near the 300/600 threshold, the plan must include one
of: scoped extraction before feature work, an explicitly documented exception, or a narrow edit
with a follow-up refactor issue.

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
