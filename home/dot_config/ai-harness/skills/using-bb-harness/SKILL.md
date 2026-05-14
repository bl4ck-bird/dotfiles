---
name: using-bb-harness
description: Use when starting any session before non-trivial work — checks the repo for BB Harness markers and routes to the right phase. Falls back to standard agent behavior when the repo does not reference the harness, so it is safe to invoke universally.
---

# Using BB Harness

Universal entry point. Invoke at every session start. If repo references BB Harness, route to right phase. If not, self-disable in one line; agent proceeds with standard behavior.

## Bootstrap Rule

Session start, before non-trivial work:

1. Check repo root for BB Harness markers:
   - `AGENTS.md`, `CLAUDE.md`, or `docs/AGENT_WORKFLOW.md` that **mentions BB Harness or uses BB skill names** (`using-bb-harness`, `subagent-driven-development`, `code-quality-review`, etc.).
2. **Markers present** — read nearest `AGENTS.md` / `CLAUDE.md`, then proceed to Start or invoke the directly matching skill (e.g. `bug-diagnosis` for a bug, `test-driven-development` for small behavior change).
3. **Markers absent** — report once: "BB Harness not in this repo. Proceeding with standard agent behavior." Skip rest. Do not force BB workflow on non-adopters.
4. Trivial questions and pure-conversation replies may skip bootstrap.

Cheap when BB absent (single grep / file-existence check). Only reliable way to make BB repos get the right workflow without user typing skill name every session.

## Skill-First Rule

- Start with `using-bb-harness` when current phase unclear.
- Task matches a skill directly → use that skill, don't rephrase its procedure in chat.
- Use next relevant skill at each phase boundary.
- Smallest set of skills that materially protects the work.
- If a relevant skill is skipped for small/local task, state reason briefly.

## Start

1. Read nearest `AGENTS.md` or `CLAUDE.md`.
2. If present, read `CONTEXT.md`, `docs/CURRENT.md`, `docs/AGENT_WORKFLOW.md`, active acceptance artifact, plan, recent review or handoff note.
3. Check available skills for direct match before choosing execution path.
4. Summarize: current goal, workflow weight, missing decisions/artifacts, next safe action.

If key context missing, ask or propose minimal recovery step. Do not invent product, domain, architecture, or safety decisions.

## Evidence Gate

- Trivial edits: inspect target file + adjacent context before editing.
- Behavior / API / dependency / data / security / infrastructure changes: trace execution path, call sites, constraints, regression surface first.
- Next action would change behavior, API/UX, naming, persistence, auth, dependency, config, compatibility, product scope, domain language outside approved plan → ask first.

## Workflow Weight

| Weight | Trigger | Default path |
| --- | --- | --- |
| Tiny / local | One bounded module, ≤ 50 LoC, no product / domain / API / data / security decision, no new test target | Direct edit or `test-driven-development` + `ship-check` |
| Scope review | 3+ files, uncertain blast radius, unclear module boundary | Decide if small path still fits; record bounded scope |
| Non-trivial | Product behavior, user workflow, domain language, public API, persistence, auth, sync, deletion, external integration | Reviewed acceptance artifact (via `write-spec` Self-Review) + compact plan (via `write-plan` Self-Review) + per-task `spec-compliance-review` + `code-quality-review` + docs gates |
| Risky / substantial | Module boundary or dependency-direction change, refactor crossing 2+ modules, weak tests, 5+ files, 2+ modules, 300/600-line file thresholds, or any High-Risk Surface (`security` / `data-loss` / `money` / `auth` / `crypto` / `deletion` / `core architecture` — canonical list in `second-review`) | Above + `security-review` when triggered + `second-review` required for High-Risk Surface or boundary / dependency-direction change |

## Acceptance Artifact

Non-trivial work needs reviewed acceptance artifact (spec, PRD, issue, review finding, approved task) before implementation. Use `write-spec` for new specs — its Self-Review owns product clarity and domain alignment. Acceptance Brief Fields (canonical: Goal, Accepted Behavior, Acceptance Criteria, Non-Goals / Stop Conditions, Touched Surfaces, Edge And Error Cases, Docs / Test Impact, Risk Level, Required Reviews, Second Review, AFK / HITL Boundary — full definitions in `write-spec` Light Acceptance Brief).

- Full `docs/specs/` spec: when product scope / domain language / public API / data / storage / auth / security / deletion / sync / external integrations / user workflow still being decided.
- Already-clear task: issue / review finding / approved request enough when it meets canonical fields. Chat-only → plan must capture them in Approved Request Anchor.
- Accepted-risk exceptions may skip a normal gate only with explicit user acceptance. Record: skipped gate, reason, risk, compensating check, user acceptance, follow-up/expiry.

## Review Channels

Harness uses **five** review channels. Upstream ones (spec/plan correctness) live in authoring skills as Self-Review. Implementation-time reviews run as fresh subagents from `subagent-driven-development`.

| Channel | Owner | When |
| --- | --- | --- |
| Spec Self-Review | `write-spec` | Before declaring an acceptance artifact ready. Domain alignment, vertical slice quality. |
| Plan Self-Review | `write-plan` | Before presenting a plan. SOLID, file boundary, file-size impact. |
| `spec-compliance-review` | reviewer subagent | After each implemented slice. Binary ✅ / ❌. |
| `code-quality-review` | reviewer subagent | After spec-compliance passes. Code quality, DDD / SOLID, file-size, tests, durable docs drift. Ready to merge? Yes / With fixes / No. |
| `security-review` | reviewer subagent | Follow-on from `code-quality-review` when security surface touched, or directly when slice is known security-heavy. |
| `second-review` | different-model agent | High-Risk Surface, explicit double-check request, or boundary / dependency-direction change. |
| `receiving-review` | authoring skill | Whenever a reviewer returns findings, before applying fixes. |

`docs-sync` and `ship-check` are workflow gates, not reviews.

## Review Rules

Iteration, stop conditions, recommendations, severity definitions live in companion files:

- `review-rules.md` — Review Iteration Pattern, Result Contract, Chain Depth Cap (1 automatic follow-on), Scope Guard, "plan needs revision" handoff, receiving-feedback ordering. **Hard stop after 2 cycles** here.
- `severity-definitions.md` — Critical / Important / Minor with examples, Untouched-Code Rule, "do not promote" guidance.

Other review skills and `claude-agents/*-reviewer.md` reference these companions as SSOT. Do not duplicate.

Quick recap:

- spec-compliance: binary ✅ / ❌.
- code-quality / security / second: Ready to merge **Yes / With fixes / No**.
- Hard stop after **2** review-fix cycles per channel — escalate, no auto third cycle.
- Findings outside touched surface default to **Minor** unless change makes them unsafe.
- At most **1** automatic follow-on review per channel; `second-review` exempt when Required When Available criteria met.

## Execution Model

- Small / local behavior change: `test-driven-development` then `ship-check`.
- Reviewed multi-task plan, host supports subagents: `subagent-driven-development` as controller; each task = fresh implementer subagent + `spec-compliance-review` + `code-quality-review`.
- Reviewed plan, host cannot dispatch subagents, or only 1-3 small tasks where dispatch overhead not worth it: `executing-plans-inline`. Same review gates as skill invocations against main agent's diff. Switch back to subagent-driven mid-plan if self-review weakens.
- Workspace isolation for multi-task execution: `using-git-worktrees`.
- Controller does not pause between tasks unless Required User Checkpoint applies (see `subagent-driven-development`).

## Branch Policy

**Never start implementation on a protected base branch** without explicit user consent. Default protected set: `main`, `master`, `develop`, `trunk`, plus any branch the repo's `AGENTS.md` / `CLAUDE.md` names as base.

- **Before the first code edit** in a session, check `git branch --show-current`. On a protected branch → invoke `using-git-worktrees` and create a feature branch / worktree first. This applies regardless of Workflow Weight — Tiny/local is not an excuse to commit directly to a protected branch.
- **Exceptions** require explicit user consent in this session ("yes, edit main directly", "this is a hotfix on main"). Record the exception briefly in the response. Project-local instructions that authorize direct base-branch work also count as consent.
- **Read-only work** (questions, investigation, doc-only navigation without edits) does not trigger this policy.
- **Branch name**: derive from the task — `<type>/<short-slug>` (e.g. `fix/vscode-comment-newline`, `feat/branch-policy`). Match the project's existing convention when one is visible in `git log` / `git branch -a`.
- **At finish time**: `ship-check` Finishing Options presents merge / push+PR / keep / discard. Do not silently commit-and-push from a feature branch without going through that gate.

Implementation skills (`test-driven-development`, `executing-plans-inline`, `subagent-driven-development`) restate this as a precondition so the rule is in context when work actually starts.

**Callsites that inline the protected-branch list** (per README Cross-Reference Inlining Policy — keep in sync when editing): `test-driven-development/SKILL.md` (Branch Precondition), `executing-plans-inline/SKILL.md` (Workspace Isolation), `subagent-driven-development/SKILL.md` (Workspace Isolation), `using-git-worktrees/SKILL.md` (When To Use).

## Routing

Choose next phase, not entire lifecycle:

| Situation | Next skill |
| --- | --- |
| New or unscaffolded repo | `project-scaffold` |
| Product brainstorming, goal, MVP, users, non-goals unclear | `product-discovery` |
| Idea, spec, or plan needs pressure testing | `pressure-test` |
| Domain terms, contexts, invariants, hard-to-reverse decisions unclear | `domain-modeling` |
| Goal clear but no acceptance artifact or slices | `write-spec` |
| Acceptance artifact ready, implementation path unclear | `write-plan` |
| Reviewed plan has multiple tasks, host supports subagents | `subagent-driven-development` |
| Reviewed plan, host cannot dispatch subagents or 1-3 small tasks | `executing-plans-inline` |
| Small behavior change or single implementation task | `test-driven-development` |
| Isolated worktree needed before execution | `using-git-worktrees` |
| 2+ independent investigations / bug repros / read-only research that can run concurrently | `dispatching-parallel-agents` |
| Bug, flaky test, regression | `bug-diagnosis` |
| Verifying a completion claim ("done", "fixed", "passes") with fresh evidence | `verification-before-completion` |
| Verifying implementation matches acceptance | `spec-compliance-review` |
| Reviewing implementation quality / architecture / tests / docs | `code-quality-review` |
| Security / data-loss / destructive / auth / secrets / crypto / untrusted-input risk | `security-review` |
| Independent double-check required or requested | `second-review` |
| Receiving review feedback, before applying fixes | `receiving-review` |
| Behavior / architecture / testing / security / workflow changed | `docs-sync` |
| Work ready to hand off, commit, PR, release | `ship-check` |
| Commit / stack / PR / release action approved | `ship-check` then commit / stack gate |
| User approved repeated autonomous progress | `bounded-loop` |

## Phase Loop

After each phase:

1. Record/update durable artifact for that phase when work non-trivial.
2. Update `docs/CURRENT.md` only when active phase, acceptance artifact/source, plan, blocker, completed slice, verification evidence, or next action materially changes.
3. Run narrowest useful verification or explain why none applies.
4. Decide: continue, ask user, clear context after handoff, or stop.
5. Recommend one next phase. Two paths equally valid → present at most one alternative.
6. Do not advance when approval required for git setup, dependency execution, hooks, deletion, commit/stack actions, history rewrite, broad scope expansion, or unresolved product/domain/architecture decisions.

## Continuation

After each phase, recommend exactly one next phase, ask concise confirmation in user's language (Korean default per global `AGENTS.md`). If user already approved end-to-end bounded goal, continue inside approved scope and stop conditions instead of asking after every safe phase.

## Parallel Work

- Scope in main agent first. Don't delegate before reading enough artifacts to split work clearly.
- Parallel tool calls for small independent reads/searches.
- Subagents for substantial independent tracks with distinct concerns and clear return formats.
- Single focused reviewer subagent OK for named review concern; exploratory batches usually have 2+ independent tracks.

## Context Control

- Load only the skill needed for current phase.
- Artifact paths over chat summaries.
- Write handoff before clearing after discovery/spec, plan approval, several implementation tasks, or review fixes.
- New sessions resume from `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`, `docs/AGENT_WORKFLOW.md`, active acceptance artifact/plan, recent reviews, relevant code.

## Output

Return: context read, workflow weight, selected next skill, current and next recommended phase, required artifact or approval, next safe action.
