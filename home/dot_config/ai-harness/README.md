# BB Harness

Central agent workflow, project templates, skills, reviewer agents, and conservative hooks managed
by chezmoi.

BB Harness turns ad-hoc Claude Code, Codex, and skill usage into a restartable side-project
workflow. The point is not to create documents for their own sake. The point is to make product
intent, acceptance criteria, implementation plan, verification evidence, review decisions, and
residual risk inspectable after the agent session ends.

This README is the human orientation guide. Agents should treat `AGENTS.md`, project-local
instructions, and `skills/*/SKILL.md` as the executable source of truth. The README does not
duplicate skill rules; it links to them.

## Design Goals

- Use the right workflow weight for the task.
- Prefer skills and plugins when they exist for the job.
- Keep durable context outside chat.
- Make non-trivial work reviewable before implementation.
- Make lightweight acceptance artifacts strong enough to protect implementation quality.
- Keep plans compact enough to execute without wasting context.
- Use TDD and project hooks for repeatable verification.
- Use independent review when risk justifies it, not as default ceremony.

## Layout

- `AGENTS.md`: shared global defaults for Codex-compatible agents.
- `skills/`: executable workflow skills. `bb-workflow` is the router.
- `claude-agents/`: Claude Code reviewer subagent definitions (thin dispatchers that delegate to
  the matching `skills/<name>-review/SKILL.md`).
- `hooks/`: conservative hook scripts. They are not wired globally by default.
- `templates/project/`: starter project instructions and durable docs.

## Link Strategy

Chezmoi installs `~/.config/ai-harness` as the source of truth, then links agent-facing locations
back to it:

- `~/.agents/AGENTS.md`
- `~/.codex/AGENTS.md`
- `~/.claude/CLAUDE.md`
- `~/.agents/skills/<skill-name>`
- `~/.claude/skills`
- `~/.claude/agents/<agent-name>.md`

Claude Code and Codex see the same workflow source. Tool-specific runtime settings still live under
their native config directories.

## Skill Separation Criteria

Use these rules before adding, splitting, or merging a skill. Apply all four together:

1. **Procedure length:** if the check fits in 1-3 bullet lines, keep it inline in the relevant
   review skill. Only split when the procedure needs grep commands, doc tracing, or multi-step
   decisions.
2. **Opt-in signal:** split only when the check applies to specific signals (domain-heavy, typed
   language, payment, sync) rather than all code. Always-applicable checks stay inline.
3. **Reuse:** split only when multiple skills/phases call the same check. Single-caller checks stay
   inline.
4. **ROI vs noise:** split only when leaving it inline would noticeably bloat unrelated projects'
   context. Otherwise the inline cost is cheaper than another skill file.

Adopted patterns (Hexagonal, CQRS, Event Sourcing, etc.) belong in `docs/ARCHITECTURE.md` or
`docs/DECISIONS/` of the project that adopts them, not in a global skill. Skills only encode
review/process steps that are useful across most projects.

DDD operational checks are kept inline in `architecture-review` because (a) BB Harness already
treats DDD as a first-class concern and (b) the inline summary stays under 6 lines. They become a
sub-skill only if that block grows past ~15 lines or if a domain-only project explicitly needs to
load them lazily.

### Phrasing Conventions

- Tables and brief threshold mentions use short forms: `5+ files`, `2+ modules`, `300/600 lines`.
- Prose uses long forms: `five or more files`, `two or more modules`, `300 lines / 600 lines`.
- The numeric thresholds themselves are canonical and identical in both forms.
- The independent reviewer is named `second-review` in cross-references. Codex is named only as
  the default integration inside `skills/second-review/SKILL.md`; other docs say "host agent's
  Codex integration when available."
- File and complexity thresholds (300/600 lines, 50-80-line functions, repeated-conditional
  triggers) are defined in `skills/architecture-review/SKILL.md` (File And Complexity Thresholds).
  Other docs reference that section rather than redefining numbers.

## Skill-First Posture

When the BB Harness is in use, skills are the workflow surface. Use them rather than recreating
their process in chat.

Skill-first does not mean "load every skill." It means:

- Start or resume with `bb-workflow` when the phase is unclear.
- Use a direct matching skill when the task clearly maps to one.
- Move from phase to phase through skills instead of improvising.
- Skip a relevant skill only when the task is clearly small/local or the skill would not materially
  protect the work.
- If a skill is skipped, record the reason briefly.

This keeps plugins and skills useful without turning every change into a heavyweight ritual.

## Workflow Model

BB Harness borrows deliberately from a few workflows:

- Superpowers: design before code, plan-backed execution, TDD, review, and finish checks.
- gstack: Think, Plan, Build, Review, Test, Ship, and Retro as an ordered delivery loop.
- Stacked PR practice: when history matters, commit and branch by logical review layer (see
  `execute-plan` Workspace Isolation and `ship-check` Finishing Options).
- Claude feature/review plugins: use focused reviewers and parallel specialists only when risk
  justifies them.

The BB version keeps those strengths but avoids making every task heavyweight. It uses the lightest
workflow that still protects correctness, evidence, safety, and project consistency.

Default non-trivial flow:

```text
bb-workflow
-> product-discovery when goal, users, MVP, or non-goals are unclear
-> pressure-test when assumptions are unclear or risky
-> domain-modeling when domain language or boundaries matter
-> acceptance artifact: spec, PRD, issue, review finding, or approved task
-> spec-review when a spec/PRD exists or acceptance criteria need shaping
-> compact implementation plan
-> required plan-review for non-trivial or multi-step plans
-> execute-plan for reviewed multi-slice plans (with workspace isolation when needed)
-> behavior-tdd for small/local work or each implementation slice
-> implementation-review and focused reviews as needed
-> second-review when high risk or independently requested
-> docs-sync
-> ship-check
-> retro-capture when memory candidates or retro insights surface
-> commit/stack gate when explicitly approved or required
```

For acceptance, spec, and plan ownership rules see `skills/write-spec/SKILL.md` (Application Rules)
and `skills/write-plan/SKILL.md`. The canonical Acceptance Brief fields live in `write-spec` and
are not re-listed elsewhere.

For workflow weight 4-tier definition see `skills/bb-workflow/SKILL.md` (Workflow Weight table).

## Skill Map

Mirror of `skills/bb-workflow/SKILL.md` Routing table for human orientation. The skill is the
source of truth; this table tracks it.

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
| Execute reviewed multi-slice plan (with workspace isolation) | `execute-plan` |
| Implement behavior through red-green-refactor | `behavior-tdd` |
| Diagnose a bug or regression | `bug-diagnosis` |
| Review whether tests prove acceptance behavior | `test-review` |
| Review architecture, DDD, SOLID, file size | `architecture-review` |
| Review implementation diff or completed slice | `implementation-review` |
| Review auth, secrets, crypto, deletion, untrusted input, data loss | `security-review` |
| Review durable docs and drift | `docs-review` |
| Request or record independent second review | `second-review` |
| Sync docs after behavior or workflow changes | `docs-sync` |
| Persist memory candidates or retro insights | `retro-capture` |
| Final handoff, verification, and residual risk check | `ship-check` |
| Continue bounded autonomous iterations | `bounded-loop` |

## Review Routing

Detailed routing lives in `skills/bb-workflow/SKILL.md` (Review Routing) and each individual
review skill. Use the lightest review that protects the work; do not run broad reviews because a
review skill exists.

For independent second review use the `second-review` skill, which defines Codex as the default
integration plus fallback procedure.

## Commit And Stack Gate

Detailed gate behavior lives in `skills/ship-check/SKILL.md` (Commit / Stack Gate). The harness
default is: commit/PR/stack actions only run with explicit user approval, project-local
instructions, or an approved bounded goal.

For stacked workflows see `skills/execute-plan/SKILL.md` (Workspace Isolation) and
`skills/ship-check/SKILL.md` (Finishing Options + Worktree Cleanup Provenance).

## Verification

Behavior changes use `behavior-tdd` (red-green-refactor with one failing public-interface test
first). Bug investigations start with `bug-diagnosis`, then return to `behavior-tdd` for the fix.

Prefer automated project checks (focused tests, full tests when risk justifies, typecheck, lint,
build, project hooks) over manual/browser QA. Manual checks are reserved for behavior that
automated checks cannot cover well.

Production behavior changes may skip TDD only with explicit user approval and a recorded
residual-risk reason. See `skills/behavior-tdd/SKILL.md` for full rules.

## Scaffold Profiles

`project-scaffold` proposes the smallest profile that preserves restartable context.

- `minimal`: `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, `docs/AGENT_WORKFLOW.md`, `docs/CURRENT.md`.
- `product`: `minimal` plus testing strategy, specs/plans/reviews folders, roadmap, architecture,
  and domain model.
- `data-security`: `product` plus data and security models.
- `full`: `data-security` plus context map and a formal decision record template.

Dependency installation is user-managed by default. Agents may suggest commands and assumptions, but
should not execute installs unless explicitly asked. For dependency add/replace/upgrade decisions,
project lefthook hooks should run language-appropriate audit tools (npm audit / pip-audit /
cargo audit / govulncheck) and `plan-review` records the rationale.

## Durable Docs

Project docs have separate ownership:

- `CONTEXT.md`: product identity, canonical vocabulary, current boundaries.
- `CONTEXT-MAP.md`: multiple contexts, apps, packages, or integrations.
- `docs/CURRENT.md`: current phase, active acceptance artifact/source, blocker, last verification,
  and next action.
- `docs/AGENT_WORKFLOW.md`: project-local overrides to global workflow; no duplication of
  `bb-workflow` rules.
- `docs/ROADMAP.md`: product goal, MVP, milestones, parking lot.
- `docs/ARCHITECTURE.md`: boundaries, layers, dependency rules, tradeoffs.
- `docs/DOMAIN_MODEL.md`: domain terms, invariants, workflows, entities, value objects.
- `docs/DATA_MODEL.md`: storage, retention, deletion, migration, backup.
- `docs/SECURITY_MODEL.md`: secrets, auth, permissions, trust boundaries, sensitive data.
- `docs/TESTING_STRATEGY.md`: TDD rules, test levels, verification commands, hooks.
- `docs/specs/`: temporary feature specs when needed.
- `docs/plans/`: compact implementation plans when needed.
- `docs/reviews/`: substantial review records, handoffs, and project-local retros.
- `docs/DECISIONS/`: formal decision records only for hard-to-reverse, surprising tradeoffs.

README files in projects should stay user-facing and high-level.

## Hooks

The hook scripts are conservative building blocks (see `hooks/README.md` for details and bypass
gaps):

- `block-dangerous-bash.sh`: destructive shell command checks and common shell-based secret reads.
- `protect-sensitive-read.sh`: read checks for `.env`, private keys, credentials, and secret files.
- `protect-sensitive-write.sh`: write checks for sensitive files and direct lockfile edits.
- `protect-sensitive-files.sh`: compatibility wrapper for tools that cannot split read/write hooks.
- `session-context.sh`: short session-start git context when supported.

Hooks are guardrails, not a sandbox. Do not assume they block all secret reads — `tail`, `head`,
`cp`, redirection, and language interpreters bypass them. Wire them at the project level first;
promote globally only after they are quiet enough for daily use.

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
- Adding a dependency without running the project's audit hooks or recording the decision.
- Stacking branches/PRs without distinct review concerns per branch.
- Saving "memory candidates" that are reconstructable from code or git log.
- Delegating unresolved product, domain, architecture, dependency, setup, delete, or git-history
  decisions to a worker.

## Tool Policy

- Dependency installation is user-managed by default.
- Ask before setup, dependency execution, hooks, deletion, history rewrite, broad scope expansion,
  or unresolved product/domain/architecture decisions.
- Prefer TDD plus project hooks such as lefthook for repeatable checks.
- Use manual/browser QA only for behavior that tests and hooks cannot cover well.
- Keep long-lived project decisions in project docs, not chat history.
