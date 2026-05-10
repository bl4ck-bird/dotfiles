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

## Edit-On-Review Mode

When `write-spec` is invoked because `spec-review` returned `Blocked` or P0/P1 findings, update
the existing artifact at the same path. Do not create a new spec file or restart from scratch.
Address each finding, preserve sections the review did not flag, and re-submit the changed
artifact to `spec-review`. See `bb-workflow` Review Iteration Pattern.

## Application Rules

- Light acceptance source (issue, PRD section, review finding, approved user task) must include
  every field above. Skip `spec-review` only when no product/domain/API/data/security/user-workflow
  decision is being made.
- Full spec mode (use the Full Spec Template below plus `spec-review`) is required when product
  scope, domain language, public API, data/storage, auth/security, deletion, sync, external
  integrations, or user workflow is still being decided.
- When the request lives only in chat, the implementation plan must capture every field in an
  "Approved Request Anchor" section.
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

## Review

Before writing a durable implementation plan, run `spec-review` when a full spec or PRD
exists, or when acceptance criteria are still being shaped. A light Acceptance Brief can
skip separate `spec-review` only when it has every canonical field and no
product/domain/API/data/security/user-workflow decision is being made. Review:

- product goal and MVP fit
- domain language
- acceptance criteria
- vertical slice quality
- missing testing or docs decisions

Use `second-review` optionally for product direction, MVP boundary, core architecture, data/security
behavior, or other risky surfaces. It is required only when the change touches a High-Risk Surface
(see `second-review`). Use the host agent's Codex integration when available.

## Output

Report:

- artifact path or source
- slices
- AFK/HITL split
- review needs
- recommended first plan or review path
- one next-phase question, such as whether to proceed to write-plan
