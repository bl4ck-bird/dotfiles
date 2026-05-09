# AI Harness

Central agent workflow, project templates, skills, reviewer agents, and conservative hooks managed by chezmoi.

This harness turns ad-hoc Claude Code, Codex, and skill usage into an inspectable development workflow for side projects.

## Layout

- `AGENTS.md` is the shared global instruction file for Codex-compatible agents.
- `skills/` contains reusable workflow skills for discovery, interview, DDD, specs, planning, TDD, execution, review, docs sync, and shipping.
- `claude-agents/` contains Claude Code reviewer subagent definitions.
- `hooks/` contains conservative hook scripts. They are not wired into global settings by default.
- `templates/project/` contains starter files for new side projects, including a lightweight `docs/CURRENT.md` status file.

## Link Strategy

Chezmoi installs `~/.config/ai-harness` as the source of truth, then links agent-facing locations back to it:

- `~/.agents/AGENTS.md`
- `~/.codex/AGENTS.md`
- `~/.claude/CLAUDE.md`
- `~/.agents/skills/<skill-name>`
- `~/.claude/skills`
- `~/.claude/agents/<agent-name>.md`

Claude Code and Codex see the same workflow source. Claude-specific plugin settings still live under `~/.claude`, and Codex runtime settings still live under `~/.codex`.

## Workflow Model

Use this as the default lifecycle for non-trivial side-project work:

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

The workflow is deliberately heavier than a one-shot prompt. The goal is not more documents for their own sake. The goal is that a human can later inspect the product goal, domain language, implementation plan, review findings, and verification evidence without reconstructing an agent session.

## Skill Map

| Phase | Skill | Purpose |
| --- | --- | --- |
| Session entry | `using-ai-harness` | Choose workflow weight, next phase, and required artifacts. |
| Start a repo | `project-scaffold` | Create or refresh project instructions and durable docs. |
| Brainstorming / product thinking | `product-discovery` | Clarify goal, users, MVP, non-goals, risks, success metrics. |
| Pressure test | `critical-interview` | Ask one critical question at a time until major ambiguity is resolved. |
| Domain design | `domain-modeling` | Align terms, bounded contexts, invariants, ADR candidates. |
| Spec writing | `spec-to-slices` | Turn resolved context into spec and vertical slices. |
| Planning | `implementation-planning` | Create file-mapped TDD implementation plan. |
| Coding | `tdd-workflow` | Implement public behavior one test at a time through red-green-refactor. |
| Parallel work | `agentic-execution` | Execute plan slices with Codex workers, subagents, and review checkpoints. |
| Bounded automation | `bounded-goal-loop` | Continue toward an approved goal inside explicit allowed actions and stop conditions. |
| Bugs | `bug-diagnosis` | Reproduce, hypothesize, instrument, fix with regression tests. |
| Architecture | `architecture-review` | Review DDD, SOLID, module boundaries, complexity, file size. |
| Review | `review-gate` | Run self/subagent review and independent Codex review. |
| Docs | `docs-sync` | Update durable docs after plans or implementation. |
| Finish | `ship-review` | Final diff, test, docs, review, and risk check. |

## Workflow Weight Rules

Use the lightest workflow that still protects the project:

- Tiny/local: bounded files in one component or module, no product/domain/API/data/security decision. Tests, styles, and docs that directly support the same change do not make it non-trivial by themselves. Use direct edit or `tdd-workflow` plus `ship-review`.
- Scope review: three or more files, or uncertainty about blast radius. Decide whether the small path still fits before escalating.
- Non-trivial: product behavior, user workflow, domain language, public API, persistence, auth/security, sync/concurrency, deletion, or external integration. Use spec, plan, review, and docs gates.
- Risky/substantial: core architecture, money, crypto, data loss, broad refactor, weak tests, five or more files, two or more modules, or 300/600-line file thresholds. Require `review-gate` and independent second review when available.

## New Project Workflow

1. Open or create the project directory. If git, stack bootstrapping, hooks, or initial commit are not decided yet, let `project-scaffold` ask through its decision gate.
2. Start with the harness entry skill:

```text
Use using-ai-harness.
Project state: new project.
Goal: <short product idea>.
Decide the workflow weight, next phase, scaffold needs, and user approvals before editing.
```

3. Ask an agent to run the scaffold:

```text
Use project-scaffold for this new side project.
Product idea: <short idea>.
Recommend a scaffold profile: minimal, product, data-security, or full.
Before creating or changing anything, ask me to approve each scaffold decision: git init, scaffold profile and exact files, .claude/.codex/.agents dirs, lefthook, package/bootstrap commands to suggest, package/bootstrap execution if explicitly requested, and initial commit.
Do not overwrite existing files without showing me the diff first.
Dependency installation is user-managed by default. Suggest commands and assumptions, but do not execute installs unless I explicitly ask you to run them.
```

4. Run brainstorming / product discovery:

```text
Use product-discovery.
Help me define the product goal, target users, MVP boundary, explicit non-goals, success metrics, and first milestone for this project.
Ask only the questions needed to remove real ambiguity.
```

5. Run critical interview:

```text
Use critical-interview.
Grill this product direction before we write a spec.
Ask one question at a time, recommend an answer, and stop when the important decision branches are resolved.
```

6. Run domain modeling:

```text
Use domain-modeling.
Read AGENTS.md, CONTEXT.md, CONTEXT-MAP.md, docs/DOMAIN_MODEL.md, and docs/DECISIONS.
Resolve overloaded terms, define bounded contexts and invariants, and propose ADRs only for hard-to-reverse tradeoffs.
```

7. Write the first spec and slices:

```text
Use spec-to-slices.
Turn the resolved context into a light spec in docs/specs/YYYY-MM-DD-<feature>.md.
Then split it into vertical slices with AFK/HITL labels, acceptance criteria, tests, docs impact, and review needs.
```

8. Review the spec:

```text
Use review-gate on docs/specs/YYYY-MM-DD-<feature>.md.
Run a primary spec review for product goal, MVP boundary, acceptance criteria, vertical slices, domain language, testing decisions, docs impact, and open risks.
Ask Codex for independent second review if risk requires it.
```

9. Plan and execute:

```text
Use implementation-planning.
Create docs/plans/YYYY-MM-DD-<feature>.md with spec review reference, file responsibility mapping, TDD steps, verification commands, docs impact, and review checkpoints.
```

```text
Use agentic-execution.
Execute the approved plan task by task. Use tdd-workflow for behavior changes.
When using Codex or another worker agent, assign one vertical slice or disjoint write scope, pass artifact paths instead of chat history, and review for spec compliance plus code quality before the next task.
Run review-gate after each substantial slice.
```

10. Finish:

```text
Use docs-sync, then review-gate, then ship-review.
Include verification evidence and residual risk.
```

## Existing Project Workflow

Use this when adding the harness to a repo that already has code:

```text
Use project-scaffold for an existing project.
First inspect README, package manifests, tests, docs, AGENTS.md/CLAUDE.md, and the main source directories.
Do not overwrite project conventions. Propose missing harness docs and update only the files I approve.
```

Then run a short context pass:

```text
Use domain-modeling.
Infer the current product goal, main bounded contexts, vocabulary, invariants, and architecture decisions from the repo.
Create or update CONTEXT.md, CONTEXT-MAP.md, docs/DOMAIN_MODEL.md, and docs/ARCHITECTURE.md.
Mark uncertainties explicitly instead of inventing facts.
```

For the next feature, use the normal feature workflow from spec onward. Existing projects should not be force-fit into a perfect DDD structure. The first goal is shared context and safe boundaries, not a rewrite.

## Current Work Tracking

Use `docs/CURRENT.md` as the lightweight progress pointer:

- update it at phase boundaries
- update it after completed implementation slices
- update it before clearing or pausing context
- keep it short; specs, plans, reviews, ADRs, and roadmap remain the durable source of detail

## Feature Workflow

Use this for meaningful feature work:

```text
Use using-ai-harness first, then use only the needed skills from critical-interview, domain-modeling, spec-to-slices, review-gate, implementation-planning, agentic-execution, docs-sync, and ship-review for this feature.
Feature idea: <feature>.
Prefer vertical slices. Keep the MVP small. Require Codex second review before implementation and before ship if the plan or diff is risky.
```

Let the harness continue the workflow:

```text
Use using-ai-harness.
Continue the project workflow from docs/CURRENT.md.
After each non-trivial phase, update docs/CURRENT.md and recommend exactly one next phase with a concise confirmation question.
Do not auto-advance across setup, dependency execution, hook, delete, git-history, product, domain, architecture, data, or security decisions unless I approved a bounded goal covering them.
```

If the work is small and local, shorten it:

```text
Use tdd-workflow and ship-review for this small behavior change.
Also run docs-sync only if behavior, architecture, testing, or user-facing behavior changes.
```

## Bounded Goal Loop

Use this when the target is clear enough for limited automation, but not broad enough to hand over the whole project:

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

Good targets:

- Fix all findings from an approved review within named files.
- Complete one approved implementation-plan slice.
- Iterate on docs until review-gate finds no material drift.
- Investigate a failing test with a bounded hypothesis budget.

Do not use it for product discovery, broad refactors, dependency changes, git setup, hook installation, deletes, history rewrites, or open-ended "improve everything" requests.

## Bug Workflow

```text
Use bug-diagnosis.
Reproduce the bug first, write or identify a failing regression test, form falsifiable hypotheses, fix the root cause, rerun the repro, then use review-gate and ship-review.
Bug: <description>.
```

Do not let the agent patch from vibes. A bug is not ready to fix until there is a reproduction loop or a clear explanation of why reproduction is impossible.

## Refactor Workflow

```text
Use architecture-review first.
Identify refactor candidates that improve testability, module depth, domain clarity, or file responsibility.
Do not change behavior. Propose small vertical refactor slices and ask before editing.
```

If approved:

```text
Use implementation-planning and tdd-workflow for the refactor.
Keep tests green throughout and run review-gate before ship.
```

## Prompt Cookbook

Start a session:

```text
Use using-ai-harness.
Task: <what you want to do>.
Read AGENTS.md, CONTEXT.md, docs/CURRENT.md, docs/AGENT_WORKFLOW.md, current docs/specs and docs/plans relevant to this task, plus data/security docs when relevant.
Summarize the workflow weight, current state, open decisions, and the next safe action before editing.
```

Ask for a spec review:

```text
Use review-gate on docs/specs/<spec>.md.
Run a primary spec review for product goal, MVP boundary, acceptance criteria, vertical slices, domain language, testing decisions, docs impact, and open risks.
Ask Codex for independent second review if risk requires it.
```

Ask for a plan review:

```text
Use review-gate on docs/plans/<plan>.md.
Confirm the spec review exists or accepted risk is recorded. Then review for spec coverage, file responsibility, TDD granularity, DDD/SOLID fit, file size risk, docs impact, and missing verification.
Then request independent Codex review if available.
```

Ask for Codex second review from Claude Code:

```text
Use the Codex plugin for an independent second review of this spec/plan/diff.
Ask Codex to focus on hidden assumptions, architecture drift, missing tests, DDD/SOLID violations, oversized files, and docs drift.
```

Independent second review fallback:

```text
Use a clean Codex session or Codex CLI as an independent reviewer.
Read AGENTS.md, CONTEXT.md, docs/CURRENT.md, docs/AGENT_WORKFLOW.md, the relevant spec/plan/review notes, and the diff or changed file list.
Return findings first with P0-P3 severity, evidence, suggested fixes, and pass/pass-with-follow-ups/blocked.
Do not rely on the primary agent's chat summary except as a pointer to artifacts.
```

If neither plugin nor separate Codex session is available, record:

```text
Second review: unavailable.
Reason: <plugin unavailable / no network / no clean session / user skipped>.
Compensating review: <self-review / reviewer subagent / manual human review>.
Accepted risk: <what could be missed>.
```

Do not ship P0/P1-risk work without explicit user acceptance when independent review is unavailable.

Ask for implementation:

```text
Use agentic-execution for docs/plans/<plan>.md.
Execute one vertical slice at a time. For behavior changes, use tdd-workflow. After each substantial slice, run review-gate and update the plan checklist.
Update docs/CURRENT.md after each completed slice.
```

Ask for finalization:

```text
Use docs-sync and ship-review.
Check git status, changed files, tests, docs, review records, and residual risk. Do not claim done without verification evidence.
```

## When To Clear Or Restart A Session

Clear context when the agent has enough durable artifacts to restart safely:

- After product discovery and critical interview are summarized into roadmap, context, and spec.
- After a spec is approved and before implementation planning, if the conversation included lots of brainstorming.
- After a detailed plan is written and reviewed, before a long implementation session.
- After several vertical slices are complete and the remaining context is mostly old diffs or logs.
- After fixing review findings, before final ship review, if the session is cluttered.

Before clearing, ask the agent to write a handoff:

```text
Write a handoff note in docs/reviews/YYYY-MM-DD-<topic>-handoff.md.
Include current goal, relevant docs, decisions made, open questions, completed slices, verification evidence, known risks, and next action.
Update docs/CURRENT.md before clearing.
```

New session prompt:

```text
Resume from docs/reviews/<handoff>.md.
Read AGENTS.md, CONTEXT.md, docs/CURRENT.md, docs/AGENT_WORKFLOW.md, the current spec, the current plan, and recent review notes.
Confirm what is done, what remains, and what you will do next.
```

## Document Status

Use explicit status labels so agents do not mistake scaffolding for truth:

- `stub`: template exists. TODO claims are not authoritative; non-TODO workflow, safety, and quality rules still apply.
- `draft`: partially confirmed by the user or repo, open questions remain.
- `ready`: current source of truth until a later reviewed change updates it.

When reading docs, prefer `ready` over `draft`. For `stub` docs, follow non-TODO workflow/safety rules and treat TODO claims as unknown.

## Document Ownership

- `README.md`: human onboarding and product overview.
- `AGENTS.md`: project-specific agent rules that must be loaded every session.
- `CONTEXT.md`: bounded-context glossary and core domain language.
- `CONTEXT-MAP.md`: relationships between bounded contexts or subsystems.
- `docs/AGENT_WORKFLOW.md`: project-specific workflow commands and phase rules.
- `docs/CURRENT.md`: current phase, active artifacts, blockers, last verification, and next action.
- `docs/ROADMAP.md`: MVP, later phases, non-goals, open product decisions.
- `docs/ARCHITECTURE.md`: system boundaries, dependency direction, quality rules.
- `docs/DOMAIN_MODEL.md`: entities, value objects, invariants, domain workflows.
- `docs/DATA_MODEL.md`: persisted data, derived data, migrations, retention, deletion, backups.
- `docs/SECURITY_MODEL.md`: secrets, auth, permissions, trust boundaries, sensitive data handling.
- `docs/TESTING_STRATEGY.md`: test levels, required commands, TDD rules.
- `docs/DECISIONS/`: ADRs for hard-to-reverse or surprising tradeoffs.
- `docs/specs/`: feature specs and light PRDs.
- `docs/plans/`: implementation plans.
- `docs/reviews/`: review records, handoffs, and risk notes.

## Tool Policy

Use local project docs and harness skills as the workflow source. External tools can help with execution, review, browsing, or stack-specific work, but durable decisions belong in `CONTEXT.md`, `docs/`, specs, plans, reviews, and ADRs.

Recommended default:

- Claude Code can be the main planning/scaffolding agent when useful.
- Codex can be an independent second reviewer for specs, plans, diffs, and stuck debugging.
- Stack-specific hooks and test checks belong at the project level, usually with `lefthook`.
