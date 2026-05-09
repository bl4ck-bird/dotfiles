---
name: bb-workflow
description: Use when starting, resuming, or routing side-project work through the BB Harness before choosing specific workflow skills.
---

# BB Workflow

Use this as the entry point for agent work. It selects the lightest sufficient workflow, names the
next skill to use, and prevents loading every process at once.

## Skill-First Rule

When the BB Harness is in use, prefer using the harness skills over ad-hoc process. Skills are the
executable workflow surface, not background reading.

- Start with `bb-workflow` when the current phase is unclear, a session is starting/resuming, or
  work may be non-trivial.
- If the task directly matches a skill, use that skill instead of rephrasing its procedure in chat.
- Use the next relevant skill at each phase boundary: discovery, pressure-test, domain-modeling,
  acceptance artifact, review, plan, execution, docs-sync, or ship-check.
- Do not load every skill just because the harness exists. Choose the smallest set that materially
  protects the work.
- If a relevant skill is skipped for a small/local task, state the reason briefly.

## Start

1. Read the nearest `AGENTS.md` or `CLAUDE.md`.
2. If present, read `CONTEXT.md`, `docs/CURRENT.md`, `docs/AGENT_WORKFLOW.md`, the active acceptance
artifact, plan, and recent review or handoff note.
3. Check available skills for a direct match before choosing the execution path.
4. Summarize only:
   - current goal
   - workflow weight
   - missing decisions or artifacts
   - next safe action

If key context is missing, ask for it or propose a minimal recovery step. Do not invent product,
domain, architecture, or safety decisions.

## Evidence Gate

- For trivial edits, inspect the target file and adjacent context before editing.
- For behavior, API, dependency, data, security, or infrastructure changes, trace the execution
  path, call sites, constraints, and regression surface first.
- If the next action would change behavior, API or UX, naming, persistence, auth, dependency,
  config, compatibility, product scope, or domain language outside an approved plan, ask before
  continuing.

## Workflow Weight

- Tiny/local: one bounded component or module, no product/domain/API/data/security
  decision. Tests, styles, fixtures, or docs supporting the same bounded change may stay
  on the small path. Use direct edit or `behavior-tdd` plus `ship-check`.
- Scope review: three or more files, uncertain blast radius, or unclear module boundary.
  Decide whether the small path still fits. If it does, record the bounded scope, files,
  unchanged product/API/data/security decisions, verification, and docs impact.
- Non-trivial: product behavior, user workflow, domain language, public API, persistence,
  auth/security, sync/concurrency, deletion, or external integration. Use a reviewed
  acceptance artifact, compact plan, focused reviews, and docs gates.
- Risky/substantial: core architecture, money, crypto, data loss, auth, deletion, broad
  refactor, weak tests, five or more files, two or more modules, or 300/600-line file
  thresholds. Require the relevant focused review. Require `second-review` for high-risk
  security/data-loss/money/auth/crypto/deletion/core-architecture work when available;
  consider it for large diffs, weak tests, or hard-to-inspect work.

## Acceptance Artifact

Before implementation, non-trivial work needs one artifact accepted or reviewed at the right weight
that says what behavior is being built and how it will be accepted. This may be:

- a feature spec in `docs/specs/`
- a clear issue, PRD, review finding, or user-approved task with testable acceptance criteria

For non-trivial work, the artifact must meet the canonical Acceptance Brief fields.

The canonical Acceptance Brief fields are:

- Goal
- Accepted Behavior
- Acceptance Criteria
- Non-Goals / Stop Conditions
- Touched Surfaces
- Edge And Error Cases
- Docs / Test Impact
- Risk Level
- Required Reviews
- Second Review
- AFK / HITL Boundary

For a clear task, the implementation plan records why separate `spec-review` is unnecessary.
If the request only exists in chat, the plan must include an approved request anchor with
the same canonical fields.

Create a separate spec when product scope, domain language, public API, data/storage, auth/security,
deletion, sync, external integrations, or user workflow is still being decided. Do not create a spec
only to restate an already clear task.

Accepted-risk exceptions may skip a normal gate only when explicitly approved by the user or
recorded in an already approved plan. Record the skipped gate, reason, risk, compensating check,
user acceptance, and follow-up or expiry.

## Review Routing

Use the lightest review that protects the work:

- `spec-review`: when a separate spec or PRD exists, or when acceptance criteria are still being
  shaped.
- `plan-review`: required before executing a non-trivial or multi-step implementation plan, unless
  an explicit accepted-risk record exists.
- `implementation-review`: after substantial slices or review-fix passes.
- `test-review`: when tests are weak, flaky, heavily mocked, missing acceptance coverage, or central
  to the risk.
- `architecture-review`, `security-review`, or `docs-review`: only when the touched surface matches
  the review concern.
- `second-review`: required for high-risk
  security/data-loss/money/auth/crypto/deletion/core-architecture work; optional for specs, plans,
  broad diffs, weak tests, or when the user wants an independent Codex check.

Prefer the Claude Code Codex plugin for `second-review` when working in Claude Code. If unavailable,
use a clean Codex session, Codex CLI, or record the fallback.

## Execution Model

- Small/local behavior change: use `behavior-tdd` directly, then `ship-check`.
- Reviewed multi-slice plan: use `execute-plan` as the controller. Each implementation slice still
  uses `behavior-tdd` for behavior changes.
- Worker/subagent execution: delegate one vertical slice or disjoint write scope at a time. The
  controller must inspect for acceptance compliance and code quality; run implementation, focused,
  or second review when the result is substantial, risky, hard to inspect, or required by the plan.

## Routing

Choose the next phase, not the entire lifecycle:

| Situation | Next skill |
| --- | --- |
| New or unscaffolded repo | `project-scaffold` |
| Product brainstorming, goal, MVP, users, or non-goals unclear | `product-discovery` |
| Idea, spec, or plan needs pressure testing | `pressure-test` |
| Domain terms, contexts, invariants, or hard-to-reverse decisions are unclear | `domain-modeling` |
| Goal is clear but no acceptance artifact or slices exist | `write-spec` |
| Spec or PRD exists but primary review is missing | `spec-review` |
| Acceptance artifact is reviewed, but implementation path is unclear | `write-plan` |
| Non-trivial or multi-step plan exists but plan review is missing | `plan-review` |
| Reviewed and approved plan has multiple slices | `execute-plan` |
| Small behavior change or implementation task | `behavior-tdd` |
| Bug, flaky test, or regression | `bug-diagnosis` |
| Tests may not prove accepted behavior | `test-review` |
| Architecture, DDD, SOLID, or file-size concern | `architecture-review` |
| Completed slice, implementation diff, or test quality needs review | `implementation-review` |
| Security, data-loss, destructive, auth, secrets, crypto, untrusted input, injection, path traversal, command construction, parser/deserialization, SSRF, or open redirect risk exists | `security-review` |
| Durable docs or handoff may be stale | `docs-review` |
| Independent Codex review is required or requested | `second-review` |
| Behavior, architecture, testing, security, or workflow changed | `docs-sync` |
| Work is ready to hand off, commit, PR, or release | `ship-check` |
| Commit, stacked branch, PR, or release action is approved | `ship-check` then commit/stack gate |
| User approved repeated autonomous progress | `bounded-loop` |

## Phase Loop

After each phase:

1. Record or update the durable artifact for that phase when the work is non-trivial.
2. Update `docs/CURRENT.md` when the active phase, active acceptance artifact/source, active plan,
blocker, completed slice, verification evidence, or next action materially changes. If the same
session immediately continues, update it once at the end of the phase.
3. Run the narrowest useful verification or explain why none applies.
4. Decide one of: continue to the next skill, ask the user, clear context after handoff, or stop.
5. Recommend exactly one next phase when the workflow has a clear next step. Ask a concise
confirmation instead of making the user remember the next skill.
6. Do not advance when approval is required for git setup, dependency execution, hooks,
   deletion, commit/stack actions, history rewrite, broad scope expansion, or unresolved
   product/domain/architecture decisions.

## Continuation Prompts

Use these as defaults after finishing a phase:

- After product discovery: "제품 방향이 정리됐습니다. 아직 불확실한 가정을 pressure-test할까요, 아니면 바로 acceptance artifact를
  정리할까요?"
- After pressure-test: "주요 가정이 정리됐습니다. 도메인 모델링이 필요할까요, 아니면 acceptance artifact 작성으로 넘어갈까요?"
- After domain modeling: "도메인 언어가 정리됐습니다. 이 내용으로 acceptance artifact와 vertical slice를 작성할까요?"
- After write-spec: "Acceptance artifact가 준비됐습니다. full spec/PRD이거나 기준이 아직 흔들리면 spec-review가 필요합니다.
  가벼운 accepted task라면 compact implementation plan으로 넘어가겠습니다."
- After spec review: "Acceptance review가 끝났습니다. compact implementation plan을 작성할까요?"
- After write-plan: "계획이 준비됐습니다. non-trivial 또는 multi-step이면 plan-review를 진행하겠습니다. 범위를 small path로
  줄이려면 알려주세요."
- After plan review: "계획 리뷰가 끝났습니다. 첫 vertical slice 구현을 시작할까요?"
- After implementation review: "리뷰 결과를 반영했습니다. docs-sync와 ship-check로 마무리할까요?"

If the user has already approved an end-to-end bounded goal, continue inside the approved scope and
stop conditions instead of asking after every safe phase.

## Parallel Work

- Scope in the main agent first. Do not delegate before reading enough artifacts to split the work
  clearly.
- Use parallel tool calls for small independent reads or searches.
- Use subagents for substantial independent tracks with distinct concerns and clear return formats.
- A single focused reviewer subagent is acceptable for a named review concern; exploratory batches
  should usually have two or more independent tracks.
- Do not send data already in main-agent context to subagents only for formatting or summarizing.

## Context Control

Keep context small:

- Load only the skill needed for the current phase.
- Prefer artifact paths over chat summaries.
- Write a handoff before clearing after discovery/spec, plan approval, several implementation
  slices, or review fixes.
- New sessions resume from `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`, `docs/AGENT_WORKFLOW.md`,
  active acceptance artifact/plan, recent reviews, and relevant code.

## Output

Return:

- Context read
- Workflow weight
- Selected next skill
- Current phase and next recommended phase
- Required artifact or approval
- Next safe action
