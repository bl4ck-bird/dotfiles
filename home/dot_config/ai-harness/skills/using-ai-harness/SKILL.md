---
name: using-ai-harness
description: Use when starting, resuming, or routing side-project work through the AI harness before choosing specific workflow skills.
---

# Using AI Harness

Use this as the entry point for agent work. It selects the lightest sufficient workflow, names the next skill to use, and prevents loading every process at once.

## Start

1. Read the nearest `AGENTS.md` or `CLAUDE.md`.
2. If present, read `CONTEXT.md`, `docs/CURRENT.md`, `docs/AGENT_WORKFLOW.md`, the active spec, plan, and recent review or handoff note.
3. Check available skills for a direct match before choosing the execution path.
4. Summarize only:
   - current goal
   - workflow weight
   - missing decisions or artifacts
   - next safe action

If key context is missing, ask for it or propose a minimal recovery step. Do not invent product, domain, architecture, or safety decisions.

## Evidence Gate

- For trivial edits, inspect the target file and adjacent context before editing.
- For behavior, API, dependency, data, security, or infrastructure changes, trace the execution path, call sites, constraints, and regression surface first.
- If the next action would change behavior, API or UX, naming, persistence, auth, dependency, config, compatibility, product scope, or domain language outside an approved plan, ask before continuing.

## Workflow Weight

- Tiny/local: one bounded component or module, no product/domain/API/data/security decision. Tests, styles, fixtures, or docs supporting the same bounded change may stay on the small path. Use direct edit or `tdd-workflow` plus `ship-review`.
- Scope review: three or more files, or uncertain blast radius. Decide whether the small path still fits.
- Non-trivial: product behavior, user workflow, domain language, public API, persistence, auth/security, sync/concurrency, deletion, or external integration. Use spec, plan, review, and docs gates.
- Risky/substantial: core architecture, money, crypto, data loss, broad refactor, weak tests, five or more files, two or more modules, or 300/600-line file thresholds. Require `review-gate` and independent second review when available.

## Routing

Choose the next phase, not the entire lifecycle:

| Situation | Next skill |
| --- | --- |
| New or unscaffolded repo | `project-scaffold` |
| Product brainstorming, goal, MVP, users, or non-goals unclear | `product-discovery` |
| Idea, spec, or plan needs pressure testing | `critical-interview` |
| Domain terms, contexts, invariants, or ADRs are unclear | `domain-modeling` |
| Goal is clear but no spec or slices exist | `spec-to-slices` |
| Spec exists but implementation path is unclear | `implementation-planning` |
| Approved plan has multiple slices | `agentic-execution` |
| Small behavior change or implementation task | `tdd-workflow` |
| Bug, flaky test, or regression | `bug-diagnosis` |
| Architecture, DDD, SOLID, or file-size concern | `architecture-review` |
| Plan, diff, loop, docs, tests, or security needs review | `review-gate` |
| Behavior, architecture, testing, security, or workflow changed | `docs-sync` |
| Work is ready to hand off, commit, PR, or release | `ship-review` |
| User approved repeated autonomous progress | `bounded-goal-loop` |

## Phase Loop

After each phase:

1. Record or update the durable artifact for that phase when the work is non-trivial.
2. Update `docs/CURRENT.md` when the active phase, active spec, active plan, blocker, completed slice, or next action changes.
3. Run the narrowest useful verification or explain why none applies.
4. Decide one of: continue to the next skill, ask the user, clear context after handoff, or stop.
5. Recommend exactly one next phase when the workflow has a clear next step. Ask a concise confirmation instead of making the user remember the next skill.
6. Do not advance when approval is required for git setup, dependency execution, hooks, deletion, history rewrite, broad scope expansion, or unresolved product/domain/architecture decisions.

## Continuation Prompts

Use these as defaults after finishing a phase:

- After product discovery: "제품 방향이 정리됐습니다. 다음 단계로 비판적 검토를 진행할까요, 아니면 바로 스펙 초안으로 갈까요?"
- After critical interview: "주요 가정이 정리됐습니다. 도메인 모델링이 필요할까요, 아니면 스펙 작성으로 넘어갈까요?"
- After domain modeling: "도메인 언어가 정리됐습니다. 이 내용으로 스펙과 vertical slice를 작성할까요?"
- After spec-to-slices: "스펙 초안이 준비됐습니다. 먼저 spec review를 진행할까요?"
- After spec review: "스펙 리뷰가 끝났습니다. 구현 계획을 작성할까요?"
- After implementation planning: "계획이 준비됐습니다. plan review를 진행할까요?"
- After plan review: "계획 리뷰가 끝났습니다. 첫 vertical slice 구현을 시작할까요?"
- After implementation review: "리뷰 결과를 반영했습니다. docs-sync와 ship-review로 마무리할까요?"

If the user has already approved an end-to-end bounded goal, continue inside the approved scope and stop conditions instead of asking after every safe phase.

## Parallel Work

- Scope in the main agent first. Do not delegate before reading enough artifacts to split the work clearly.
- Use parallel tool calls for small independent reads or searches.
- Use subagents for substantial independent tracks with distinct concerns and clear return formats.
- A single focused reviewer subagent is acceptable for a named review gate; exploratory batches should usually have two or more independent tracks.
- Do not send data already in main-agent context to subagents only for formatting or summarizing.

## Context Control

Keep context small:

- Load only the skill needed for the current phase.
- Prefer artifact paths over chat summaries.
- Write a handoff before clearing after discovery/spec, plan approval, several implementation slices, or review fixes.
- New sessions resume from `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`, `docs/AGENT_WORKFLOW.md`, active spec/plan, recent reviews, and relevant code.

## Output

Return:

- Context read
- Workflow weight
- Selected next skill
- Current phase and next recommended phase
- Required artifact or approval
- Next safe action
