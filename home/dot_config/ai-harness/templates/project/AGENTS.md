# Project Agent Instructions

Document status: stub. TODO claims are not project truth yet. Non-TODO workflow, safety, and quality rules apply immediately.

## Project Shape

- Product goal: TODO
- Primary users: TODO
- MVP boundary: TODO
- Explicit non-goals: TODO
- Keep this file focused on instructions agents must follow every session.
- Move long-lived design details into `CONTEXT.md`, `CONTEXT-MAP.md`, and `docs/`.

## Required Reading

Before non-trivial edits, read:

- `CONTEXT.md`
- `docs/CURRENT.md`
- `docs/AGENT_WORKFLOW.md`
- relevant acceptance artifacts, plans, and review notes

Read conditionally when relevant:

- `CONTEXT-MAP.md`: multiple bounded contexts, apps, packages, or external integrations.
- `docs/ROADMAP.md`: product scope, milestones, or non-goals may change.
- `docs/ARCHITECTURE.md`: boundaries, dependencies, runtime surfaces, or module shape may change.
- `docs/DOMAIN_MODEL.md`: domain language, invariants, entities, value objects, or workflows may change.
- `docs/DATA_MODEL.md`: persistence, migration, retention, deletion, backup, import, or export may change.
- `docs/SECURITY_MODEL.md`: auth, permissions, secrets, trust boundaries, sensitive data, deletion, or crypto may change.
- `docs/TESTING_STRATEGY.md`: verification commands, test levels, or test strategy may change.

If a required or conditional doc is `stub`, use non-TODO rules as guidance and treat TODO claims as unknown until confirmed.

## Communication

- Act like a senior engineering peer: direct, specific, and concise.
- For reviews, lead with findings and evidence.
- For implementation, report changed files, verification, docs impact, and residual risk.
- Avoid generic praise, motivational filler, and long chat-only reasoning.

## Evidence And Safety

- Do not fabricate paths, commits, APIs, config keys, env vars, test results, tool behavior, or capabilities.
- Do not game verification by weakening assertions, narrowing coverage, skipping relevant checks, or changing tests to match broken behavior.
- Ask before changing behavior, API or UX, naming, persistence, auth, dependencies, config, compatibility, product scope, or domain language unless the approved plan already covers it.
- For infrastructure work, inspect environment, services, configs, and logs before changing behavior. Validate config before reload or restart; prefer reload when safe.
- Project-specific service names, deploy paths, reload commands, and environment details belong in this file or dedicated project docs.

## Architecture Rules

- Domain logic belongs in TODO.
- Application orchestration belongs in TODO.
- Infrastructure adapters belong in TODO.
- UI/interface logic belongs in TODO.
- Allowed dependency direction: TODO.
- Forbidden patterns:
  - TODO

## Quality Rules

- Prefer vertical slices over horizontal technical phases.
- Behavior tests should exercise public interfaces, user-visible flows, or stable domain boundaries.
- Source files over 300 lines require responsibility review.
- Source files over 600 lines require explicit approval, documented exception, or split plan.
- Use SOLID as concrete checks for responsibility, dependency direction, and interface size.
- Use DDD only where domain complexity justifies it.
- Do not introduce speculative abstractions.

## Development Workflow

For non-trivial work, select only the phases justified by workflow weight:

0. `bb-workflow` at session start, resume, or when the next workflow phase is unclear.
1. `product-discovery` for new product direction or major features.
2. `pressure-test` to pressure-test unclear ideas.
3. `domain-modeling` to align vocabulary and invariants.
4. `write-spec` to write the lightest acceptance artifact and vertical slices when needed.
5. `spec-review` for full specs, PRDs, or unclear acceptance criteria.
6. `write-plan` to create a compact implementation plan before non-trivial code edits.
7. `plan-review` before implementation.
8. `execute-plan` for reviewed multi-slice plans, Codex worker execution, or subagent work.
9. `behavior-tdd` for small/local behavior changes or each implementation slice.
10. `bounded-loop` only when goal, scope, allowed autonomous actions, iteration budget, verification gate, and stop conditions are explicit.
11. `implementation-review`, `architecture-review`, `docs-review`, `security-review`, or optional/required `second-review` as risk requires.
12. `docs-sync` after behavior, architecture, testing, security, or workflow changes.
13. `ship-check` before handoff, commit, PR, or release.

Small local changes may use `behavior-tdd` + `ship-check` only when no product, domain, or architecture decision changes. Reviewed multi-slice plans use `execute-plan` as the controller, with `behavior-tdd` inside each behavior-changing slice.

When delegating coding work to Codex or another worker agent, assign one vertical slice or disjoint write scope and review the result for acceptance compliance plus code quality before the next task.

Before using a bounded loop, stop and ask if scope expands, verification fails twice for the same reason, unapproved worker scope is needed, or setup/destructive/git-history actions are needed.

After each non-trivial phase, update `docs/CURRENT.md` when the active phase, active acceptance artifact/source, active plan, blocker, completed slice, verification evidence, or next action materially changes. If the same session continues immediately, update it once at the end of the phase.

Use a scope review when a change touches three or more files. Keep the small path if those files are bounded to one component/module and include direct tests, styles, fixtures, or docs for the same behavior.

Use the heavier workflow when a change touches product behavior, domain language, public API, persistence, auth/security, sync/concurrency, deletion, external integrations, two or more modules, or 300/600-line file thresholds.

## Verification

- Install: TODO
- Test: TODO
- Typecheck: TODO
- Lint: TODO
- Build: TODO
- E2E/manual: TODO
- Config validate/reload: TODO

Dependency installation is user-managed by default. Agents may suggest package or bootstrap commands, but must not run them unless explicitly asked to execute.

## Session Handoff

Before clearing a long session, write or update `docs/reviews/YYYY-MM-DD-<topic>-handoff.md` with:

- current goal
- completed slices
- open questions
- verification evidence
- next safe action

Also update `docs/CURRENT.md` before clearing or pausing.
