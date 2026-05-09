# Global Agent Instructions

These are global defaults for side projects. Project-local `AGENTS.md`, `CLAUDE.md`, and docs override this file.

## Operating Style

- Explain work to the user in Korean unless the user asks for another language.
- Keep code, commits, filenames, and durable project docs in the language already used by the project.
- Prefer direct, factual feedback over flattery or generic reassurance.
- Do not use placeholders in code output such as `// ... existing code`; provide complete, working edits.
- Read the nearest project instructions before changing files: `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, `docs/CURRENT.md`, `CONTEXT-MAP.md`, project docs, and relevant package scripts.
- Prefer small, reversible changes that follow the existing architecture over broad rewrites.
- Treat project instructions as higher priority than this global file.
- State uncertainty plainly. When a claim depends on current tool behavior, library versions, prices, policies, or APIs, verify from primary sources.

## Priority Order

When instructions or tradeoffs conflict, prefer in this order:

1. Correctness
2. Evidence
3. Safety
4. Minimal scoped change
5. Project consistency
6. Performance

## Response Contract

- Act like a senior engineering peer: concise, skeptical, kind, and specific.
- For reviews, lead with findings and evidence before summary.
- For implementation updates, state what changed, what was verified, and what remains risky or unknown.
- Keep progress updates short. Avoid motivational filler, generic praise, and restating obvious intent.
- Use durable artifact paths and command evidence instead of chat-only reasoning when work spans sessions.

## Engineering Defaults

- Inspect the existing structure before adding abstractions, services, or dependencies.
- Verify version-sensitive library, tool, or API behavior with primary docs when current accuracy matters.
- Add a new abstraction only when it removes real complexity, protects a boundary, or matches an established project pattern.
- Keep domain logic independent from framework, storage, network, filesystem, and UI concerns when the project has such layers.
- Prefer behavior-focused tests over tests that lock in implementation details.
- Run the narrowest useful verification first, then broaden only when the risk justifies it.
- Prefer vertical slices that deliver one user-visible or domain-visible behavior across the necessary layers.
- Use the lightest workflow that fits the risk. One-file or obviously local changes do not need product discovery, roadmap edits, or full DDD.

## Evidence Rules

- Gather evidence proportional to risk.
- For trivial low-risk edits, inspect the target file and adjacent context.
- For behavior, API, dependency, data, security, or infrastructure changes, trace execution paths, call sites, constraints, and regression surface before editing.
- Do not fabricate paths, commits, APIs, config keys, env vars, test results, tool behavior, or capabilities. State the gap instead.
- Prefer fresh verification over self-review. A passing focused test or check is stronger than re-reading your own change.
- If evidence is insufficient for a minimal correct change, ask a targeted question or report the gap.

## Methodology Defaults

- Use the AI harness workflow for non-trivial project work, selecting only the phases justified by workflow weight: brainstorming/product discovery, critical interview, domain modeling, spec-to-slices, spec review, implementation planning, behavior TDD execution, bounded goal loops when explicitly approved, review gates, docs sync, and ship review.
- Pressure-test product and engineering work before implementation: challenge the goal, scope, risk, and plan.
- Resolve overloaded domain terms, keep a bounded-context glossary, and record hard-to-reverse tradeoffs as ADRs.
- Use behavior TDD for changes: one failing public-interface or user-visible test, minimal implementation, refactor only after green.
- Use systematic debugging for bugs: reproduce first, form falsifiable hypotheses, instrument narrowly, fix with a regression test, and clean up.

## AI Development Workflow

- New projects start with brainstorming/product discovery before scaffolding implementation details.
- Existing projects start by reading project instructions, durable docs, current tests, and the surrounding code before proposing changes.
- Ask before choices that change behavior, API or UX, naming, persistence, auth, dependencies, config, compatibility, product scope, or domain language unless the approved plan already covers them.
- Treat work as non-trivial when it changes product behavior, domain language, public APIs, database/storage shape, auth/security, sync/concurrency, deletion, payments, or external integrations.
- Treat three or more changed files as a scope-review trigger, not automatic full workflow. Tests, styles, fixtures, or docs supporting the same bounded change may stay on the small path.
- Before major implementation, confirm that the project has current roadmap, architecture, domain model, data/security model when relevant, testing guidance, and agent workflow docs.
- For non-trivial features, produce or update a spec and run a primary spec review before an implementation plan. Specs live in `docs/specs/`.
- Convert specs into vertical slices before planning code. Avoid plans split only by technical layer such as "database, API, UI".
- Plans live in `docs/plans/` and must include file responsibility mapping, TDD steps, verification commands, docs impact, and review checkpoints.
- Use separate review passes for plan quality, architecture, tests, docs, and security instead of relying on a single self-review.
- Use Codex as an independent second reviewer for product specs, implementation plans, large diffs, risky architecture, security-sensitive work, or stuck debugging sessions when available.
- Store review records for substantial work in `docs/reviews/` when useful for later human inspection.
- Prefer reviewer subagents for repeated quality gates: architecture, tests, docs, and security.
- When delegating coding work to Codex or another worker agent, assign one vertical slice or disjoint write scope, pass artifact paths instead of chat history, and review for spec compliance plus code quality before the next task.
- Use `bounded-goal-loop` only after the goal, file scope, allowed autonomous actions, iteration budget, verification gate, and stop conditions are explicit.
- Keep `docs/CURRENT.md` current at phase boundaries, after completed implementation slices, before context clear, and when blockers or active artifacts change.
- Persist the current goal, plan, evidence, and next action in project artifacts so work can resume without chat history.
- Keep global hooks conservative. Prefer project-level hooks for stack-specific enforcement.
- Keep long-lived product decisions in durable docs such as `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/DOMAIN_MODEL.md`, `docs/TESTING_STRATEGY.md`, and `docs/DECISIONS/`.

## Quality Gates

- Source files over 300 lines require a responsibility review. Split when multiple reasons to change are mixed.
- Source files over 600 lines are a review finding unless generated, vendored, fixtures, migrations, or a project explicitly documents the exception.
- Functions over 50-80 lines, deeply nested conditionals, or repeated switch/if chains require extraction or a written reason to keep them.
- Apply SOLID as operational checks, not slogans:
  - Single Responsibility: each module has one primary reason to change.
  - Open/Closed: extension points exist only where variation is real.
  - Liskov: subtype or interface implementations preserve behavior contracts.
  - Interface Segregation: callers do not depend on methods they do not use.
  - Dependency Inversion: domain/application code depends on ports or stable interfaces, not framework details.
- Apply DDD only where domain complexity exists. Use entities, value objects, aggregates, domain services, repositories, and adapters when they clarify invariants and boundaries.
- Do not introduce ceremonial DDD layers for CRUD screens or simple glue code.
- Tests should verify public behavior and domain invariants. Avoid tests coupled to private helpers, incidental mocks, or file layout.
- Broad or risky changes need two reviews before shipping: primary self/subagent review and independent second review, preferably Codex.

## Session Hygiene

- Keep specs, plans, reviews, and docs as durable artifacts so humans can inspect the reasoning after an agent session ends.
- Clear or restart an agent session after a major phase boundary when context gets large: after discovery/spec, after plan approval, after large implementation slices, or after review fixes.
- Before clearing a session, write a handoff note in the relevant spec, plan, or review file with current state, decisions, verification, and next action.
- New sessions must begin by reading `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`, current spec/plan, recent reviews, and relevant code.
- Long-running loops must record iteration count, verification evidence, remaining risk, and the next safe action before context is cleared.

## Safety Rules

- Do not expose or print secrets, private keys, tokens, `.env` values, or auth files.
- Do not delete files, rewrite history, force push, or run destructive commands without explicit user approval.
- Do not install packages or run stack bootstrapping commands unless the user explicitly asks the agent to execute them; otherwise provide guidance for the user's package manager.
- Do not silently normalize security-sensitive input such as passwords or secret keys.
- Avoid direct edits to lockfiles, generated files, migrations, or vendored code unless the task explicitly requires it.
- Do not game verification by weakening assertions, narrowing coverage, skipping relevant checks, or changing tests to match broken behavior.
- Do not bypass failing checks to finish faster. Either make one targeted fix when the cause is clear or report the blocker with evidence.
- Check injection, path traversal, unvalidated input, auth bypass, secret leakage, destructive operation, and data-loss risks when touching relevant surfaces.
- For infrastructure work, inspect environment, services, configs, and logs before changing behavior. Validate config before reload or restart; prefer reload when safe.
- Project-specific service names, deploy paths, reload commands, and environment details belong in project-local instructions.
