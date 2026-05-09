---
name: architecture-review
description: Use when reviewing implementation plans, diffs, or designs for architecture, DDD, SOLID, module boundaries, over-abstraction, or maintainability.
---

# Architecture Review

Review the current plan, diff, or implementation as a skeptical architecture reviewer.

## Inputs

Read what exists before judging:

- `AGENTS.md`, `CONTEXT.md`, `CONTEXT-MAP.md`
- `docs/ARCHITECTURE.md`
- `docs/DOMAIN_MODEL.md`
- `docs/DECISIONS/`
- The relevant spec, plan, and diff

## Review Focus

- Boundary clarity between domain, application, infrastructure, and UI layers.
- Coupling direction, dependency inversion, circular dependencies, and framework leakage.
- Whether new abstractions are justified by real complexity, repeated variation, or established project patterns.
- File size, responsibility creep, hidden mutation, and confusing control flow.
- Testability of core behavior without relying on UI, network, database, or filesystem details.
- Whether the implementation supports the roadmap without building speculative infrastructure.

## DDD Checks

Use DDD where domain complexity exists. Do not force ceremony onto simple CRUD.

Check:

- Important terms match `CONTEXT.md` and `docs/DOMAIN_MODEL.md`.
- Entities have identity and lifecycle only when identity matters.
- Value objects are immutable or treated as immutable and protect validation rules.
- Aggregates protect invariants and do not expose inconsistent intermediate state.
- Application services orchestrate use cases without owning domain rules.
- Infrastructure adapters do not leak persistence, network, or framework types into domain rules.
- Repositories or ports represent real boundaries, not fake abstractions around one-line CRUD.

## SOLID Checks

Translate SOLID into concrete findings:

- SRP: modules with multiple reasons to change should be split.
- OCP: extension points should exist only for real variation.
- LSP: implementations must preserve caller-visible behavior contracts.
- ISP: broad interfaces should be split when callers use small subsets.
- DIP: high-level domain/application code should not depend on framework or adapter details.

## File And Complexity Thresholds

Use these as review gates, not mechanical rewrite commands:

- Source file over 300 lines: require responsibility review.
- Source file over 600 lines: finding unless generated, vendored, migration, fixture, or documented exception.
- Function over 50-80 lines: consider extraction if it mixes concerns or has deep branching.
- Three or more repeated conditionals on the same concept: consider a domain concept, strategy, lookup table, or policy object.
- Long files are acceptable when they are data tables, generated code, test fixtures, or deliberately documented framework glue.

## Agentic Maintainability

Review whether a future human or agent can understand the code:

- Can the core behavior be located from the spec or domain docs?
- Are module names aligned with domain language?
- Are interfaces small and stable enough to test?
- Is the plan split into reviewable vertical slices?
- Are temporary specs reconciled into durable docs?

## Output

Lead with findings, ordered by severity. Avoid generic praise.

For each finding include:

- Impact
- Evidence with file references
- Suggested correction
- Whether it blocks implementation, blocks shipping, or can be tracked

If there are no material issues, say so directly and list residual risks or test gaps.

## Biases

- Prefer simpler boundaries over ceremonial DDD.
- Prefer explicit project rules over generic SOLID slogans.
- Do not recommend large rewrites unless the current design blocks the requested work.
- Prefer small refactor slices that keep tests green.
