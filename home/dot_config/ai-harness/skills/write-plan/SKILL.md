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

Before writing the plan, confirm the acceptance artifact was prepared at the right weight:

- Full spec or PRD: `write-spec` Self-Review completed (Product Clarity + Domain Alignment),
  unless an explicit accepted-risk record exists.
- Clear issue, review finding, or approved user task: record the acceptance source and the
  Acceptance Brief Fields (see `write-spec`). If the request only exists in chat, add an
  `Approved Request Anchor` section with those fields and date.
- High-risk work: consider `second-review`; require it when the change touches a High-Risk
  Surface (see `second-review`).

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
**Acceptance Self-Review:** <write-spec Self-Review note in the artifact / explicit accepted-risk record / why a separate Self-Review is unnecessary>
**Goal:** <one sentence>
**Slice:** <vertical slice or issue id>
**Review Needs:** <code-quality-review (default after spec-compliance) / security-review when security surface touched / second-review when High-Risk Surface or boundary change>

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

## Edit-On-Findings Mode

When the plan is revised because `spec-compliance-review` or `code-quality-review` found a
plan-level flaw (wrong file boundary, missing task, weak verification), or because the
user changed scope, update the existing plan at the same path. Do not create a new plan
file or restart from scratch. Address each finding, preserve tasks not flagged, and re-run
Plan Self-Review on the changed plan. See `using-bb-harness` Review Iteration Pattern.

## Planning Rules

- Keep plans compact. Link to the acceptance artifact instead of restating it.
- Map files before tasks. File boundaries shape the plan.
- Use vertical slices. Avoid horizontal phases like "build DB", "build API", "build UI"
  unless the slice is purely infrastructure.
- Each task should be independently verifiable.
- For behavior changes, include TDD steps. Do not plan "write tests later".
- Include exact commands where known.
- Include expected failure and expected pass signals.
- Include docs impact for domain, architecture, testing, security, and user-facing
  behavior.
- Include commit/stack strategy, but do not authorize commit, push, PR, or stack
  operations unless the user or project-local instructions already approved them.
- Default review per implemented task: `spec-compliance-review` → `code-quality-review`.
  Plan only the *additional* reviews relevant to the task — `security-review` when the
  task touches a security surface, `second-review` when its Required / Strongly Consider
  rules apply.

## File Size Planning

Apply the file/function size thresholds defined in `code-quality-review` (File And
Complexity Thresholds). When a touched file is at or near the 300/600 threshold, the plan
must include one of: scoped extraction before feature work, an explicitly documented
exception, or a narrow edit with a follow-up refactor issue.

## Self-Review

Before presenting the plan, walk this checklist yourself. The harness no longer runs a
separate `plan-review` skill — plan correctness is owned here, then re-verified by
`spec-compliance-review` + `code-quality-review` after implementation.

### Plan Hygiene

- Every acceptance requirement maps to a task or explicit non-goal.
- Every task has exact verification commands and expected RED / GREEN signals for TDD
  steps.
- No placeholder language ("TBD", "later", "appropriate error handling").
- New identifier names match `CONTEXT.md`.
- The plan does not copy large sections from the acceptance artifact — it links.
- A human can inspect the plan without chat history.

### Architecture Soundness (SOLID upstream check)

When the plan touches more than glue / CRUD code:

- **SRP**: each file in the File Responsibility Map has one primary reason to change. If
  a file is listed for two unrelated concerns, split or revisit.
- **DIP**: domain or application code in the plan does not depend on framework, ORM,
  HTTP client, or filesystem types. If it must, name the port/adapter explicitly.
- **Dependency direction**: imports flow inward (UI / infra → application → domain). Plan
  does not introduce a domain file that imports an infrastructure file.
- **File-size impact**: estimate per touched file. If a file already at or near the 300 /
  600-line threshold (see `code-quality-review` File And Complexity Thresholds), the plan
  includes scoped extraction, a documented exception, or a follow-up refactor task.
- **Speculative abstraction**: the plan does not introduce ports, interfaces, factories,
  or strategy patterns for variation that does not yet exist.
- **Cross-cutting concerns**: logging, auth, persistence, caching are placed at consistent
  boundaries, not sprinkled across domain code.

For glue, config, docs, or scaffold-only plans, mark this section `N/A — non-architectural
change` and skip.

### Domain Alignment

Same checks as `write-spec` Self-Review Domain Alignment apply here when the plan touches
domain code. Do not re-list invariants resolved in the spec; do check the plan respects
them.

### Independent Review

Two options when the author wants a second pair of eyes:

- **`plan-document-reviewer-prompt.md`** (in this directory) — dispatch a same-host
  subagent that re-reads the plan, acceptance artifact, and project docs
  independently. Use when:
  - Plan crosses module boundaries or changes dependency direction.
  - Many tasks or large file responsibility map.
  - High-Risk Surface (see `second-review`) touched.
  - Self-Review passed but the author is uncertain about file mapping or
    verification commands.
- **`second-review`** (Codex by default) — different-model, fully-independent
  double-check. Required when the plan touches a High-Risk Surface; otherwise
  optional. Heavier than the same-host reviewer.

Neither is mandatory — Self-Review alone is the default. Pick the one (or both)
whose value justifies the time.

Otherwise, the next gates are `spec-compliance-review` and `code-quality-review` after
each implemented slice.

## Output

Report:

- Plan path
- Slice count
- Highest-risk files
- Required reviews
- Recommended next command
- One next-phase question, such as whether to start the approved first slice
