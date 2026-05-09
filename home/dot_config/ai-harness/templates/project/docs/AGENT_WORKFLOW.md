# Agent Workflow

Document status: stub. TODO claims are not project truth yet. Non-TODO workflow, safety, and quality rules apply immediately.

This project uses the local AI harness workflow so humans can inspect agent decisions, plans, reviews, and verification.

## Default Lifecycle

```text
Brainstorming / product discovery
-> Critical interview when unclear or risky
-> Domain modeling when domain language matters
-> Spec or light PRD
-> Vertical slices
-> Spec review
-> Implementation plan
-> Plan review
-> Behavior TDD execution
-> Implementation review
-> Risk-based review / second review when required
-> Docs sync
-> Ship review
```

## Session Start

Use this prompt:

```text
Use using-ai-harness.
Task: <describe task>.
Read AGENTS.md, CONTEXT.md, docs/CURRENT.md, docs/AGENT_WORKFLOW.md, current specs/plans/reviews relevant to this task, and data/security docs when relevant.
Report the workflow weight, current phase, selected next skill, required artifact or approval, and next safe action before editing.
```

## Evidence Gate

- For trivial edits, inspect the target file and adjacent context.
- For behavior, API, dependency, data, security, or infrastructure changes, trace execution paths, call sites, constraints, and regression surface before editing.
- Do not fabricate paths, commits, APIs, config keys, env vars, test results, tool behavior, or capabilities.
- Do not weaken validation to make a change look complete.
- Ask before changing behavior, API or UX, naming, persistence, auth, dependencies, config, compatibility, product scope, or domain language outside the approved plan.

## New Feature

Use this prompt:

```text
Use using-ai-harness first, then use only the needed skills from critical-interview, domain-modeling, spec-to-slices, review-gate, implementation-planning, agentic-execution, docs-sync, and ship-review for this feature.
Feature: <describe feature>.
Keep the MVP small, prefer vertical slices, and require Codex second review for risky plans or diffs.
```

Expected artifacts:

- `docs/specs/YYYY-MM-DD-<feature>.md`
- `docs/plans/YYYY-MM-DD-<feature>.md`
- `docs/CURRENT.md`
- `docs/reviews/YYYY-MM-DD-<feature>-*.md` when substantial
- updates to durable docs if product, domain, architecture, or testing changes

## Workflow Weight

Use the lightest workflow that fits the risk:

- Tiny/local: bounded files in one component or module, no product/domain/API/data/security decision. Tests, styles, and docs that directly support the same change do not make it non-trivial by themselves. Use direct edit or `tdd-workflow` plus `ship-review`.
- Scope review: three or more files, or uncertainty about blast radius. Decide whether the small path still fits before escalating.
- Non-trivial: product behavior, user workflow, domain language, public API, persistence, auth/security, sync/concurrency, deletion, or external integration. Use spec, plan, review, and docs gates.
- Risky/substantial: core architecture, money, crypto, data loss, broad refactor, weak tests, five or more files, two or more modules, or 300/600-line file thresholds. Require `review-gate` and independent second review when available.

## Project Scaffold Gate

Before first scaffold or major harness refresh, ask the user to approve each setup action:

- `git init`
- template docs and agent instruction files
- `.claude/`, `.codex/`, or `.agents/`
- `lefthook.yml`
- package or stack bootstrap commands to suggest
- package install or stack bootstrap execution only when explicitly requested
- initial commit

Complete only the approved actions and report skipped actions.

Dependency installation is user-managed by default. Suggest commands and assumptions; do not execute installs unless the user explicitly asks the agent to run them.

## Workflow Continuation

After each non-trivial phase:

1. Update `docs/CURRENT.md` with current phase, active spec/plan, done, next, blockers, and last verification.
2. Recommend exactly one next phase when the path is clear.
3. Ask a concise confirmation question instead of waiting for the user to know the next skill.

Default continuation questions:

- After product discovery: "제품 방향이 정리됐습니다. 다음 단계로 비판적 검토를 진행할까요, 아니면 바로 스펙 초안으로 갈까요?"
- After critical interview: "주요 가정이 정리됐습니다. 도메인 모델링이 필요할까요, 아니면 스펙 작성으로 넘어갈까요?"
- After domain modeling: "도메인 언어가 정리됐습니다. 이 내용으로 스펙과 vertical slice를 작성할까요?"
- After spec-to-slices: "스펙 초안이 준비됐습니다. 먼저 spec review를 진행할까요?"
- After spec review: "스펙 리뷰가 끝났습니다. 구현 계획을 작성할까요?"
- After implementation planning: "계획이 준비됐습니다. plan review를 진행할까요?"
- After plan review: "계획 리뷰가 끝났습니다. 첫 vertical slice 구현을 시작할까요?"

Do not auto-advance across setup, dependency execution, hook, delete, git-history, product, domain, architecture, data, or security decisions unless the approved bounded goal explicitly covers them.

## Small Change

Use this prompt:

```text
Use tdd-workflow and ship-review for this small behavior change.
Run docs-sync only if behavior, architecture, testing, or user-facing behavior changes.
Change: <describe change>.
```

## Bounded Goal Loop

Use this prompt only after the goal is clear:

```text
Use bounded-goal-loop.
Goal: <specific outcome>.
Allowed scope: <files/modules/docs/commands>.
Allowed autonomous actions: <exact file areas, commands, review/fix scope, and worker-agent use>.
Forbidden actions: <setup/dependencies/hooks/git history/deletes/deploys/etc>.
Iteration budget: <max loops or timebox>.
Verification gate: <test/typecheck/lint/build/manual check>.
Review gate: <when to run review-gate or Codex second review>.
Stop and ask me if scope expands, verification fails twice for the same reason, a product/domain/architecture decision changes, unapproved worker scope is needed, or setup/destructive/git-history action is needed.
```

Do not use a loop for product discovery, broad refactors without a reviewed plan, dependency changes, git setup, hook installation, deletes, or history rewrites.

## Worker Agent Execution

Use this prompt when an approved plan has independent slices and a worker agent is available:

```text
Use agentic-execution.
Execute only the approved plan task: <task>.
Controller: keep plan state, review state, and final decisions in this main session.
Worker: use Codex plugin, Codex session, Claude subagent, or another worker only for <slice> with a disjoint write scope.
Give the worker the spec path, plan path, allowed files, relevant docs, verification commands, and required return format.
After the worker returns, inspect the diff and run spec-compliance review plus code-quality review before starting another worker task.
```

Do not delegate unresolved product, domain, architecture, dependency, setup, delete, or git-history decisions to a worker.

## Bug Fix

Use this prompt:

```text
Use bug-diagnosis.
Reproduce the bug first, add or preserve a failing regression test, fix the root cause, rerun the repro, then use review-gate and ship-review.
Bug: <describe bug>.
```

## Refactor

Use this prompt:

```text
Use architecture-review.
Find refactor candidates that improve testability, module depth, domain clarity, file responsibility, or agent navigability.
Do not edit code until the refactor slice is approved.
```

## Spec Review

Use this prompt before implementation planning:

```text
Use review-gate on docs/specs/<spec>.md.
Run a primary spec review for product goal, MVP boundary, acceptance criteria, vertical slices, domain language, testing decisions, docs impact, and open risks.
Ask Codex for independent second review if risk requires it.
```

Do not write an implementation plan until the spec review is complete or accepted risk is recorded.

## Plan Review

Use this prompt:

```text
Use review-gate on docs/plans/<plan>.md.
Confirm the spec review exists or accepted risk is recorded. Then review for spec coverage, file responsibility, TDD granularity, DDD/SOLID fit, file size risk, docs impact, and verification.
Ask Codex for independent second review if risk requires it.
```

## Second Review

Use Codex as an independent reviewer when:

- Product direction, MVP boundary, or core architecture changes.
- The plan touches auth, crypto, money, deletion, sync, concurrency, persistence, or external integrations.
- The diff is large or spans multiple modules.
- A source file exceeds 600 lines or accepts a 300+ line risk.
- Tests are weak, flaky, slow, or heavily mocked.
- The primary agent got stuck or changed approach repeatedly.

Claude Code prompt:

```text
Use the Codex plugin for independent second review.
Ask Codex to review this spec/plan/diff for hidden assumptions, architecture drift, missing tests, DDD/SOLID violations, file size risk, and docs drift.
```

Fallback prompt for a clean Codex session or CLI:

```text
Review this independently.
Read AGENTS.md, CONTEXT.md, docs/CURRENT.md, docs/AGENT_WORKFLOW.md, the relevant spec/plan/review notes, and the diff or changed file list.
Return findings first with P0-P3 severity, evidence, suggested fixes, and pass/pass-with-follow-ups/blocked.
Do not rely on the primary agent's chat summary except as a pointer to artifacts.
```

If independent review is unavailable, record the reason, compensating review, accepted risk, and whether the user accepted proceeding without it.

## Session Clear Policy

Clear or restart an agent session at phase boundaries, not in the middle of a slice.

Good clear points:

- After discovery/interview is summarized into docs.
- After spec approval and before implementation planning.
- After plan approval and before long implementation.
- After several vertical slices are completed and verified.
- After review fixes and before final ship review.

Before clearing, write:

```text
Write a handoff note in docs/reviews/YYYY-MM-DD-<topic>-handoff.md.
Include goal, docs to read, decisions, completed slices, changed files, verification, risks, and next action.
Update docs/CURRENT.md before clearing.
```

New session prompt:

```text
Resume from docs/reviews/<handoff>.md.
Read AGENTS.md, CONTEXT.md, docs/CURRENT.md, CONTEXT-MAP.md, docs/AGENT_WORKFLOW.md, the current spec, the current plan, recent reviews, and data/security docs when relevant.
Summarize what is done, what remains, and what you will do next.
```

## Required Checks

Project-specific commands:

- Install: TODO
- Test: TODO
- Typecheck: TODO
- Lint: TODO
- Build: TODO
- E2E/manual: TODO
- Config validate/reload: TODO

Dependency installation is user-managed by default. Agents may suggest package or bootstrap commands, but must not run them unless explicitly asked to execute.

## Artifact Rules

- Durable decisions go in `docs/DECISIONS/`, not only chat.
- Current phase, active spec/plan, blockers, last verification, and next action go in `docs/CURRENT.md`.
- Product scope goes in `docs/ROADMAP.md` and specs.
- Domain language goes in `CONTEXT.md` and `docs/DOMAIN_MODEL.md`.
- Data storage, migration, retention, deletion, and backups go in `docs/DATA_MODEL.md`.
- Secrets, auth, permissions, trust boundaries, and sensitive data handling go in `docs/SECURITY_MODEL.md`.
- Implementation detail for one feature goes in `docs/plans/`.
- Review records and handoffs go in `docs/reviews/`.
- README stays user-facing and high-level.
