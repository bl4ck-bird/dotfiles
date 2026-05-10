---
name: second-review
description: Use when requesting or recording an independent Codex review of a spec, plan, diff, security-sensitive change, broad refactor, or stuck debugging session.
---

# Second Review

Run an independent review after the primary review.

## High-Risk Surfaces (canonical)

This list is the harness-wide canonical definition. Other docs and skills reference it as
"High-Risk Surfaces (see `second-review`)" instead of re-listing the items.

- security
- data-loss
- money
- auth
- crypto
- deletion
- core architecture

## Required When Available

Use independent second review when any are true:

- the change touches a High-Risk Surface
- the user explicitly asks

## Strongly Consider

Treat second review as **strongly recommended** (not automatic) only when **two or more** of the
following triggers apply together, or one trigger touches a High-Risk Surface. A single trigger in
isolation is **optional**, not strongly recommended.

Triggers:

- diff is large, multi-module, hard to inspect, or accepts a 300/600-line file risk
- tests are weak, flaky, slow, expensive, or heavily mocked
- the primary agent is stuck or changed approach more than once
- bounded automation is proposed for broad or user-facing work
- product direction, MVP boundary, persistence, sync, concurrency, external integrations, or broad
  architecture direction changes

## Optional For Specs And Plans

For specs and plans, `second-review` is optional unless the change meets the required criteria
above. The primary `spec-review` or `plan-review` may pass with a recommendation to get independent
Codex review before implementation or before ship.

## Procedure

Prefer, in order:

1. The host agent's Codex integration when available (for example a Claude Code Codex plugin, an
   in-tool Codex command, or a project-specific Codex helper).
2. A separate clean Codex app session or Codex CLI in the same repo.
3. Human/manual review using the same output format.

Codex is the default; substitute another reviewer only when Codex is unavailable and record the
fallback. The reviewer must read artifacts, not only chat summaries:

- `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`, `docs/AGENT_WORKFLOW.md`
- relevant acceptance artifact, plan, review records, durable decisions, and changed files or diff
- test and verification evidence

## Fallback Record

If unavailable, record:

```text
Second review: unavailable
Reason: <why>
Compensating review: <self-review / focused reviewer subagent / human review>
Accepted risk: <what could be missed>
User accepted proceeding: <yes/no>
```

Do not approve P0/P1-risk work without explicit user acceptance when independent review is
unavailable.

## Output

Store substantial records in `docs/reviews/YYYY-MM-DD-<topic>-second-review.md`.
