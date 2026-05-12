---
name: second-review
description: Use when running an independent double-check (Codex by default) on a spec, plan, diff, or security-sensitive change — catches what self-review and the first reviewer missed by reading artifacts in a fresh context.
---

# Second Review

Run an independent review that does not inherit the primary agent's context. The purpose is
to **catch what self-review and the first reviewer missed** — same artifacts, fresh eyes,
different model when possible.

This is the harness's mechanism for "did the primary agent miss something?" It is not a
rubber stamp on prior findings and it is not a re-run of `code-quality-review` by the same
model.

## High-Risk Surfaces (Canonical)

This list is the harness-wide canonical definition. Other docs and skills reference it as
"High-Risk Surfaces (see `second-review`)" instead of re-listing.

- security
- data-loss
- money
- auth
- crypto
- deletion
- core architecture

## Required When Available

Use independent second review when any are true:

- The change touches a High-Risk Surface.
- The user explicitly asks for an independent double-check.
- A primary review (`spec-compliance-review`, `code-quality-review`, `security-review`)
  passed but the artifact crosses module boundaries the primary reviewer could not fully
  inspect.

## Strongly Consider

Treat second review as **strongly recommended** (not automatic) only when **two or more** of
the following triggers apply together, or one trigger touches a High-Risk Surface. A single
trigger in isolation is **optional**, not strongly recommended.

Triggers:

- Diff is large, multi-module, hard to inspect, or accepts a 300 / 600-line file risk.
- Tests are weak, flaky, slow, expensive, or heavily mocked.
- The primary agent is stuck or changed approach more than once.
- Bounded automation is proposed for broad or user-facing work.
- Product direction, MVP boundary, persistence, sync, concurrency, external integrations,
  or broad architecture direction changes.

## Optional For Specs And Plans

For specs and plans, `second-review` is optional unless the change meets the required
criteria above. The author can request it from `write-spec` Self-Review or `write-plan`
Self-Review when they want a second opinion before implementation.

## Procedure

Prefer, in order:

1. The host agent's Codex integration when available (Claude Code Codex plugin, in-tool
   Codex command, project-specific Codex helper).
2. A separate clean Codex app session or Codex CLI in the same repo.
3. A Claude subagent dispatched with the `second-reviewer` agent definition, *only* when
   Codex is unavailable.
4. Human / manual review using the same output format.

Codex is the default; substitute another reviewer only when Codex is unavailable and
record the fallback.

The reviewer must read artifacts, not only chat summaries:

- `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`, `docs/AGENT_WORKFLOW.md`
- Relevant acceptance artifact, plan, primary review records, durable decisions
- Changed files or diff
- Test and verification evidence

## What The Independent Reviewer Looks For

The independent reviewer is not duplicating `code-quality-review`. It focuses on:

- **Blind spots the primary reviewer shares with the primary author** (same model, same
  framing, same skim path).
- **Acceptance gaps** the primary review accepted without challenge.
- **Architecture / boundary decisions** the primary review treated as given.
- **Test gaps** where coverage looked present but the assertion was weak.
- **Security / data-loss / money** paths where the primary review used "looks fine".
- **Plan vs reality drift** the primary review did not check against the durable docs.

When the independent reviewer agrees with the primary review, say so directly and list any
residual risk the primary review did not surface.

## Severity And Result

Use the same vocabulary as `code-quality-review`:

- **Critical (Must Fix)** — blocks shipping.
- **Important (Should Fix)** — fix before next phase.
- **Minor (Nice To Have)** — does not block.

Result: **Ready to merge: Yes / With fixes / No**.

Stop after two cycles in the same phase if findings are still surfacing — escalate to the
user. See `using-bb-harness` Review Iteration Pattern.

## Fallback Record

If unavailable, record:

```text
Second review: unavailable
Reason: <why>
Compensating review: <self-review / focused reviewer subagent / human review>
Accepted risk: <what could be missed>
User accepted proceeding: <yes/no>
```

Do not approve Critical-risk work without explicit user acceptance when independent review
is unavailable.

## Output

Lead with strengths (briefly), then findings, then result and double-check summary.

```text
## Strengths
- <specific observation>

## Findings missed by primary review
### Critical
### Important
### Minor

## Findings primary review caught (acknowledged)
- <brief; do not re-litigate>

## Result
- Ready to merge: Yes / With fixes / No
- Double-check verdict: primary review was complete / had gaps / requires re-run
- Residual risk:
```

Store substantial records in `docs/reviews/YYYY-MM-DD-<topic>-second-review.md`.
