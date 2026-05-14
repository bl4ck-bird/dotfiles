---
name: domain-modeling
description: Use when domain terms are unclear, overloaded, or drifting; when introducing or renaming aggregates, value objects, or bounded contexts; or when CONTEXT.md / CONTEXT-MAP.md / docs/DOMAIN_MODEL.md need updates before a spec or plan touches domain code.
---

# Domain Modeling

Keep agent plans aligned with product language and boundaries.

Called from `write-spec` Self-Review when domain terms are unstable, and from `write-plan`
Self-Review when the plan touches domain code with unclear boundaries. May be invoked directly
when introducing or renaming aggregates, value objects, or bounded contexts.

`code-quality-review/ddd-operational-checks.md` validates the resulting code; this skill
*establishes* the model that those checks validate against.

## Read First

- `CONTEXT.md`
- `CONTEXT-MAP.md`
- `docs/DOMAIN_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/DECISIONS/`
- Current spec or plan
- Relevant code and tests

If files do not exist, propose initial versions instead of inventing final truth.

## Interview Pattern

One question at a time, only when the answer cannot be inferred from docs or code.

Challenge fuzzy terms immediately: "account", "user", "member", "project", "workspace",
"payment", "order", "session", "status", "sync", "delete".

For each ambiguous term, resolve:

- Canonical term
- Synonyms to avoid
- Definition
- Ownership context
- Key states
- Invariants
- Example usage

## DDD Modeling

Use only concepts that clarify design:

- Entity: identity and lifecycle matter.
- Value object: equality by value, validates a concept, no independent lifecycle.
- Aggregate: consistency boundary protecting invariants.
- Domain service: domain rule not naturally belonging to one entity/value object.
- Application service: orchestrates use case and transaction boundary.
- Repository/port: boundary for persistence or external systems.
- Adapter: implementation detail outside the domain.

Avoid ceremonial layers when domain is simple.

## Context Map

Multiple subsystems or bounded contexts → update `CONTEXT-MAP.md`:

- Context name
- Responsibility
- Owned terms
- Upstream/downstream relationships
- Integration style
- Translation or anti-corruption needs

## Decision Record Rule

Suggest a formal decision record only for hard-to-reverse, surprising tradeoffs.

## Outputs

Update or propose updates to:

- `CONTEXT.md`
- `CONTEXT-MAP.md`
- `docs/DOMAIN_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/DECISIONS/<number>-<slug>.md`

End with:

- resolved terms
- unresolved terms
- invariants
- boundary decisions
- next skill to run
