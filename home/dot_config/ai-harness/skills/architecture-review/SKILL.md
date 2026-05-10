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
- The relevant acceptance artifact (spec/PRD/issue/review finding/approved task), plan, and diff

## Review Focus

- Boundary clarity between domain, application, infrastructure, and UI layers.
- Coupling direction, dependency inversion, circular dependencies, and framework leakage.
- Whether new abstractions are justified by real complexity, repeated variation, or established
  project patterns.
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

### DDD Operational Checks (when domain-heavy)

Run only when `CONTEXT.md` or `docs/DOMAIN_MODEL.md` exists and the diff touches domain code:

- Bounded context boundaries: no cross-context imports of another context's aggregates or value
  objects without an explicit translation layer.
- Aggregate invariants: each documented invariant has at least one test through a public interface
  or domain event.
- Anti-corruption layer: external integrations translate at the boundary; external types do not
  appear in domain code.
- Ubiquitous language drift: grep code identifiers (class, function, table, event names) against
  the `CONTEXT.md` glossary; flag synonyms or undefined terms.

## SOLID Checks

Translate SOLID into concrete findings:

- SRP: modules with multiple reasons to change should be split.
- OCP: extension points should exist only for real variation.
- LSP: implementations must preserve caller-visible behavior contracts.
- ISP: broad interfaces should be split when callers use small subsets.
- DIP: high-level domain/application code should not depend on framework or adapter details.

## Code Hygiene Checks

Always-applicable checks. Each finding should cite a file/line.

- Comment hygiene: comments explain *why* (constraints, invariants, workarounds). Flag tutorial
  comments, restated identifiers, "added for X" temporal notes, and large auto-generated docstrings
  that drift from the code.
- Silent failure: flag swallowed exceptions, broad `try/except` or `catch (...)` without re-raise,
  default fallbacks that mask upstream failure, and `console.error`/log-and-continue on errors that
  must reach the caller.
- Type design (typed languages): types encode invariants where practical. Flag `any`/`unknown`
  leakage past boundaries, stringly-typed states that should be enums or value objects, and public
  interfaces that accept broader types than they need (ISP at the type level).

## File And Complexity Thresholds

Canonical thresholds for the harness; other docs link here.

- **300 lines (source file)**: require responsibility review. Split when multiple reasons to
  change are mixed.
- **600 lines (source file)**: review finding unless the file is generated, vendored, a fixture,
  a migration, a data table, or has a documented exception in `docs/ARCHITECTURE.md`.
- **50-80 lines (function)**: consider extraction if it mixes concerns or has deep branching.
- **3+ repeated conditionals on the same concept**: consider a domain concept, strategy, lookup
  table, or policy object.
- Long files are acceptable when they are data tables, generated code, test fixtures, or
  deliberately documented framework glue.

Treat these as review thresholds, not mechanical rewrite commands.

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
