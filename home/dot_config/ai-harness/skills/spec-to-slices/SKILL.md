---
name: spec-to-slices
description: Use when converting resolved product context, PRDs, feature ideas, or plans into specs, acceptance criteria, and vertical implementation slices.
---

# Spec To Slices

Turn resolved context into a spec that can be implemented and reviewed. Then split it into vertical slices.

## Save Location

Save specs to:

```text
docs/specs/YYYY-MM-DD-<feature>.md
```

Use the project's established location if it already has one.

## Inputs

Always read:

- `docs/ROADMAP.md`
- `CONTEXT.md`
- Discovery or interview notes
- Existing code and tests when the feature extends current behavior

Read conditionally when relevant:

- `CONTEXT-MAP.md`: multiple contexts, apps, packages, or integrations.
- `docs/DOMAIN_MODEL.md`: domain terms, invariants, or workflows may change.
- `docs/DATA_MODEL.md`: persistence, migration, retention, deletion, import/export, or backup may change.
- `docs/SECURITY_MODEL.md`: auth, permissions, secrets, trust boundaries, sensitive data, deletion, or crypto may change.
- Relevant ADRs when decisions are hard to reverse or surprising.

If the idea is still ambiguous, run `critical-interview` before writing the spec.
If terms are unstable, run `domain-modeling` before writing the spec.

## Spec Template

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

Before implementation planning, run the primary `review-gate` on the spec for:

- product goal and MVP fit
- domain language
- acceptance criteria
- vertical slice quality
- missing testing or docs decisions

Use independent Codex second review when the spec changes product direction, MVP boundary, core architecture, data/security behavior, or other risky surfaces. Record accepted risk if the second review is unavailable.

## Output

Report:

- spec path
- slices
- AFK/HITL split
- review needs
- recommended first plan after spec review
- one next-phase question, such as whether to proceed to implementation planning
