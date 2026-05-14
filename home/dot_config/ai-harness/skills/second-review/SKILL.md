---
name: second-review
description: Use when running an independent double-check (Codex by default) on a spec, plan, diff, or security-sensitive change — catches what self-review and the first reviewer missed by reading artifacts in a fresh context.
---

# Second Review

Independent review, fresh context, different model when possible. Purpose: **catch what
self-review and the first reviewer missed**. Not a rubber stamp. Not a re-run of
`code-quality-review` by the same model.

## High-Risk Surfaces (Canonical)

Harness-wide canonical list. Other docs reference as "High-Risk Surfaces (see `second-review`)".

- security
- data-loss
- money
- auth
- crypto
- deletion
- core architecture

## Required When Available

Any of:

- Change touches a High-Risk Surface.
- User asks for independent double-check.
- Primary review passed but artifact crosses module boundaries primary could not fully inspect.

## Strongly Consider

**Two or more** triggers, or one trigger on a High-Risk Surface. Single trigger = optional.

- Diff is large, multi-module, hard to inspect, or accepts a 300/600-line file risk.
- Tests are weak, flaky, slow, expensive, or heavily mocked.
- Primary agent stuck or changed approach more than once.
- Bounded automation proposed for broad or user-facing work.
- Product direction, MVP boundary, persistence, sync, concurrency, external integrations, or
  broad architecture direction changes.

## Optional For Specs And Plans

Optional unless required criteria met. Authors may request from `write-spec` or `write-plan`
Self-Review.

## Procedure

Prefer in order:

1. Host agent's Codex integration (Claude Code Codex plugin, in-tool Codex command,
   project-specific Codex helper).
2. Separate clean Codex app session or Codex CLI in same repo.
3. Claude subagent with `second-reviewer` agent definition — *only* when Codex unavailable.
4. Human / manual review using same output format.

Codex is default. Record any fallback.

Reviewer reads artifacts, not chat:

- `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`, `docs/AGENT_WORKFLOW.md`
- Acceptance artifact, plan, primary review records, durable decisions
- Changed files or diff
- Test and verification evidence

## What The Independent Reviewer Looks For

Not duplicating `code-quality-review`. Focus:

- **Blind spots** primary reviewer shares with author (same model, framing, skim).
- **Acceptance gaps** primary accepted without challenge.
- **Architecture / boundary decisions** primary treated as given.
- **Test gaps** — coverage present but assertion weak.
- **Security / data-loss / money** paths where primary used "looks fine".
- **Plan vs reality drift** primary did not check against durable docs.

Agreeing with primary? Say so directly. List residual risk primary did not surface.

## Severity And Result

Same vocabulary as `code-quality-review`:

- **Critical (Must Fix)** — blocks shipping.
- **Important (Should Fix)** — fix before next phase.
- **Minor (Nice To Have)** — does not block.

Result: **Ready to merge: Yes / With fixes / No**.

Stop after two cycles in same phase if findings still surfacing — escalate. See
`using-bb-harness` Review Iteration Pattern.

## Fallback Record

If unavailable:

```text
Second review: unavailable
Reason: <why>
Compensating review: <self-review / focused reviewer subagent / human review>
Accepted risk: <what could be missed>
User accepted proceeding: <yes/no>
```

Do not approve Critical-risk work without explicit user acceptance when independent review is
unavailable.

## Scope Discipline

Stay inside the supplied artifact / diff. Same artifacts as the primary review, fresh eyes — do not expand scope or audit untouched code.

- Findings cite file:line in the diff or section:line in the artifact.
- No proposing new product behavior, new dependencies, or broad rewrites as required fixes.
- Out-of-scope hardening or improvements are Minor unless they expose a Critical defect in the touched path.
- YAGNI applies. Speculative future-proofing is Minor at best.

## Output

```text
## Strengths
- <specific observation>

## Findings missed by primary review
### Critical (Must Fix)
### Important (Should Fix)
### Minor (Nice To Have)

## Findings primary review caught (acknowledged)
- <brief; do not re-litigate>

## Result
- Ready to merge: Yes / With fixes / No
- Double-check verdict: primary review was complete / had gaps / requires re-run
- Residual risk:
```

Store substantial records in `docs/reviews/YYYY-MM-DD-<topic>-second-review.md`.
