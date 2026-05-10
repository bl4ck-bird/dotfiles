---
name: bb-workflow
description: Use when starting, resuming, or routing side-project work through the BB Harness before choosing specific workflow skills.
---

# BB Workflow

Entry point for agent work. Selects the lightest sufficient workflow, names the next skill, and
prevents loading every process at once.

## Skill-First Rule

- Start with `bb-workflow` when the current phase is unclear, a session is starting/resuming, or
  work may be non-trivial.
- If the task directly matches a skill, use that skill instead of rephrasing its procedure in chat.
- Use the next relevant skill at each phase boundary.
- Choose the smallest set of skills that materially protects the work.
- If a relevant skill is skipped for a small/local task, state the reason briefly.

## Start

1. Read the nearest `AGENTS.md` or `CLAUDE.md`.
2. If present, read `CONTEXT.md`, `docs/CURRENT.md`, `docs/AGENT_WORKFLOW.md`, the active acceptance
artifact, plan, and recent review or handoff note.
3. Check available skills for a direct match before choosing the execution path.
4. Summarize only: current goal, workflow weight, missing decisions or artifacts, next safe action.

If key context is missing, ask for it or propose a minimal recovery step. Do not invent product,
domain, architecture, or safety decisions.

## Evidence Gate

- Trivial edits: inspect the target file and adjacent context before editing.
- Behavior, API, dependency, data, security, or infrastructure changes: trace execution path, call
  sites, constraints, and regression surface first.
- If the next action would change behavior, API/UX, naming, persistence, auth, dependency, config,
  compatibility, product scope, or domain language outside an approved plan, ask first.

## Workflow Weight

| Weight | Trigger | Default path |
| --- | --- | --- |
| Tiny/local | One bounded module, no product/domain/API/data/security decision | Direct edit or `behavior-tdd` + `ship-check` |
| Scope review | 3+ files, uncertain blast radius, unclear module boundary | Decide if small path still fits; record bounded scope |
| Non-trivial | Product behavior, user workflow, domain language, public API, persistence, auth, sync, deletion, external integration | Reviewed acceptance artifact + compact plan + focused reviews + docs gates |
| Risky/substantial | Module boundary or dependency-direction change, refactor crossing 2+ modules, weak tests, 5+ files, 2+ modules, 300/600-line file thresholds, or any High-Risk Surface (see `second-review`) | Required focused review + `second-review` when a High-Risk Surface is touched, or for boundary/dependency-direction change |

## Acceptance Artifact

Non-trivial work needs a reviewed acceptance artifact (spec, PRD, issue, review finding, or
approved task) before implementation. The Acceptance Brief Fields (see `write-spec`) are the
canonical field set; do not duplicate them here.

- Use a full `docs/specs/` spec when product scope, domain language, public API, data/storage,
  auth/security, deletion, sync, external integrations, or user workflow is still being decided.
- For an already-clear task, an issue/review finding/approved request can be enough when it meets
  the canonical fields. If it only exists in chat, the plan must capture them in an Approved
  Request Anchor.
- Accepted-risk exceptions may skip a normal gate only with explicit user acceptance. Record:
  skipped gate, reason, risk, compensating check, user acceptance, follow-up/expiry.

## Review Routing

Call a review skill only when the trigger signal in the left column is present in the touched
surface.

| Trigger signal (only call when present) | Skill |
| --- | --- |
| Spec/PRD or unclear acceptance criteria | `spec-review` |
| Non-trivial or multi-step plan before execution | `plan-review` (required) |
| Substantial slice or review-fix pass | `implementation-review` |
| Weak/flaky/heavily-mocked/acceptance-critical tests | `test-review` |
| Boundary, DDD, SOLID, file-size, over-abstraction signal | `architecture-review` |
| Auth, secrets, crypto, deletion, sensitive data, untrusted input, injection, SSRF touched | `security-review` |
| Durable docs touched or suspected drift | `docs-review` |
| Any High-Risk Surface (see `second-review`) | `second-review` (required) |
| Independent second review explicitly requested | `second-review` |

### Review Chain Depth Cap

A focused review may automatically recommend at most **one** follow-on review (e.g.
`implementation-review` → `architecture-review`). A second hop (e.g. `architecture-review` →
`security-review`) requires user confirmation. This stops review chains from inflating into
"review of review of review" loops on small/medium work.

`second-review` is exempt from the cap when its Required When Available criteria are met.

## Execution Model

- Small/local behavior change: `behavior-tdd` then `ship-check`.
- Reviewed multi-slice plan: `execute-plan` as controller; each behavior-changing slice uses
  `behavior-tdd`.
- Worker/subagent: delegate one vertical slice or disjoint write scope. Controller inspects for
  acceptance compliance and code quality; run focused or second review when result is substantial,
  risky, hard to inspect, weakly verified, or required by the plan.

## Routing

Choose the next phase, not the entire lifecycle:

| Situation | Next skill |
| --- | --- |
| New or unscaffolded repo | `project-scaffold` |
| Product brainstorming, goal, MVP, users, non-goals unclear | `product-discovery` |
| Idea, spec, or plan needs pressure testing | `pressure-test` |
| Domain terms, contexts, invariants, hard-to-reverse decisions unclear | `domain-modeling` |
| Goal clear but no acceptance artifact or slices | `write-spec` |
| Spec/PRD exists but primary review missing | `spec-review` |
| Acceptance artifact reviewed, implementation path unclear | `write-plan` |
| Non-trivial/multi-step plan exists, plan review missing | `plan-review` |
| Reviewed plan has multiple slices | `execute-plan` (includes Workspace Isolation guidance) |
| Small behavior change or implementation task | `behavior-tdd` |
| Bug, flaky test, regression | `bug-diagnosis` |
| Tests may not prove accepted behavior | `test-review` |
| Architecture/DDD/SOLID/file-size concern | `architecture-review` |
| Completed slice/diff/test quality needs review | `implementation-review` |
| Security/data-loss/destructive/auth/secrets/crypto/untrusted-input risk | `security-review` |
| Durable docs or handoff may be stale | `docs-review` |
| Independent second review required or requested | `second-review` |
| Behavior/architecture/testing/security/workflow changed | `docs-sync` |
| Work ready to hand off, commit, PR, release | `ship-check` |
| Commit/stack/PR/release action approved | `ship-check` then commit/stack gate |
| User approved repeated autonomous progress | `bounded-loop` |

## Phase Loop

After each phase:

1. Record or update the durable artifact for that phase when work is non-trivial.
2. Update `docs/CURRENT.md` only when active phase, acceptance artifact/source, plan, blocker,
   completed slice, verification evidence, or next action materially changes. Update once at end
   of phase, not after every small step.
3. Run the narrowest useful verification or explain why none applies.
4. Decide one of: continue to next skill, ask the user, clear context after handoff, or stop.
5. Recommend one next phase. If two paths are equally valid, present at most one alternative for
   confirmation. Ask a concise confirmation rather than making the user remember the next skill.
6. Do not advance when approval is required for git setup, dependency execution, hooks, deletion,
   commit/stack actions, history rewrite, broad scope expansion, or unresolved
   product/domain/architecture decisions.

## Continuation

After each phase, recommend exactly one next phase and ask a concise confirmation question. Phrase
it naturally in the user's language (the global `AGENTS.md` Korean default applies unless the user
asks otherwise). If the user already approved an end-to-end bounded goal, continue inside the
approved scope and stop conditions instead of asking after every safe phase.

## Parallel Work

- Scope in the main agent first. Do not delegate before reading enough artifacts to split the work
  clearly.
- Use parallel tool calls for small independent reads or searches.
- Use subagents for substantial independent tracks with distinct concerns and clear return formats.
- A single focused reviewer subagent is acceptable for a named review concern; exploratory batches
  should usually have two or more independent tracks.
- Do not send data already in main-agent context to subagents only for formatting or summarizing.

## Context Control

- Load only the skill needed for the current phase.
- Prefer artifact paths over chat summaries.
- Write a handoff before clearing after discovery/spec, plan approval, several implementation
  slices, or review fixes.
- New sessions resume from `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`, `docs/AGENT_WORKFLOW.md`,
  active acceptance artifact/plan, recent reviews, and relevant code.

## Output

Return: context read, workflow weight, selected next skill, current and next recommended phase,
required artifact or approval, next safe action.
