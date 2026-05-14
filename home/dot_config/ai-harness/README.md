# BB Harness

Central agent workflow, project templates, skills, reviewer agents, and conservative hooks — managed by chezmoi.

Turns ad-hoc Claude Code / Codex / skill usage into a restartable side-project workflow. Goal: product intent, acceptance criteria, plan, verification, review decisions, and residual risk remain inspectable after the agent session ends.

This README is for humans. Agents treat `AGENTS.md`, project-local instructions, and `skills/*/SKILL.md` as the executable source of truth. The README links to skills; it does not duplicate their rules.

## Design Goals

- Right workflow weight for the task.
- Skills/plugins over ad-hoc when they exist.
- Durable context outside chat.
- Non-trivial work reviewable before implementation.
- Lightweight acceptance artifacts strong enough to protect quality.
- Compact plans that execute without wasting context.
- TDD + project hooks for repeatable verification.
- Independent review when risk justifies it, not as default ceremony.

## Adapts To The Project

Domain / DDD / security depth is **opt-in by file presence**:

- With `CONTEXT.md` or `docs/DOMAIN_MODEL.md`: `code-quality-review` runs DDD checks; `write-spec`/`write-plan` Self-Review verifies domain alignment.
- Without those docs: those checks self-skip. Harness still works as a general TDD/review workflow.
- Security depth (`security-review`, `second-review`) triggers only when the diff touches a security-sensitive surface or High-Risk Surface.
- Scaffold profiles (`minimal` → `product` → `data-security` → `full`) let a project pick durable-doc depth.

Small CLI = TDD + spec-compliance + code-quality + ship. Domain-heavy app = same skills + DDD checks.

## Layout

- `AGENTS.md` — shared global defaults for Codex-compatible agents.
- `skills/` — executable workflow skills. `using-bb-harness` is bootstrap + router.
- `claude-agents/` — Claude Code reviewer subagents (thin dispatchers delegating to `skills/<name>-review/SKILL.md`). Four reviewers: `spec-compliance-reviewer`, `code-quality-reviewer`, `security-reviewer`, `second-reviewer`. `receiving-review` is implementer-side behavior, not a subagent.
- `hooks/` — conservative hook scripts. Not wired globally by default.
- `templates/project/` — starter project instructions and durable docs. The single `project/` nest leaves room for future template categories (e.g. `library/`, `service/`, `skill/`) without restructuring.

## Link Strategy

Chezmoi installs `~/.config/ai-harness` as the source of truth, then links agent-facing locations back:

- `~/.codex/AGENTS.md` → `~/.config/ai-harness/AGENTS.md`
- `~/.claude/CLAUDE.md` → `~/.config/ai-harness/AGENTS.md`
- `~/.gemini/GEMINI.md` → `~/.config/ai-harness/AGENTS.md`  *(one file serves all three)*
- `~/.codex/skills` → `~/.config/ai-harness/skills`
- `~/.claude/skills` → `~/.config/ai-harness/skills`
- `~/.gemini/skills` → `~/.config/ai-harness/skills`
- `~/.claude/agents/<agent>.md` → `~/.config/ai-harness/claude-agents/<agent>.md`

Tool-specific runtime settings stay under their native config directories.

## Skill Separation Criteria

Apply all four before adding/splitting/merging a skill:

1. **Procedure length** — fits 1-3 bullets? Stay inline. Split only for grep commands, doc tracing, or multi-step decisions.
2. **Opt-in signal** — split only when the check applies to specific signals (domain-heavy, typed language, payment, sync). Always-applicable checks stay inline.
3. **Reuse** — split only when multiple skills/phases call the same check.
4. **ROI vs noise** — split only when inline would noticeably bloat unrelated projects' context.

Adopted patterns (Hexagonal, CQRS, Event Sourcing) belong in `docs/ARCHITECTURE.md` or `docs/DECISIONS/` of the adopting project — not in a global skill.

DDD operational checks, SOLID, file/complexity thresholds, Coverage Matrix, and durable docs drift checks are SSOT-owned by `skills/code-quality-review/SKILL.md`. Upstream variants (domain alignment, SOLID at plan time) are inlined into `write-spec` / `write-plan` Self-Review.

### Phrasing Conventions

- Tables/brief mentions: short forms (`5+ files`, `300/600 lines`).
- Prose: long forms (`five or more files`, `300 lines / 600 lines`).
- Numeric thresholds are canonical and identical in both forms.
- The independent reviewer is `second-review` in cross-references; Codex is named only inside `skills/second-review/SKILL.md` as the default integration.
- File/complexity thresholds defined in `skills/code-quality-review/SKILL.md` (File And Complexity Thresholds). Other docs reference, not redefine.

## Reviewer Pair Pattern (maintenance)

Two reviewer types exist in parallel for `code-quality-review` and `spec-compliance-review`:

| File | Role |
| --- | --- |
| `skills/subagent-driven-development/<name>-reviewer-prompt.md` | Canonical reviewer prompt — used by all hosts via `general-purpose` fallback. Self-contained. |
| `claude-agents/<name>-reviewer.md` | Claude Code named-subagent definition — Claude-only, lives at `~/.claude/agents/` via symlink. Condensed mirror of the canonical prompt. |

When updating reviewer rules (severity, scope guard, output format, follow-on logic, etc.), update **both** files. Other hosts (Codex, Gemini) ignore `claude-agents/` entirely — sdd templates are sufficient for them. `security-reviewer` and `second-reviewer` exist only in `claude-agents/` because their sdd dispatch is handled by `code-quality-reviewer-prompt.md` follow-on logic.

## Skill-First Posture

When BB Harness is in use, skills are the workflow surface. Skill-first ≠ "load every skill":

- Start/resume with `using-bb-harness` when phase is unclear.
- Use a direct matching skill when the task clearly maps to one.
- Move phase-to-phase through skills, not improvisation.
- Skip a relevant skill only when the task is clearly small/local or the skill would not materially protect the work — record the reason.

## Workflow Model

Borrows from: Superpowers (design → plan → TDD → review → finish), gstack (Think/Plan/Build/Review/Test/Ship/Retro), stacked PR practice (commit/branch by logical review layer — see `subagent-driven-development` Workspace Isolation and `ship-check` Finishing Options), Claude feature/review plugins (focused reviewers when risk justifies).

Default non-trivial flow:

```text
using-bb-harness
-> product-discovery (goal/users/MVP/non-goals unclear)
-> pressure-test (assumptions unclear or risky)
-> domain-modeling (domain language or boundaries matter)
-> write-spec (Self-Review: Product Clarity + Domain Alignment)
-> write-plan (Self-Review: Plan Hygiene + Architecture Soundness)
-> subagent-driven-development as controller
   per task:
     implementer subagent (test-driven-development inside)
     -> spec-compliance-review subagent (binary ✅/❌)
     -> code-quality-review subagent (Yes / With fixes / No)
     -> security-review subagent (when triggered)
     -> second-review (Codex) (High-Risk Surface or independent double-check)
     -> receiving-review (between reviewer feedback and next fix)
-> docs-sync
-> ship-check
-> commit/stack gate (only when explicitly approved/required)
```

Acceptance/spec/plan ownership: see `skills/write-spec/SKILL.md` (Application Rules) and `skills/write-plan/SKILL.md`. Canonical Acceptance Brief fields live in `write-spec`.

Workflow weight 4-tier definition: `skills/using-bb-harness/SKILL.md` (Workflow Weight).

## Skill Map

Mirror of `skills/using-bb-harness/SKILL.md` Routing. Skill is the source of truth.

| Situation | Skill |
| --- | --- |
| Choose workflow weight and next phase | `using-bb-harness` |
| Start or refresh project instructions | `project-scaffold` |
| Product direction unclear | `product-discovery` |
| Assumptions need challenge | `pressure-test` |
| Domain language or boundaries matter | `domain-modeling` |
| Create acceptance artifact and slices (includes Self-Review) | `write-spec` |
| Create compact implementation plan (includes Self-Review) | `write-plan` |
| Execute reviewed multi-task plan (host supports subagents) | `subagent-driven-development` |
| Execute reviewed plan inline (no subagents, or 1-3 small tasks) | `executing-plans-inline` |
| Set up isolated worktree before execution | `using-git-worktrees` |
| Implement behavior through red-green-refactor | `test-driven-development` |
| Verify completion claims with fresh evidence | `verification-before-completion` |
| Diagnose bug or regression | `bug-diagnosis` |
| 2+ independent investigations/repros/research concurrently | `dispatching-parallel-agents` |
| Verify implementation matches acceptance (binary) | `spec-compliance-review` |
| Review code quality, DDD/SOLID, size, tests, docs drift, prod readiness | `code-quality-review` |
| Review auth, secrets, crypto, deletion, untrusted input, data loss | `security-review` |
| Independent double-check (Codex by default) | `second-review` |
| Process reviewer feedback (verify, push back, apply one at a time) | `receiving-review` |
| Sync docs after behavior or workflow changes | `docs-sync` |
| Final handoff, verification, residual risk check | `ship-check` |
| Continue bounded autonomous iterations | `bounded-loop` |

## Review Routing

Detailed routing: `skills/using-bb-harness/SKILL.md` (Review Routing) and each review skill. Use the lightest review that protects the work.

For independent second review: `second-review` skill (Codex default + fallback procedure).

## Commit And Stack Gate

Detailed behavior: `skills/ship-check/SKILL.md` (Commit / Stack Gate). Default: commit/PR/stack actions run only with explicit user approval, project-local instructions, or an approved bounded goal.

Stacked workflows: `skills/subagent-driven-development/SKILL.md` (Workspace Isolation) + `skills/ship-check/SKILL.md` (Finishing Options + Worktree Cleanup Provenance).

## Verification

Behavior changes use `test-driven-development` (red-green-refactor, one failing public-interface test first). Bugs start with `bug-diagnosis`, then return to TDD for the fix.

Prefer automated project checks (focused tests, full tests when risk justifies, typecheck, lint, build, project hooks) over manual/browser QA. Manual checks for behavior automated checks can't cover well.

Production behavior changes may skip TDD only with explicit user approval + recorded residual-risk reason. Full rules: `skills/test-driven-development/SKILL.md`.

## Scaffold Profiles

`project-scaffold` proposes the smallest profile that preserves restartable context.

- `minimal` — `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, `docs/AGENT_WORKFLOW.md`, `docs/CURRENT.md`.
- `product` — `minimal` + testing strategy, specs/plans/reviews folders, roadmap, architecture, domain model.
- `data-security` — `product` + data and security models.
- `full` — `data-security` + context map + formal decision record template.

Dependency installation is user-managed by default. Agents may suggest commands but should not execute installs unless asked. For dep add/replace/upgrade, project lefthook hooks should run language-appropriate audit tools (npm audit / pip-audit / cargo audit / govulncheck); `write-plan` Self-Review records the rationale.

## Durable Docs

Separate ownership:

- `CONTEXT.md` — product identity, canonical vocabulary, current boundaries.
- `CONTEXT-MAP.md` — multiple contexts, apps, packages, integrations.
- `docs/CURRENT.md` — phase, active acceptance artifact/source, blocker, last verification, next action.
- `docs/AGENT_WORKFLOW.md` — project-local overrides; no duplication of `using-bb-harness` rules.
- `docs/ROADMAP.md` — product goal, MVP, milestones, parking lot.
- `docs/ARCHITECTURE.md` — boundaries, layers, dependency rules, tradeoffs.
- `docs/DOMAIN_MODEL.md` — domain terms, invariants, workflows, entities, value objects.
- `docs/DATA_MODEL.md` — storage, retention, deletion, migration, backup.
- `docs/SECURITY_MODEL.md` — secrets, auth, permissions, trust boundaries, sensitive data.
- `docs/TESTING_STRATEGY.md` — TDD rules, test levels, verification commands, hooks.
- `docs/specs/` — temporary feature specs.
- `docs/plans/` — compact implementation plans.
- `docs/reviews/` — substantial review records, handoffs, project-local retros.
- `docs/DECISIONS/` — formal decision records only for hard-to-reverse, surprising tradeoffs.

Project README files stay user-facing and high-level.

## Hooks

Conservative building blocks (see `hooks/README.md` for details and bypass gaps):

- `block-dangerous-bash.sh` — destructive shell command checks + common shell-based secret reads.
- `protect-sensitive-read.sh` — read checks for `.env`, private keys, credentials, secret files.
- `protect-sensitive-write.sh` — write checks for sensitive files + direct lockfile edits.
- `protect-sensitive-files.sh` — compatibility wrapper for tools that can't split read/write hooks.
- `session-context.sh` — short session-start git context when supported.

Hooks are guardrails, not a sandbox. `tail`, `head`, `cp`, redirection, and language interpreters bypass them. Wire at project level first; promote globally only after they're quiet enough for daily use.

## Quick Starts

New project:

```text
Use using-bb-harness.
Project state: new project.
Goal: <short product idea>.
Decide workflow weight, next phase, scaffold needs, approvals before editing.
```

Existing project:

```text
Use using-bb-harness.
Task: <describe>.
Read project instructions, current docs, tests, relevant code. Report workflow weight, next skill, required artifact/approval, next safe action before editing.
```

Small behavior change:

```text
Use test-driven-development and ship-check.
Run docs-sync only if behavior/architecture/testing/user-facing behavior changes.
Change: <describe>.
```

Non-trivial feature:

```text
Use using-bb-harness first.
Feature: <describe>.
Use relevant skills for acceptance artifact, review, compact plan, subagent-driven-development for multi-slice, TDD inside behavior-changing slices, docs sync, ship check. Keep weight proportional to risk.
```

Bounded autonomous loop:

```text
Use bounded-loop.
Goal: <specific outcome>.
Allowed scope: <files/modules/docs/commands>.
Allowed autonomous actions: <exact file areas, commands, review/fix scope, worker-agent use>.
Forbidden actions: <setup/dependencies/hooks/git history/deletes/deploys>.
Iteration budget: <max loops or timebox>.
Verification gate: <test/typecheck/lint/build/manual>.
Stop and ask if scope expands, verification fails twice for the same reason, or an unapproved product/domain/architecture/setup/destructive/git-history decision appears.
```

## Common Anti-Patterns

- Full spec for a clear task.
- Plan that copies the spec instead of constraining file changes.
- Broad reviews because the skill exists, not because risk calls for it.
- Skipping TDD for behavior changes without recording why.
- Updating durable docs with unverified claims.
- Treating hooks as complete security controls.
- Adding a dependency without running audit hooks or recording the decision.
- Stacking branches/PRs without distinct review concerns per branch.
- "Memory candidates" reconstructable from code or git log.
- Delegating unresolved product/domain/architecture/dependency/setup/delete/history decisions to a worker.

## Tool Policy

- Dependency installation is user-managed by default.
- Ask before: setup, dependency execution, hooks, deletion, history rewrite, broad scope expansion, unresolved product/domain/architecture decisions.
- Prefer TDD + project hooks (lefthook) for repeatable checks.
- Manual/browser QA only for behavior tests and hooks can't cover well.
- Long-lived project decisions in project docs, not chat history.
