# Architecture

Document status: stub. TODO claims are not project truth yet. Non-TODO workflow, safety, and quality
rules apply immediately.

## Overview

TODO: Describe system boundaries, primary runtime surfaces, deployment shape, and core data flow.

## Layers

- Domain: TODO
- Application: TODO
- Infrastructure: TODO
- Interface/UI: TODO
- Tests: TODO

## Dependency Rules

- TODO: Define which layers can import which other layers.
- Domain should not depend on frameworks, storage, network, filesystem, or UI unless this project
  explicitly documents an exception.
- Application may orchestrate domain behavior and ports.
- Infrastructure implements ports and adapts external systems.
- UI/interface code calls application use cases; does not own domain invariants.

## Module Responsibility Rules

- Prefer small, focused files with one primary reason to change.
- File and complexity thresholds (300/600 lines, 50-80-line functions, repeated-conditional
  triggers) follow `skills/code-quality-review/SKILL.md` (File And Complexity Thresholds). Do not
  redefine numbers here; record project-specific exceptions only.
- Do not introduce abstractions without real variation, meaningful complexity, or an established
  project pattern.

## DDD Rules

Use DDD where domain complexity exists:

- Entities own identity and lifecycle.
- Value objects protect validation and equality-by-value concepts.
- Aggregates protect consistency boundaries.
- Domain services hold domain rules that do not belong to one entity/value object.
- Application services orchestrate use cases and transaction boundaries.
- Repositories/ports represent real persistence or external-system boundaries.
- Adapters keep framework and external API details outside domain rules.

Avoid ceremonial DDD for simple CRUD or thin glue code.

## SOLID Checks

- SRP: each module has one primary reason to change.
- OCP: extension points exist only where variation is real.
- LSP: implementations preserve caller-visible contracts.
- ISP: callers do not depend on methods they do not use.
- DIP: domain/application code depends on stable ports or interfaces, not adapter details.

## External Systems

| System | Boundary | Adapter | Failure Handling |
| --- | --- | --- | --- |
| TODO | TODO | TODO | TODO |

## Related Models

- Data storage, migrations, retention, deletion, recovery → `docs/DATA_MODEL.md`.
- Secrets, auth, permissions, trust boundaries, sensitive data handling → `docs/SECURITY_MODEL.md`.

## Tradeoffs

Record intentional constraints and decisions future agents should preserve. Use formal decision
records only for hard-to-reverse, surprising tradeoffs from real options; otherwise keep normal
durable decisions in the relevant docs.

## Open Architecture Questions

- TODO
