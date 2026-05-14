---
name: write-plan
description: Use when turning a reviewed acceptance artifact, PRD, issue, review finding, or vertical slice into a compact implementation plan before editing code.
---

# Write Plan

Compact plan a future agent or human can execute without guessing. Constrain work; do not
duplicate the acceptance artifact or become line-by-line code prose.

## Save Location

```text
docs/plans/YYYY-MM-DD-<feature-or-slice>.md
```

Use the project's established location if it has one.

## Reading Tiers

Always read:

- `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`, `docs/AGENT_WORKFLOW.md`
- Reviewed acceptance artifact (spec, PRD, issue, review finding, approved task)
- Existing tests and package scripts

Conditional reads:

| Doc | Read when |
| --- | --- |
| `CONTEXT-MAP.md` | Multiple bounded contexts, apps, packages, external integrations |
| `docs/ARCHITECTURE.md` | Boundaries, dependency direction, runtime surfaces, module shape may change |
| `docs/DOMAIN_MODEL.md` | Domain terms, invariants, entities, value objects, workflows may change |
| `docs/DATA_MODEL.md` | Persistence, migration, retention, deletion, backup, import/export may change |
| `docs/SECURITY_MODEL.md` | Auth, permissions, secrets, trust boundaries, sensitive data, deletion, crypto may change |
| `docs/TESTING_STRATEGY.md` | Verification commands, test levels, test strategy may change |
| Durable decisions | Decisions are hard to reverse or surprising |

Before writing, confirm acceptance artifact weight:

- Full spec / PRD: `write-spec` Self-Review completed (Product Clarity + Domain Alignment) unless explicit accepted-risk record.
- Clear issue / review finding / approved user task: record acceptance source + Acceptance Brief Fields (canonical: Goal, Accepted Behavior, Acceptance Criteria, Non-Goals / Stop Conditions, Touched Surfaces, Edge And Error Cases, Docs / Test Impact, Risk Level, Required Reviews, Second Review, AFK / HITL Boundary — full definitions in `write-spec` Light Acceptance Brief). Chat-only request? Add `Approved Request Anchor` section with those fields + date.
- High-risk: consider `second-review`; required when High-Risk Surface (`security` / `data-loss` / `money` / `auth` / `crypto` / `deletion` / `core architecture` — canonical list in `second-review`).

If product goal / domain terms / acceptance criteria unclear, run `pressure-test` or `domain-modeling` first.

Accepted-risk records may skip a normal gate only with explicit user approval or approved plan. Record: skipped gate, reason, risk, compensating check, user acceptance, follow-up/expiry.

## Required Sections

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
- Acceptance Brief Fields (all 11 fields listed in Preconditions above).

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

When plan is revised because `spec-compliance-review` / `code-quality-review` found a plan-level flaw (wrong file boundary, missing task, weak verification), or user changed scope: update existing plan at same path. Do not create a new plan file. Address each finding, preserve unflagged tasks, re-run Plan Self-Review. See `using-bb-harness` Review Iteration Pattern.

## Planning Rules

- Keep plans compact. Link to acceptance artifact instead of restating.
- Map files before tasks. File boundaries shape the plan.
- Vertical slices. Avoid horizontal phases ("build DB", "build API", "build UI") unless slice is purely infrastructure.
- Each task independently verifiable.
- Behavior changes → TDD steps. No "write tests later".
- Exact commands where known.
- Expected failure and expected pass signals.
- Docs impact for domain, architecture, testing, security, user-facing behavior.
- Commit/stack strategy included, but do not authorize commit/push/PR/stack unless user or project-local instructions approved.
- Default per-task review: `spec-compliance-review` → `code-quality-review`. Plan only *additional* reviews — `security-review` when security surface touched, `second-review` when its Required / Strongly Consider rules apply.

## File Size Planning

Apply file/function size thresholds from `code-quality-review` (File And Complexity Thresholds). When a touched file is at/near 300/600 threshold, plan must include one of: scoped extraction before feature work, documented exception, or narrow edit + follow-up refactor issue.

## Self-Review

Walk this checklist before presenting. Plan correctness owned here, re-verified by `spec-compliance-review` + `code-quality-review` after implementation.

### Plan Hygiene

- Every acceptance requirement maps to a task or explicit non-goal.
- Every task has exact verification commands and expected RED / GREEN signals for TDD steps.
- No placeholder language ("TBD", "later", "appropriate error handling").
- New identifier names match `CONTEXT.md`.
- Plan does not copy large sections from acceptance artifact — links.
- Human can inspect plan without chat history.

### Architecture Soundness (SOLID upstream check)

When plan touches more than glue / CRUD code:

- **SRP**: each file in File Responsibility Map has one primary reason to change. Two unrelated concerns → split or revisit.
- **DIP**: domain / application code does not depend on framework, ORM, HTTP client, filesystem types. If it must, name port/adapter explicitly.
- **Dependency direction**: imports flow inward (UI / infra → application → domain). No domain file importing infrastructure.
- **File-size impact**: estimate per touched file. At/near 300/600 threshold → scoped extraction, documented exception, or follow-up refactor task.
- **Speculative abstraction**: no ports, interfaces, factories, strategy patterns for variation that does not yet exist.
- **Cross-cutting concerns**: logging, auth, persistence, caching at consistent boundaries, not sprinkled across domain code.

Glue, config, docs, scaffold-only: mark `N/A — non-architectural change` and skip.

### Domain Alignment

Same checks as `write-spec` Self-Review Domain Alignment when plan touches domain code. Do not re-list invariants resolved in spec; check plan respects them.

### Independent Review

Two options for a second pair of eyes:

- **`plan-document-reviewer-prompt.md`** (this dir) — same-host subagent re-reads plan, acceptance artifact, project docs independently. Use when:
  - Plan crosses module boundaries or changes dependency direction.
  - Many tasks or large file responsibility map.
  - High-Risk Surface (see `second-review`) touched.
  - Self-Review passed but uncertain about file mapping or verification commands.
- **`second-review`** (Codex by default) — different-model, fully-independent double-check. Required for High-Risk Surface; otherwise optional. Heavier than same-host reviewer.

Neither mandatory — Self-Review alone is default. Pick the one (or both) whose value justifies the time.

Otherwise next gates: `spec-compliance-review` and `code-quality-review` after each implemented slice.

## Output

- Plan path
- Slice count
- Highest-risk files
- Required reviews
- Recommended next command
- One next-phase question (e.g. start approved first slice?)
