---
name: review-gate
description: Use when reviewing specs, plans, diffs, tests, architecture, docs, or before asking for an independent second review.
---

# Review Gate

Run focused reviews before expensive execution and before shipping. This skill makes second review explicit instead of optional.

## Review Levels

Every spec, non-trivial plan, substantial implementation diff, and bounded loop proposal gets a primary review first:

- self-review when the change is small and local
- reviewer subagent when the concern is architecture, tests, docs, or security
- manual human review when product judgment or taste is the main risk

Independent Codex review is a second review. It is additive, not a replacement for the primary review. Use it when risk triggers require it or when the user requests it.

## Review Types

Choose the review types that match the risk:

- Product/spec review: goal, users, MVP, non-goals, acceptance criteria.
- Domain review: vocabulary, bounded contexts, invariants, ADR candidates.
- Plan review: file responsibility, vertical slices, TDD steps, verification, docs impact.
- Architecture review: DDD, SOLID, boundaries, file size, module depth.
- Test review: behavior coverage, regression cases, brittle mocks, edge cases.
- Security review: secrets, auth, permissions, crypto, data exposure, destructive operations.
- Docs review: durable docs reflect decisions and behavior.
- Loop review: bounded goal, allowed scope, allowed autonomous actions, forbidden actions, iteration budget, verification gate, and stop conditions.
- Ship review: diff scope, tests, docs, residual risk.

## When Second Review Is Required

Request independent Codex review when available if any are true:

- Spec changes product direction or MVP boundary.
- Plan touches core architecture, domain model, persistence, auth, crypto, money, deletion, sync, or concurrency.
- Diff is large, multi-module, or hard to inspect in one screen.
- A source file exceeds 600 lines or a plan accepts a 300+ line responsibility risk.
- Tests are weak, expensive, flaky, or mostly mocked.
- The primary agent is stuck or has changed approach more than once.
- A bounded goal loop is proposed for broad, risky, or user-facing work.
- The user explicitly asks for second review.

## Independent Review Procedure

Use the strongest available independent path:

1. Claude Code Codex plugin, when available.
2. Separate clean Codex app session or Codex CLI in the same repo.
3. Human/manual review using this skill's output format.

The independent reviewer must read artifacts, not only the primary chat:

- `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`, and `docs/AGENT_WORKFLOW.md`
- relevant spec, plan, review notes, and ADRs
- diff, changed file list, or exact files under review
- test and verification evidence

If independent review is unavailable, record:

```text
Second review: unavailable
Reason: <why>
Compensating review: <self-review / reviewer subagent / human review>
Accepted risk: <what could be missed>
```

Do not approve P0/P1-risk work without explicit user acceptance when independent review is unavailable.

## Review Order

For plans:

1. Spec review exists or accepted risk is recorded
2. Spec coverage
3. Domain and architecture fit
4. File responsibility and slice size
5. TDD and verification
6. Docs impact
7. Codex second review if required

For diffs:

1. Scope and unintended changes
2. Correctness against spec
3. Tests and edge cases
4. Architecture and file size
5. Security/data safety
6. Docs sync
7. Codex second review if required

## Handling Review Feedback

When receiving review findings, do not apply them blindly:

1. Classify each finding as valid, likely valid, unclear, or invalid.
2. Verify valid findings against artifacts, code, tests, or docs before editing when practical.
3. Ask for clarification when a finding lacks enough evidence to fix safely.
4. Reject or narrow findings that conflict with the spec, domain model, architecture rules, or verified behavior, and record why.
5. Fix accepted findings with the smallest scoped change, preferably through `tdd-workflow` or a bounded goal loop when multiple findings are approved.
6. Rerun the relevant verification and update the review record with fixed, accepted-risk, or deferred status.

## Output Format

Lead with findings:

```text
Findings
- [P1] <issue>
  Impact:
  Evidence:
  Suggested fix:

Open Questions
- ...

Review Result
- Pass / Pass with follow-ups / Blocked
- Second review: required/not required, requested/not available
```

Severity:

- P0: ships broken, data loss, security exposure, destructive risk.
- P1: likely bug, architecture trap, missing critical test, spec mismatch.
- P2: maintainability, unclear docs, brittle test, medium risk.
- P3: cleanup or polish.

## Storing Review Records

For substantial work, store the review in:

```text
docs/reviews/YYYY-MM-DD-<topic>-<review-type>.md
```

Include:

- artifact reviewed
- reviewer type
- findings
- fixes applied or accepted risk
- verification after fixes

## Rules

- Do not bury findings under summaries.
- Do not approve plans with placeholders.
- Do not approve implementation without verification evidence.
- Do not let second review replace primary review; it is additive.
- If no issues are found, say that directly and list residual risk.
