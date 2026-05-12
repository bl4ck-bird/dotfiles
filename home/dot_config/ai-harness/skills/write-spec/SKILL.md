---
name: write-spec
description: Use when converting resolved product context, PRDs, feature ideas, issues, or review findings into an acceptance artifact, acceptance criteria, and vertical implementation slices.
---

# Write Spec

Turn resolved context into the lightest acceptance artifact that can be implemented and reviewed.
Then split it into vertical slices.

Do not create a full spec just to restate an already clear task. A clear issue, PRD, review finding,
or approved user request may be enough when acceptance criteria and risk are already explicit.

## Save Location

Save full specs to:

```text
docs/specs/YYYY-MM-DD-<feature>.md
```

Use the project's established location if it already has one.

For small well-understood work, use the existing issue, review record, or approved user request as
the acceptance source instead of creating a new spec file. `docs/CURRENT.md` may point to the active
source, but it should not replace the acceptance source.

## Inputs

Light artifact mode:

Use this when an issue, review finding, PRD section, or approved user request is already clear
enough to become the acceptance source. Read:

- `CONTEXT.md`
- `docs/CURRENT.md`
- the acceptance source: issue, PRD section, review finding, or approved user request
- Existing code and tests when the feature extends current behavior

Full spec mode:

Use this when product scope, domain language, public API, data/storage, auth/security, deletion,
sync, external integrations, or user workflow is still being decided. Also read:

- `docs/ROADMAP.md`
- Discovery or interview notes

Read conditionally in either mode when relevant:

- `CONTEXT-MAP.md`: multiple contexts, apps, packages, or integrations.
- `docs/DOMAIN_MODEL.md`: domain terms, invariants, or workflows may change.
- `docs/DATA_MODEL.md`: persistence, migration, retention, deletion, import/export, or backup may
  change.
- `docs/SECURITY_MODEL.md`: auth, permissions, secrets, trust boundaries, sensitive data, deletion,
  or crypto may change.
- Relevant durable decisions when decisions are hard to reverse or surprising.

If the idea is still ambiguous, run `pressure-test` before writing the artifact.
If terms are unstable, run `domain-modeling` before writing the artifact.

## Light Acceptance Brief

Other docs and skills reference this section as "Acceptance Brief Fields (see `write-spec`)"
instead of re-listing the fields. The harness-wide canonical field set lives here.

Use this for non-trivial work when a full spec would only duplicate an already clear
request. The source can live in an issue, review record, plan anchor, or short
`docs/specs/` note, but it must include every field below:

```markdown
# <Feature or Change> Acceptance Brief

## Goal

## Accepted Behavior

## Acceptance Criteria

## Non-Goals / Stop Conditions

## Touched Surfaces
- Product:
- API:
- Data/storage:
- Security/privacy:
- UI:
- Docs:
- Tests:

## Edge And Error Cases

## Docs / Test Impact

## Risk Level

## Required Reviews

## Second Review

## AFK / HITL Boundary
```

## Edit-On-Findings Mode

When the spec is revised because `spec-compliance-review` found drift between implementation
and acceptance, or because the user changed scope, update the existing artifact at the same
path. Do not create a new spec file or restart from scratch. Address each finding, preserve
sections that did not change, and re-run Self-Review on the changed artifact. See
`using-bb-harness` Review Iteration Pattern.

## Application Rules

- Light acceptance source (issue, PRD section, review finding, approved user task) must
  include every field above. Self-Review (Product Clarity + Domain Alignment) is always
  required; `second-review` is only required when triggers in Self-Review apply.
- Full spec mode is required when product scope, domain language, public API,
  data/storage, auth/security, deletion, sync, external integrations, or user workflow is
  still being decided. Run full Self-Review on the result.
- When the request lives only in chat, the implementation plan must capture every field in
  an "Approved Request Anchor" section.
- Other skills/docs link to this template; field changes happen only here.

## Full Spec Template

```markdown
# <Feature> Spec

## Goal

## Problem

## Users

## MVP Scope

## Non-Goals

## Domain Terms

## User Stories

## Acceptance Criteria

## Implementation Decisions

## Testing Decisions

## Docs Impact

## Risks

## Open Questions

## Vertical Slices
```

## Vertical Slice Rules

A slice should:

- Deliver one behavior or decision that can be reviewed.
- Include all necessary layers for that behavior.
- Have acceptance criteria.
- Include test expectations.
- Be small enough for one focused implementation plan.
- Be labeled AFK or HITL:
  - AFK: agent can complete without user input.
  - HITL: requires user decision, product taste, credentials, deployment, or manual validation.

Avoid horizontal slices like:

- "Create database schema"
- "Build API"
- "Build UI"
- "Add tests"

Prefer:

- "User can create the first workspace with validation and persistence."
- "User can see reconciliation mismatch details and retry the import."

## Self-Review

Before declaring the artifact ready, walk this checklist yourself. The harness no longer runs
a separate `spec-review` skill — domain and acceptance correctness is owned here, then
re-verified by `spec-compliance-review` after implementation.

### Product Clarity

- Goal, problem, users, MVP, non-goals explicit (or, for a Light Acceptance Brief, every
  canonical field present).
- Acceptance criteria are testable through a public interface or user-visible flow, not
  implementation notes.
- Vertical slices deliver reviewable behavior, not horizontal layers ("build DB", "build
  API").
- AFK / HITL labels realistic.
- Testing and docs impact named.

### Domain Alignment (DDD upstream check)

When `CONTEXT.md` or `docs/DOMAIN_MODEL.md` exists:

- Every domain term in the spec matches the `CONTEXT.md` glossary. New terms are defined
  and added to `CONTEXT.md` as part of the acceptance work, not silently introduced.
- Aggregate boundaries in the spec match `docs/DOMAIN_MODEL.md`. The spec does not cross a
  bounded context without naming the translation layer.
- Documented invariants the spec touches are listed with how each will be proven (test or
  domain event). Invariants without proof are open questions, not acceptance criteria.
- The spec uses `entity` vs `value object` vs `aggregate` vocabulary correctly when it
  introduces or changes one.

For purely UI / CRUD / glue work where domain complexity is low, mark this section
`N/A — non-domain change` and skip.

### Independent Review

Two options when the author wants a second pair of eyes:

- **`spec-document-reviewer-prompt.md`** (in this directory) — dispatch a same-host
  subagent that re-reads the spec and project context independently. Use when:
  - Domain language is being introduced or renamed.
  - High-Risk Surface (see `second-review`) touched.
  - Product direction, MVP boundary, or core architecture changes.
  - Self-Review passed but the author is uncertain.
- **`second-review`** (Codex by default) — a different-model, fully-independent
  double-check. Required when the spec touches a High-Risk Surface; otherwise
  optional. Heavier than the same-host reviewer.

Neither is mandatory — Self-Review alone is the default. Pick the one (or both)
whose value justifies the time.

Otherwise, the next gate is `spec-compliance-review` after implementation.

## Output

Report:

- artifact path or source
- slices
- AFK/HITL split
- review needs
- recommended first plan or review path
- one next-phase question, such as whether to proceed to write-plan
