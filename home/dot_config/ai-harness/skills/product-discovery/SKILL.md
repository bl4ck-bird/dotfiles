---
name: product-discovery
description: Use when brainstorming, starting a new product, side project, major feature, MVP, roadmap, or product direction before writing specs or code.
---

# Brainstorming / Product Discovery

Clarify the product goal before architecture or code. This is the product-facing entry point of the
harness and covers lightweight brainstorming.

## Questions To Resolve

Do not ask all questions mechanically. Inspect existing docs first, then ask only the questions that
remove real ambiguity.

Resolve:

- Product goal: what useful outcome should exist?
- Primary user: who will repeatedly use it?
- Pain or job: what problem happens without this?
- MVP boundary: what is the smallest useful version?
- Non-goals: what are we explicitly not building now?
- Success signal: what proves the MVP worked?
- Differentiator: what makes this worth building instead of a generic clone?
- Constraints: time, budget, stack, platform, privacy, offline/online, deployment.
- Risks: product, technical, UX, data, security, legal, operational.
- First vertical slice: what can be built and tested earliest?

## Output Documents

Create or update only the artifacts justified by the approved scaffold profile and project risk:

- `docs/reviews/YYYY-MM-DD-<topic>-discovery.md` for longer discovery sessions
- `docs/CURRENT.md` when the active phase, next step, blocker, or active acceptance artifact/plan
  changes
- `docs/ROADMAP.md` when product scope, milestones, non-goals, or open product decisions need
  durable tracking

Do not create a spec from discovery directly. Route resolved discovery output through `write-spec`
when an acceptance artifact is needed.

For new projects, also ensure the approved scaffold profile has the right docs:

- `AGENTS.md`
- `CONTEXT.md`
- `docs/AGENT_WORKFLOW.md`
- `docs/TESTING_STRATEGY.md`

Add only when relevant:

- `CONTEXT-MAP.md`: multiple contexts, apps, packages, or integrations.
- `docs/ARCHITECTURE.md`: boundaries, runtime surfaces, or dependency direction matter.
- `docs/DOMAIN_MODEL.md`: domain terms, invariants, or workflows matter.
- `docs/DATA_MODEL.md`: persistence, migration, retention, deletion, import/export, or backup
  matter.
- `docs/SECURITY_MODEL.md`: auth, permissions, secrets, trust boundaries, sensitive data, deletion,
  or crypto matter.

## Discovery Output Format

Use this concise structure:

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

- Do not start implementation from product discovery.
- Do not create a broad roadmap without a concrete first slice.
- Do not hide uncertainty. Mark unknowns as open questions.
- Do not copy competitor features without explaining the user job.
- Prefer one excellent MVP workflow over many shallow features.

## Next Step

After discovery, run:

1. `pressure-test` if decisions still need pressure-testing.
2. `domain-modeling` if domain language matters.
3. `write-spec` when the direction is ready for an acceptance artifact.

End by recommending exactly one next phase and asking for confirmation, for example: "제품 방향이 정리됐습니다.
다음 단계로 스펙 초안을 작성할까요?"
