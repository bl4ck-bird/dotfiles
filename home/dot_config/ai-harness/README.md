# BB Harness

Central agent workflow, project templates, skills, reviewer agents, and conservative hooks managed by chezmoi.

BB Harness turns ad-hoc Claude Code, Codex, and skill usage into a restartable side-project workflow. The point is not to create documents for their own sake. The point is to make product intent, acceptance criteria, implementation plan, verification evidence, review decisions, and residual risk inspectable after the agent session ends.

This README is the human orientation guide. Agents should treat `AGENTS.md`, project-local instructions, and `skills/*/SKILL.md` as the executable source of truth. The README may be used for orientation, but it should not duplicate every skill rule.

## Design Goals

- Use the right workflow weight for the task.
- Prefer skills and plugins when they exist for the job.
- Keep durable context outside chat.
- Make non-trivial work reviewable before implementation.
- Keep plans compact enough to execute without wasting context.
- Use TDD and project hooks for repeatable verification.
- Use independent review when risk justifies it, not as default ceremony.

## Layout

- `AGENTS.md`: shared global defaults for Codex-compatible agents.
- `skills/`: executable workflow skills. `bb-workflow` is the router.
- `claude-agents/`: Claude Code reviewer subagent definitions.
- `hooks/`: conservative hook scripts. They are not wired globally by default.
- `templates/project/`: starter project instructions and durable docs.

## Link Strategy

Chezmoi installs `~/.config/ai-harness` as the source of truth, then links agent-facing locations back to it:

- `~/.agents/AGENTS.md`
- `~/.codex/AGENTS.md`
- `~/.claude/CLAUDE.md`
- `~/.agents/skills/<skill-name>`
- `~/.claude/skills`
- `~/.claude/agents/<agent-name>.md`

Claude Code and Codex see the same workflow source. Tool-specific runtime settings still live under their native config directories.

## Skill-First Posture

When the BB Harness is in use, skills are the workflow surface. Use them rather than recreating their process in chat.

Skill-first does not mean "load every skill." It means:

- Start or resume with `bb-workflow` when the phase is unclear.
- Use a direct matching skill when the task clearly maps to one.
- Move from phase to phase through skills instead of improvising.
- Skip a relevant skill only when the task is clearly small/local or the skill would not materially protect the work.
- If a skill is skipped, record the reason briefly.

This keeps plugins and skills useful without turning every change into a heavyweight ritual.

## Workflow Model

Default non-trivial flow:

```text
bb-workflow
-> product-discovery when goal, users, MVP, or non-goals are unclear
-> pressure-test when assumptions are unclear or risky
-> domain-modeling when domain language or boundaries matter
-> acceptance artifact: spec, PRD, issue, review finding, or approved task
-> spec-review when a spec/PRD exists or acceptance criteria need shaping
-> compact implementation plan
-> plan-review for non-trivial or multi-step plans
-> execute-plan for reviewed multi-slice plans
-> behavior-tdd for small/local work or each implementation slice
-> implementation-review and focused reviews as needed
-> second-review when high risk or independently requested
-> docs-sync
-> ship-check
```

A separate spec is not mandatory for every task. Non-trivial work needs a reviewed acceptance artifact: something durable enough to state the behavior, acceptance criteria, risks, and boundaries.

Use a full `docs/specs/` spec when product scope, domain language, public API, data/storage, auth/security, deletion, sync, external integrations, or user workflow is still being decided. For already-clear work, an issue, review finding, or approved user task can be enough.

Plans should be compact. A plan records file responsibility, TDD steps, verification, docs impact, review needs, and rollback notes. It should not restate the spec or become line-by-line implementation prose.

## Workflow Weight

Use the lightest workflow that protects correctness, evidence, safety, and consistency:

- Tiny/local: bounded files in one component or module, no product/domain/API/data/security decision. Use direct edit or `behavior-tdd` plus `ship-check`.
- Scope review: three or more files, uncertain blast radius, or unclear module boundary. Decide whether the small path still fits.
- Non-trivial: product behavior, user workflow, domain language, public API, persistence, auth/security, sync/concurrency, deletion, or external integration. Use a reviewed acceptance artifact, compact plan, focused reviews, and docs gates.
- Risky/substantial: core architecture, money, crypto, data loss, auth, deletion, broad refactor, weak tests, five or more files, two or more modules, or 300/600-line file thresholds. Require the relevant focused review. Require `second-review` for high-risk security/data-loss/money/auth/crypto/deletion/core-architecture work, and consider it for large diffs or weak verification.

## Skill Map

| Situation | Skill |
| --- | --- |
| Choose workflow weight and next phase | `bb-workflow` |
| Start or refresh project instructions | `project-scaffold` |
| Product direction is unclear | `product-discovery` |
| Assumptions need challenge | `pressure-test` |
| Domain language or boundaries matter | `domain-modeling` |
| Create an acceptance artifact and slices | `write-spec` |
| Review a spec, PRD, or acceptance artifact | `spec-review` |
| Create a compact implementation plan | `write-plan` |
| Review implementation plan before execution | `plan-review` |
| Execute reviewed multi-slice plan | `execute-plan` |
| Implement behavior through red-green-refactor | `behavior-tdd` |
| Diagnose a bug or regression | `bug-diagnosis` |
| Review architecture, DDD, SOLID, file size | `architecture-review` |
| Review implementation diff or completed slice | `implementation-review` |
| Review auth, secrets, crypto, deletion, untrusted input, data loss | `security-review` |
| Review durable docs and drift | `docs-review` |
| Request or record independent Codex review | `second-review` |
| Sync docs after behavior or workflow changes | `docs-sync` |
| Final handoff, verification, and residual risk check | `ship-check` |
| Continue bounded autonomous iterations | `bounded-loop` |

## Acceptance Artifact, Spec, And Plan

The harness separates "what should be true" from "how to change files."

Acceptance artifact:

- Owns behavior, acceptance criteria, scope, non-goals, and risks.
- Can be a full spec, PRD, issue, review finding, or approved user task.
- Should be reviewed at the right weight before implementation.

Spec:

- Use when product, domain, API, data, security, or user workflow decisions are still being shaped.
- Avoid for small clear tasks where it only restates the request.
- Review with `spec-review` when it exists or when acceptance criteria are unclear.

Plan:

- Owns file responsibility, TDD steps, verification commands, docs impact, rollback, and review checkpoints.
- Should link to the acceptance artifact instead of copying it. If the accepted task only exists in chat, the plan should include a short approved request anchor with scope, acceptance criteria, and non-goals or stop conditions.
- Review with `plan-review` for non-trivial or multi-step implementation.

This means the flow is not always "full spec -> huge plan -> code." For clear work it can be "accepted issue -> compact plan -> TDD."

## Review Routing

Use the lightest useful review:

- `spec-review`: full specs, PRDs, or unclear acceptance criteria.
- `plan-review`: non-trivial or multi-step implementation plans.
- `implementation-review`: substantial slices or review-fix passes.
- `architecture-review`: boundaries, DDD/SOLID, file size, over-abstraction.
- `security-review`: auth, secrets, crypto, deletion, sensitive data, destructive operations, untrusted input, injection, path traversal, command construction, parser/deserialization, SSRF, open redirects, data loss.
- `docs-review`: durable docs, handoffs, or documentation drift.
- `second-review`: required independent Codex review for high-risk security, data-loss, money, auth, crypto, deletion, or core-architecture work when available. Optional for specs, plans, broad diffs, weak tests, and user-requested independent checks.

In Claude Code, prefer the Codex plugin for `second-review` when available. If unavailable, use a clean Codex session, Codex CLI, or record the fallback and accepted risk.

Review routing exists to prevent both under-review and review overload. It should answer "which review protects this work?" rather than "how many reviews can we add?"

## Verification

Behavior changes should use `behavior-tdd`:

1. Write one failing behavior or regression test.
2. Confirm the expected failure.
3. Implement the smallest change.
4. Run focused verification.
5. Refactor only after green.

Production behavior changes may skip TDD only with explicit user approval and a recorded residual-risk reason. Generated code, pure docs, and mechanical config with no test harness can skip TDD with the reason noted in the final report.

Prefer automated project checks:

- focused tests
- full tests when risk justifies it
- typecheck
- lint
- build
- lefthook or other project hooks

Manual/browser QA is not a separate BB Harness phase. Use it only when automated tests and hooks cannot cover the behavior well.

## Scaffold Profiles

`project-scaffold` should propose the smallest profile that preserves restartable context.

- `minimal`: `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, `docs/AGENT_WORKFLOW.md`, `docs/CURRENT.md`.
- `product`: `minimal` plus testing strategy, specs/plans/reviews folders, roadmap, architecture, and domain model.
- `data-security`: `product` plus data and security models.
- `full`: `data-security` plus context map and a formal decision record template.

Dependency installation is user-managed by default. Agents may suggest commands and assumptions, but should not execute installs unless explicitly asked.

## Durable Docs

Project docs have separate ownership:

- `CONTEXT.md`: product identity, canonical vocabulary, current boundaries.
- `CONTEXT-MAP.md`: multiple contexts, apps, packages, or integrations.
- `docs/CURRENT.md`: current phase, active acceptance artifact/source, blocker, last verification, and next action.
- `docs/ROADMAP.md`: product goal, MVP, milestones, parking lot.
- `docs/ARCHITECTURE.md`: boundaries, layers, dependency rules, tradeoffs.
- `docs/DOMAIN_MODEL.md`: domain terms, invariants, workflows, entities, value objects.
- `docs/DATA_MODEL.md`: storage, retention, deletion, migration, backup.
- `docs/SECURITY_MODEL.md`: secrets, auth, permissions, trust boundaries, sensitive data.
- `docs/TESTING_STRATEGY.md`: TDD rules, test levels, verification commands, hooks.
- `docs/specs/`: temporary feature specs when needed.
- `docs/plans/`: compact implementation plans when needed.
- `docs/reviews/`: substantial review records and handoffs.
- `docs/DECISIONS/`: formal decision records only for hard-to-reverse, surprising tradeoffs.

README files in projects should stay user-facing and high-level.

## Hooks

The hook scripts are conservative building blocks:

- `block-dangerous-bash.sh`: destructive shell command checks and common shell-based secret reads.
- `protect-sensitive-read.sh`: read checks for `.env`, private keys, credentials, and secret files.
- `protect-sensitive-write.sh`: write checks for sensitive files and direct lockfile edits.
- `protect-sensitive-files.sh`: compatibility wrapper for tools that cannot split read/write hooks.
- `session-context.sh`: short session-start git context when supported.

Hooks are guardrails, not a sandbox. Wire them at the project level first, then promote globally only after they are quiet enough for daily use.

## Quick Starts

New project:

```text
Use bb-workflow.
Project state: new project.
Goal: <short product idea>.
Decide the workflow weight, next phase, scaffold needs, and approvals before editing.
```

Existing project:

```text
Use bb-workflow.
Task: <describe task>.
Read project instructions, current docs, tests, and relevant code. Report workflow weight, selected next skill, required artifact or approval, and next safe action before editing.
```

Small behavior change:

```text
Use behavior-tdd and ship-check for this small behavior change.
Run docs-sync only if behavior, architecture, testing, or user-facing behavior changes.
Change: <describe change>.
```

Non-trivial feature:

```text
Use bb-workflow first.
Feature: <describe feature>.
Use the relevant skills for acceptance artifact, review, compact plan, execute-plan for multi-slice work, behavior-tdd inside behavior-changing slices, docs sync, and ship check. Keep the workflow weight proportional to risk.
```

Bounded autonomous loop:

```text
Use bounded-loop.
Goal: <specific outcome>.
Allowed scope: <files/modules/docs/commands>.
Allowed autonomous actions: <exact file areas, commands, review/fix scope, and worker-agent use>.
Forbidden actions: <setup/dependencies/hooks/git history/deletes/deploys/etc>.
Iteration budget: <max loops or timebox>.
Verification gate: <test/typecheck/lint/build/manual check>.
Stop and ask if scope expands, verification fails twice for the same reason, or an unapproved product/domain/architecture/setup/destructive/git-history decision appears.
```

## Common Anti-Patterns

- Creating a full spec only to repeat a clear task.
- Writing a plan that copies the spec instead of constraining file changes.
- Running broad reviews because a review skill exists, not because the risk calls for it.
- Skipping TDD for behavior changes without recording why.
- Updating durable docs with unverified claims.
- Treating hooks as complete security controls.
- Delegating unresolved product, domain, architecture, dependency, setup, delete, or git-history decisions to a worker.

## Tool Policy

- Dependency installation is user-managed by default.
- Ask before setup, dependency execution, hooks, deletion, history rewrite, broad scope expansion, or unresolved product/domain/architecture decisions.
- Prefer TDD plus project hooks such as lefthook for repeatable checks.
- Use manual/browser QA only for behavior that tests and hooks cannot cover well.
- Keep long-lived project decisions in project docs, not chat history.
