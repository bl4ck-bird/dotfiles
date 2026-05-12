---
name: using-bb-harness
description: Use when starting any session before non-trivial work — checks the repo for BB Harness markers and routes to the right phase. Falls back to standard agent behavior when the repo does not reference the harness, so it is safe to invoke universally.
---

# Using BB Harness

Universal entry point. Invoke at every session start. If the repo references the BB
Harness, route to the right phase. If not, this skill self-disables with a one-line
note and the agent proceeds with standard behavior.

## Bootstrap Rule

At the start of any session, before non-trivial work:

1. Check the repo root for BB Harness markers:
   - `AGENTS.md`, `CLAUDE.md`, or `docs/AGENT_WORKFLOW.md` that **mentions BB Harness
     or uses BB skill names** (`using-bb-harness`, `subagent-driven-development`,
     `code-quality-review`, etc.).
2. **If markers present** — read the nearest `AGENTS.md` or `CLAUDE.md`, then proceed
   to Start (below) or invoke the directly matching skill when the task obviously
   maps to one (e.g., `bug-diagnosis` for a bug, `test-driven-development` for a
   small behavior change).
3. **If markers absent** — report once: "BB Harness not in this repo. Proceeding with
   standard agent behavior." Skip the rest of this skill. Do not force BB workflow
   on projects that did not adopt it.
4. Trivial questions and pure-conversation replies may skip the bootstrap check
   entirely.

This bootstrap is **cheap when BB is absent** (a single grep / file-existence check)
and is the only reliable way to make sure BB-using repos get the right workflow
without the user typing the skill name every session.

## Skill-First Rule

- Start with `using-bb-harness` when current phase is unclear.
- If the task directly matches a skill, use that skill instead of rephrasing its procedure
  in chat.
- Use the next relevant skill at each phase boundary.
- Choose the smallest set of skills that materially protects the work.
- If a relevant skill is skipped for a small / local task, state the reason briefly.

## Start

1. Read the nearest `AGENTS.md` or `CLAUDE.md`.
2. If present, read `CONTEXT.md`, `docs/CURRENT.md`, `docs/AGENT_WORKFLOW.md`, the active
   acceptance artifact, plan, and recent review or handoff note.
3. Check available skills for a direct match before choosing the execution path.
4. Summarize only: current goal, workflow weight, missing decisions or artifacts, next safe
   action.

If key context is missing, ask for it or propose a minimal recovery step. Do not invent
product, domain, architecture, or safety decisions.

## Evidence Gate

- Trivial edits: inspect the target file and adjacent context before editing.
- Behavior, API, dependency, data, security, or infrastructure changes: trace execution
  path, call sites, constraints, and regression surface first.
- If the next action would change behavior, API / UX, naming, persistence, auth,
  dependency, config, compatibility, product scope, or domain language outside an approved
  plan, ask first.

## Workflow Weight

| Weight | Trigger | Default path |
| --- | --- | --- |
| Tiny / local | One bounded module, ≤ 50 LoC, no product / domain / API / data / security decision, no new test target | Direct edit or `test-driven-development` + `ship-check` |
| Scope review | 3+ files, uncertain blast radius, unclear module boundary | Decide if small path still fits; record bounded scope |
| Non-trivial | Product behavior, user workflow, domain language, public API, persistence, auth, sync, deletion, external integration | Reviewed acceptance artifact (via `write-spec` Self-Review) + compact plan (via `write-plan` Self-Review) + per-task `spec-compliance-review` + `code-quality-review` + docs gates |
| Risky / substantial | Module boundary or dependency-direction change, refactor crossing 2+ modules, weak tests, 5+ files, 2+ modules, 300 / 600-line file thresholds, or any High-Risk Surface (see `second-review`) | Above + `security-review` when triggered + `second-review` required for High-Risk Surface or boundary / dependency-direction change |

## Acceptance Artifact

Non-trivial work needs a reviewed acceptance artifact (spec, PRD, issue, review finding, or
approved task) before implementation. Use `write-spec` for new specs (its Self-Review
replaces the former `spec-review` skill). The Acceptance Brief Fields (see `write-spec`)
are the canonical field set.

- Use a full `docs/specs/` spec when product scope, domain language, public API,
  data / storage, auth / security, deletion, sync, external integrations, or user workflow
  is still being decided.
- For an already-clear task, an issue / review finding / approved request can be enough
  when it meets the canonical fields. If it only exists in chat, the plan must capture
  them in an Approved Request Anchor.
- Accepted-risk exceptions may skip a normal gate only with explicit user acceptance.
  Record: skipped gate, reason, risk, compensating check, user acceptance,
  follow-up / expiry.

## Review Channels

The harness uses **five** review channels. The upstream ones (spec / plan correctness)
live inside their authoring skills as Self-Review. Implementation-time reviews run as
fresh subagents from `subagent-driven-development`.

| Channel | Owner | When |
| --- | --- | --- |
| Spec Self-Review | `write-spec` | Before declaring an acceptance artifact ready. Domain alignment, vertical slice quality. |
| Plan Self-Review | `write-plan` | Before presenting a plan. SOLID, file boundary, file-size impact. |
| `spec-compliance-review` | reviewer subagent | After each implemented slice. Binary ✅ / ❌. |
| `code-quality-review` | reviewer subagent | After spec-compliance passes. Code quality, DDD / SOLID, file-size, tests, durable docs drift. Ready to merge? Yes / No / With fixes. |
| `security-review` | reviewer subagent | Follow-on from `code-quality-review` when security surface touched, or directly when slice is known security-heavy. |
| `second-review` | Codex (default) | High-Risk Surface, explicit double-check request, or boundary / dependency-direction change. |
| `receiving-review` | authoring skill | Whenever a reviewer returns findings, before applying fixes. |

`docs-sync` and `ship-check` are workflow gates, not reviews.

## Review Rules

How reviews iterate, when they stop, what they may recommend, and severity
definitions live in two companion files in this directory:

- `review-rules.md` — Review Iteration Pattern, Result Contract, Chain Depth Cap (1
  automatic follow-on), Scope Guard, "plan needs revision" handoff, receiving-feedback
  ordering. **Hard stop after 2 cycles** is here.
- `severity-definitions.md` — Critical / Important / Minor with concrete examples,
  Untouched-Code Rule, "do not promote" guidance, P0-P3 legacy mapping.

Other review skills and `claude-agents/*-reviewer.md` reference these companions as
the SSOT. Do not duplicate the definitions in calling skills.

Quick recap (full rules in the companion files):

- spec-compliance: binary ✅ / ❌.
- code-quality / security / second: Ready to merge **Yes / With fixes / No**.
- Hard stop after **2** review-fix cycles per channel — escalate to user, do not
  auto-run a third cycle.
- Findings outside the touched surface default to **Minor** unless the change makes
  them unsafe.
- At most **1** automatic follow-on review per channel; `second-review` is exempt
  when its Required-When-Available criteria are met.

## Execution Model

- Small / local behavior change: `test-driven-development` then `ship-check`.
- Reviewed multi-task plan, host supports subagents: `subagent-driven-development` as
  controller; each task runs in a fresh implementer subagent + `spec-compliance-review` +
  `code-quality-review`.
- Reviewed plan, host cannot dispatch subagents or plan has only 1-3 small tasks where
  dispatch overhead is not worth it: `executing-plans-inline`. Same review gates, run as
  skill invocations against the main agent's diff. Switch back to subagent-driven mid-plan
  if self-review weakens.
- Workspace isolation for any multi-task execution: `using-git-worktrees`.
- The controller does not pause for confirmation between tasks unless a Required User
  Checkpoint applies (see `subagent-driven-development`).

## Routing

Choose the next phase, not the entire lifecycle:

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

1. Record or update the durable artifact for that phase when work is non-trivial.
2. Update `docs/CURRENT.md` only when active phase, acceptance artifact / source, plan,
   blocker, completed slice, verification evidence, or next action materially changes.
3. Run the narrowest useful verification or explain why none applies.
4. Decide: continue to next skill, ask the user, clear context after handoff, or stop.
5. Recommend one next phase. If two paths are equally valid, present at most one
   alternative for confirmation.
6. Do not advance when approval is required for git setup, dependency execution, hooks,
   deletion, commit / stack actions, history rewrite, broad scope expansion, or unresolved
   product / domain / architecture decisions.

## Continuation

After each phase, recommend exactly one next phase and ask a concise confirmation in the
user's language (Korean default per global `AGENTS.md`). If the user already approved an
end-to-end bounded goal, continue inside the approved scope and stop conditions instead of
asking after every safe phase.

## Parallel Work

- Scope in the main agent first. Do not delegate before reading enough artifacts to split
  the work clearly.
- Use parallel tool calls for small independent reads or searches.
- Use subagents for substantial independent tracks with distinct concerns and clear return
  formats.
- A single focused reviewer subagent is acceptable for a named review concern; exploratory
  batches should usually have two or more independent tracks.

## Context Control

- Load only the skill needed for the current phase.
- Prefer artifact paths over chat summaries.
- Write a handoff before clearing after discovery / spec, plan approval, several
  implementation tasks, or review fixes.
- New sessions resume from `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`,
  `docs/AGENT_WORKFLOW.md`, active acceptance artifact / plan, recent reviews, and
  relevant code.

## Output

Return: context read, workflow weight, selected next skill, current and next recommended
phase, required artifact or approval, next safe action.
