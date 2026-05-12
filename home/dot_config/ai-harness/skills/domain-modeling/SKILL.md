---
name: domain-modeling
description: Use when domain terms are unclear, overloaded, or drifting; when introducing or renaming aggregates, value objects, or bounded contexts; or when CONTEXT.md / CONTEXT-MAP.md / docs/DOMAIN_MODEL.md need updates before a spec or plan touches domain code.
---

# Domain Modeling

Keep agent plans aligned with the product's language and boundaries.

Called from `write-spec` Self-Review when domain terms are unstable, and from
`write-plan` Self-Review when the plan touches domain code with unclear boundaries.
Can be invoked directly when introducing or renaming aggregates, value objects, or
bounded contexts.

`code-quality-review/ddd-operational-checks.md` validates the resulting code; this
skill *establishes* the model that those checks validate against.

## Read First

Look for:

- `CONTEXT.md`
- `CONTEXT-MAP.md`
- `docs/DOMAIN_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/DECISIONS/`
- Current spec or plan
- Relevant code and tests

If these files do not exist, propose initial versions instead of inventing final truth.

## Interview Pattern

Ask one question at a time only when the answer cannot be inferred from docs or code.

Challenge fuzzy terms immediately:

- "account"
- "user"
- "member"
- "project"
- "workspace"
- "payment"
- "order"
- "session"
- "status"
- "sync"
- "delete"

For each ambiguous term, resolve:

- Canonical term
- Synonyms to avoid
- Definition
- Ownership context
- Key states
- Invariants
- Example usage

## DDD Modeling

Use only the concepts that clarify the design:

- Entity: identity and lifecycle matter.
- Value object: equality by value, validates a concept, no independent lifecycle.
- Aggregate: consistency boundary that protects invariants.
- Domain service: domain rule that does not naturally belong to one entity/value object.
- Application service: orchestrates a use case and transaction boundary.
- Repository/port: boundary for persistence or external systems.
- Adapter: implementation detail outside the domain.

Avoid ceremonial layers when the domain is simple.

## Context Map

When the repo has multiple subsystems or bounded contexts, update `CONTEXT-MAP.md` with:

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
