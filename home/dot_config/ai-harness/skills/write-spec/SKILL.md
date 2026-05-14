---
name: write-spec
description: Use when converting resolved product context, PRDs, feature ideas, issues, or review findings into an acceptance artifact, acceptance criteria, and vertical implementation slices. Direction must already be settled — run product-discovery / domain-modeling first if not.
---

# Write Spec

Turn resolved context into the lightest acceptance artifact that can be implemented and reviewed. Then split into vertical slices.

Do not create a full spec just to restate an already clear task. A clear issue, PRD, review finding, or approved user request may suffice when acceptance criteria and risk are already explicit.

## Save Location

```text
docs/specs/YYYY-MM-DD-<feature>.md
```

Use the project's established location if it has one.

For small well-understood work, use the existing issue, review record, or approved user request as the acceptance source instead of creating a new spec file. `docs/CURRENT.md` may point to the active source but should not replace it.

## Inputs

**Light artifact mode**: issue, review finding, PRD section, or approved user request is already clear enough to become the acceptance source. Read:

- `CONTEXT.md`
- `docs/CURRENT.md`
- The acceptance source: issue, PRD section, review finding, or approved user request
- Existing code and tests when feature extends current behavior

**Full spec mode**: product scope, domain language, public API, data/storage, auth/security, deletion, sync, external integrations, or user workflow still being decided. Also read:

- `docs/ROADMAP.md`
- Discovery or interview notes

Conditional reads in either mode:

- `CONTEXT-MAP.md`: multiple contexts, apps, packages, or integrations.
- `docs/DOMAIN_MODEL.md`: domain terms, invariants, or workflows may change.
- `docs/DATA_MODEL.md`: persistence, migration, retention, deletion, import/export, or backup may change.
- `docs/SECURITY_MODEL.md`: auth, permissions, secrets, trust boundaries, sensitive data, deletion, or crypto may change.
- Relevant durable decisions when hard to reverse or surprising.

Idea still ambiguous → run `pressure-test` first. Terms unstable → run `domain-modeling` first.

## Light Acceptance Brief

Other docs reference this section as "Acceptance Brief Fields (see `write-spec`)" instead of re-listing fields. Harness-wide canonical field set lives here.

Use for non-trivial work when a full spec would only duplicate an already clear request. Source can live in an issue, review record, plan anchor, or short `docs/specs/` note, but must include every field below:

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

When the spec is revised because `spec-compliance-review` found drift, or user changed scope, update the existing artifact at the same path. Do not create a new spec file or restart. Address each finding, preserve unchanged sections, re-run Self-Review. See `using-bb-harness` Review Iteration Pattern.

## Application Rules

- Light acceptance source (issue, PRD section, review finding, approved user task) must include every field above. Self-Review (Product Clarity + Domain Alignment) always required; `second-review` only when Self-Review triggers apply.
- Full spec mode required when product scope, domain language, public API, data/storage, auth/security, deletion, sync, external integrations, or user workflow is still being decided. Run full Self-Review on result.
- Request lives only in chat → implementation plan must capture every field in an "Approved Request Anchor" section.
- Other skills/docs link here; field changes happen only here.

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

- Deliver one behavior or decision reviewable end to end.
- Include all necessary layers for that behavior.
- Have acceptance criteria.
- Include test expectations.
- Be small enough for one focused implementation plan.
- Be labeled AFK or HITL:
  - AFK: agent can complete without user input.
  - HITL: requires user decision, product taste, credentials, deployment, or manual validation.

Avoid horizontal slices: "Create database schema", "Build API", "Build UI", "Add tests".

Prefer: "User can create the first workspace with validation and persistence.", "User can see reconciliation mismatch details and retry the import."

## Self-Review

Walk this checklist before declaring artifact ready. Domain and acceptance correctness owned here, then re-verified by `spec-compliance-review` after implementation.

### Product Clarity

- Goal, problem, users, MVP, non-goals explicit (or, for Light Acceptance Brief, every canonical field present).
- Acceptance criteria testable through public interface or user-visible flow, not implementation notes.
- Vertical slices deliver reviewable behavior, not horizontal layers.
- AFK / HITL labels realistic.
- Testing and docs impact named.

### Domain Alignment (DDD upstream check)

When `CONTEXT.md` or `docs/DOMAIN_MODEL.md` exists:

- Every domain term matches `CONTEXT.md` glossary. New terms defined and added to `CONTEXT.md` as part of acceptance work, not silently introduced.
- Aggregate boundaries match `docs/DOMAIN_MODEL.md`. Spec does not cross a bounded context without naming the translation layer.
- Documented invariants the spec touches are listed with how each will be proven (test or domain event). Invariants without proof are open questions, not acceptance criteria.
- Spec uses `entity` vs `value object` vs `aggregate` vocabulary correctly when introducing or changing one.

Purely UI / CRUD / glue work with low domain complexity → mark `N/A — non-domain change` and skip.

### Independent Review

Two options when author wants a second pair of eyes:

- **`spec-document-reviewer-prompt.md`** (in this directory) — same-host subagent re-reads spec and project context independently. Use when:
  - Domain language being introduced or renamed.
  - High-Risk Surface (see `second-review`) touched.
  - Product direction, MVP boundary, or core architecture changes.
  - Self-Review passed but author is uncertain.
- **`second-review`** (Codex by default) — different-model, fully-independent double-check. Required when spec touches High-Risk Surface; otherwise optional. Heavier than same-host reviewer.

Neither is mandatory — Self-Review alone is the default. Pick whichever justifies the time.

Otherwise, next gate is `spec-compliance-review` after implementation.

## Output

Report:

- artifact path or source
- slices
- AFK/HITL split
- review needs
- recommended first plan or review path
- one next-phase question, such as whether to proceed to write-plan
