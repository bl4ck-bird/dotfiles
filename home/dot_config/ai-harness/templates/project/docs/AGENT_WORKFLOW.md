# Agent Workflow

Document status: stub. TODO claims are not project truth yet. Non-TODO workflow, safety, and quality
rules apply immediately.

This project uses the local BB Harness. Global workflow rules live in the harness skills; this file
records project-local usage, commands, and overrides.

## Skill-First

When using this harness, prefer the relevant workflow skill over ad-hoc process.

- Start every session with `using-bb-harness` (universal bootstrap, self-disables when
  this repo's markers are absent).
- Use direct matching skills when the task obviously maps to one.
- Use the smallest useful set of skills for the workflow weight.
- If a relevant skill is skipped for a small/local task, record why in the final report
  or plan.

## Session Start

Use this prompt:

```text
Use using-bb-harness.
Task: <describe task>.
Read AGENTS.md, CONTEXT.md, docs/CURRENT.md, docs/AGENT_WORKFLOW.md, current
acceptance artifacts, plans, and reviews relevant to this task, and data/security
docs when relevant.
Report workflow weight, selected next skill, required artifact or approval, and
next safe action before editing.
```

## Workflow Weight

- **Tiny/local**: direct edit or `test-driven-development` plus `ship-check`.
- **Scope review**: 3+ files, uncertain blast radius, or unclear module boundary. Decide
  whether the small path still fits. Record bounded scope.
- **Non-trivial**: reviewed acceptance artifact (`write-spec` Self-Review) + compact
  plan (`write-plan` Self-Review) + `subagent-driven-development` (or
  `executing-plans-inline` when subagent dispatch is unavailable) + per-task
  `test-driven-development` + `spec-compliance-review` + `code-quality-review` +
  `docs-sync` + `ship-check`.
- **Risky/substantial**: above + `security-review` when triggered, `second-review`
  for High-Risk Surface or boundary/dependency-direction change. File-size
  thresholds defined in `code-quality-review` (File And Complexity Thresholds).

## Default Non-Trivial Flow

```text
product-discovery → pressure-test → domain-modeling      (discovery, as needed)
  ↓
write-spec      (with Self-Review: Product Clarity + Domain Alignment)
  ↓
write-plan      (with Self-Review: Plan Hygiene + Architecture Soundness)
  ↓
using-git-worktrees                                       (isolated workspace)
  ↓
subagent-driven-development   OR   executing-plans-inline
  for each task:
    test-driven-development
    spec-compliance-review        (binary ✅/❌)
    code-quality-review           (Ready to merge? Yes/No/With fixes)
    security-review               (when triggered)
    second-review                 (High-Risk Surface or double-check)
    receiving-review              (between reviewer feedback and fix)
  ↓
verification-before-completion                            (every completion claim)
  ↓
docs-sync
  ↓
ship-check
  ↓
commit / stack / PR / release    (only when explicitly approved)
```

Adjacent skills:

- `bug-diagnosis` for bugs / flaky tests / regressions (with companion files when
  needed: `root-cause-tracing`, `defense-in-depth`, `condition-based-waiting`,
  `test-pollution`, `debugging-pressure-scenarios`).
- `dispatching-parallel-agents` for 2+ independent concurrent investigations
  (distinct from `subagent-driven-development`'s sequential plan execution).
- `bounded-loop` for user-approved autonomous repetition (only after goal, scope,
  allowed actions, iteration budget, verification gate, and stop conditions are
  explicit).
- `project-scaffold` for adding or refreshing harness scaffold in this project.

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

Use the canonical Acceptance Brief fields defined in `skills/write-spec/SKILL.md` (Light Acceptance
Brief template). Do not re-list the fields here.

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

- Spec correctness lives in `write-spec` Self-Review (Product Clarity + Domain Alignment).
- Plan correctness lives in `write-plan` Self-Review (Plan Hygiene + Architecture
  Soundness).
- For each implemented task, run `spec-compliance-review` (binary ✅/❌) first, then
  `code-quality-review` (Ready to merge? Yes / No / With fixes). Both run as fresh
  reviewer subagents from `subagent-driven-development`.
- `code-quality-review` is the SSOT for DDD operational checks, SOLID, file size, the
  Coverage Matrix, and durable docs drift.
- Use `security-review` as a follow-on when the diff touches auth, secrets, crypto,
  deletion, untrusted input, sensitive data, or a destructive operation.
- Use `second-review` when High-Risk Surface is touched, boundary or dependency direction
  changes, or the user requests an independent double-check. Codex by default; record a
  fallback when unavailable.
- Apply `receiving-review` whenever a reviewer returns findings — verify before
  implementing, push back if wrong, apply one item at a time.

## Workflow Continuation

After each non-trivial phase:

1. Update `docs/CURRENT.md` when current phase, active acceptance artifact/source, plan, done,
   next, blockers, or last verification materially changes. If the same session continues
   immediately, update it once at the end of the phase.
2. Recommend exactly one next phase when the path is clear.
3. Ask a concise confirmation question when approval is needed.

Default continuation prompts live in `skills/using-bb-harness/SKILL.md`. The project may override here
when wording needs to differ from the harness default.

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
