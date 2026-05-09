# Agent Workflow

Document status: stub. TODO claims are not project truth yet. Non-TODO workflow, safety, and quality
rules apply immediately.

This project uses the local BB Harness. Global workflow rules live in the harness skills; this file
records project-local usage, commands, and overrides.

## Skill-First

When using this harness, prefer the relevant workflow skill over ad-hoc process.

- Start or resume with `bb-workflow` when the phase is unclear.
- Use direct matching skills for discovery, pressure-test, domain modeling, acceptance artifacts,
  reviews, plans, execution, docs sync, and ship checks.
- Use the smallest useful set of skills for the workflow weight.
- If a relevant skill is skipped for a small/local task, record why in the final report or plan.

## Session Start

Use this prompt:

```text
Use bb-workflow.
Task: <describe task>.
Read AGENTS.md, CONTEXT.md, docs/CURRENT.md, docs/AGENT_WORKFLOW.md, current acceptance artifacts, plans, and reviews relevant to this task, and data/security docs when relevant.
Report workflow weight, selected next skill, required artifact or approval, and next safe action before editing.
```

## Workflow Weight

- Tiny/local: use direct edit or `behavior-tdd` plus `ship-check`.
- Scope review: three or more files, uncertain blast radius, or unclear module boundary. Decide
  whether the small path still fits. If keeping the small path, record why it is bounded, the
  files/modules involved, why no product/API/data/security decision is changing, verification, and
  docs impact.
- Non-trivial: use a reviewed acceptance artifact, compact plan, `execute-plan` for multi-slice
  work, TDD inside each behavior-changing slice, focused reviews, docs sync, and ship check.
- Risky/substantial: core architecture, money, crypto, data loss, auth, deletion, broad refactor,
  weak tests, five or more files, two or more modules, or 300/600-line file thresholds. Add the
  relevant focused review. Require `second-review` for high-risk
  security/data-loss/money/auth/crypto/deletion/core-architecture work when available; consider it
  for large diffs or weak verification.

## Acceptance Artifacts

Non-trivial work needs one artifact accepted or reviewed at the right weight that states behavior
and acceptance criteria. This can be:

- `docs/specs/YYYY-MM-DD-<feature>.md`
- a PRD or issue
- a review finding
- a user-approved task with testable acceptance criteria

Use a full spec when product scope, domain language, API, data/storage, auth/security, deletion,
sync, external integrations, or user workflow is still being decided. Do not create a spec only to
restate an already clear task.

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

## Project Scaffold Gate

Before first scaffold or major harness refresh, ask the user to approve each setup action:

- `git init`
- template docs and agent instruction files
- `.claude/`, `.codex/`, or `.agents/`
- `lefthook.yml`
- package or stack bootstrap commands to suggest
- package install or stack bootstrap execution only when explicitly requested
- initial commit
- commit, push, PR, or stacked-branch actions after implementation

Complete only approved actions and report skipped actions.

Dependency installation is user-managed by default. Suggest commands and assumptions; do not execute
installs unless the user explicitly asks the agent to run them.

## Review Routing

- Use `spec-review` for full specs, PRDs, or unclear acceptance criteria.
- Use `plan-review` for non-trivial or multi-step implementation plans.
- Use `implementation-review` after substantial slices or review-fix passes.
- Use `test-review` for weak, missing, flaky, heavily mocked, or acceptance-critical tests.
- Use `architecture-review`, `security-review`, or `docs-review` only when the work touches that
  concern.
- Use `second-review` when high-risk work needs independent review. For specs and plans, this is
  optional unless security, data loss, money, auth, crypto, deletion, or core architecture risk is
  high.
- In Claude Code, prefer the Codex plugin for `second-review` when available.

## Workflow Continuation

After each non-trivial phase:

1. Update `docs/CURRENT.md` when current phase, active acceptance artifact/source, plan, done,
   next, blockers, or last verification materially changes. If the same session continues
   immediately, update it once at the end of the phase.
2. Recommend exactly one next phase when the path is clear.
3. Ask a concise confirmation question when approval is needed.

Default continuation questions:

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

Do not auto-advance across setup, dependency execution, hook, delete, git-history,
commit/stack, product, domain, architecture, data, or security decisions unless the
approved bounded goal explicitly covers them.

Accepted-risk exceptions may skip a normal gate only when explicitly approved by the user or
recorded in an already approved plan. Record the skipped gate, reason, risk, compensating check,
user acceptance, and follow-up or expiry.

## Commit And Stack Gate

After `ship-check`, commit or stack work is allowed only when the user, project-local
instructions, or approved bounded goal explicitly authorizes it.

Default policy:

- Stage only files owned by the completed task or slice.
- Prefer one commit per completed vertical slice when history matters.
- For stacked work, name branch order and review audience in the plan.
- If commit is not approved, report "ready to commit" with a suggested message.

## Required Checks

Project-specific commands:

- Install: TODO
- Test: TODO
- Typecheck: TODO
- Lint: TODO
- Build: TODO
- E2E/manual: TODO
- Config validate/reload: TODO

Prefer TDD plus project hooks such as lefthook for automated coverage. Add manual/browser
verification only when the behavior cannot be covered well by automated tests or hooks.

## Bounded Loop Prompt

```text
Use bounded-loop.
Goal: <specific outcome>.
Allowed scope: <files/modules/docs/commands>.
Allowed autonomous actions: <exact file areas, commands, review/fix scope, and worker-agent use>.
Forbidden actions: <setup/dependencies/hooks/git history/deletes/deploys/etc>.
Iteration budget: <max loops or timebox>.
Verification gate: <test/typecheck/lint/build/manual check>.
Stop and ask if scope expands, verification fails twice for the same reason, a product/domain/architecture decision changes, unapproved worker scope is needed, or setup/destructive/git-history action is needed.
```

## Artifact Rules

- Current phase, active acceptance artifact/source, blockers, last verification, and next action go
  in `docs/CURRENT.md`.
- Product scope goes in `docs/ROADMAP.md` and acceptance artifacts.
- Domain language goes in `CONTEXT.md` and `docs/DOMAIN_MODEL.md`.
- Data storage, migration, retention, deletion, and backups go in `docs/DATA_MODEL.md`.
- Secrets, auth, permissions, trust boundaries, and sensitive data handling go in
  `docs/SECURITY_MODEL.md`.
- Implementation details for one feature go in `docs/plans/` when a durable plan is needed.
- Review records and handoffs go in `docs/reviews/`.
- Formal decision records go in `docs/DECISIONS/` only for hard-to-reverse, surprising tradeoffs.
- README stays user-facing and high-level.
