---
name: product-discovery
description: Use when brainstorming, starting a new product, side project, major feature, MVP, roadmap, or product direction before writing specs or code. First phase when goal/MVP/non-goals are unsettled; precedes pressure-test and write-spec.
---

# Brainstorming / Product Discovery

Clarify the product goal before architecture or code. Product-facing entry point; covers
lightweight brainstorming.

## Questions To Resolve

Inspect existing docs first. Ask only questions that remove real ambiguity.

- Product goal: what useful outcome should exist?
- Primary user: who will repeatedly use it?
- Pain or job: what problem happens without this?
- MVP boundary: smallest useful version?
- Non-goals: what are we explicitly not building now?
- Success signal: what proves MVP worked?
- Differentiator: why build instead of generic clone?
- Constraints: time, budget, stack, platform, privacy, offline/online, deployment.
- Risks: product, technical, UX, data, security, legal, operational.
- First vertical slice: what can be built and tested earliest?

## Output Documents

Create or update only artifacts justified by approved scaffold profile and project risk:

- `docs/reviews/YYYY-MM-DD-<topic>-discovery.md` for longer sessions
- `docs/CURRENT.md` when active phase, next step, blocker, or acceptance artifact/plan changes
- `docs/ROADMAP.md` when product scope, milestones, non-goals, or open decisions need durable
  tracking

Do not create a spec from discovery directly. Route output through `write-spec` when an
acceptance artifact is needed.

For new projects, ensure approved scaffold profile has:

- `AGENTS.md`
- `CONTEXT.md`
- `docs/AGENT_WORKFLOW.md`
- `docs/TESTING_STRATEGY.md`

Add only when relevant:

- `CONTEXT-MAP.md`: multiple contexts, apps, packages, integrations.
- `docs/ARCHITECTURE.md`: boundaries, runtime surfaces, dependency direction matter.
- `docs/DOMAIN_MODEL.md`: domain terms, invariants, workflows matter.
- `docs/DATA_MODEL.md`: persistence, migration, retention, deletion, import/export, backup.
- `docs/SECURITY_MODEL.md`: auth, permissions, secrets, trust boundaries, sensitive data,
  deletion, crypto.

## Discovery Output Format

```markdown
# <Product/Feature> Discovery
## Product Goal
## Primary Users
## MVP
## Non-Goals
## Success Signals
## Risks
## Open Questions
## First Vertical Slice
```

## Rules

- No implementation from product discovery.
- No broad roadmap without a concrete first slice.
- No hiding uncertainty. Mark unknowns as open questions.
- No copying competitor features without explaining the user job.
- Prefer one excellent MVP workflow over many shallow features.

## Next Step

1. `pressure-test` if decisions still need pressure-testing.
2. `domain-modeling` if domain language matters.
3. `write-spec` when direction is ready for an acceptance artifact.

Recommend exactly one next phase and ask for confirmation, e.g. "제품 방향이 정리됐습니다.
다음 단계로 스펙 초안을 작성할까요?"
