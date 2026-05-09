# Context Map

Document status: stub. TODO claims are not project truth yet. Non-TODO workflow, safety, and quality
rules apply immediately.

Use this file when the project has multiple bounded contexts, subsystems, apps, packages, or
external integrations.

## Contexts

| Context | Responsibility | Owned Terms | Notes |
| --- | --- | --- | --- |
| TODO | TODO | TODO | TODO |

## Relationships

| Upstream | Downstream | Integration Style | Translation Needed |
| --- | --- | --- | --- |
| TODO | TODO | TODO | TODO |

## External Systems

| System | Purpose | Boundary | Failure Mode |
| --- | --- | --- | --- |
| TODO | TODO | TODO | TODO |

## Rules

- Each context owns its canonical terms.
- Cross-context data should be translated at boundaries.
- Do not leak external API or storage vocabulary into the domain unless the external concept is the
  domain.
- Add formal decision records only for hard-to-reverse, surprising context or integration tradeoffs
  from real options.
