---
name: docs-sync
description: Use when project documentation may need updates after code, architecture, scope, testing, security, or user-facing behavior changes.
---

# Docs Sync

Keep durable docs aligned with project state.

Triggered from `ship-check` Preconditions when behavior, architecture, testing, security, or
user-facing behavior changed. May also be invoked directly when user notes drift.
`code-quality-review` durable-docs-drift overlaps — that review flags drift *during code
review*; this skill *resolves* drift after acceptance.

## Check

Review changed files, identify durable concerns touched, decide whether any candidate doc
needs updates:

- `README.md`, `AGENTS.md`, `CLAUDE.md`, `.ai-harness/CONTEXT.md`, `.ai-harness/CONTEXT-MAP.md`
- `.ai-harness/AGENT_WORKFLOW.md`, `.ai-harness/CURRENT.md`, `.ai-harness/ROADMAP.md`
- `.ai-harness/ARCHITECTURE.md`, `.ai-harness/DOMAIN_MODEL.md`, `.ai-harness/DATA_MODEL.md`
- `.ai-harness/SECURITY_MODEL.md`, `.ai-harness/TESTING_STRATEGY.md`
- `.ai-harness/DECISIONS/`, `.ai-harness/specs/`, `.ai-harness/plans/`, `.ai-harness/reviews/`
- feature specs and implementation plans

## Rules

- README stays high-level and user-facing.
- `.ai-harness/CONTEXT.md` owns bounded-context vocabulary and canonical domain terms.
- Architecture, domain, data, security, testing rules live in focused docs.
- Specs and plans describe a single work item; not long-term source of truth.
- Remove stale claims instead of adding caveats around them.
- No placeholders, future-tense promises, or vague sync notes in `ready` docs.
- Scaffolded `stub` docs may contain TODOs. TODO claims are not project truth; non-TODO
  workflow, safety, and quality rules still apply.
- Promote docs from `stub` to `draft`/`ready` only when claims have been reviewed against the
  repo or confirmed by user.

## Common Triggers

Update docs when:

- Product goal, MVP boundary, or non-goals change.
- Domain term added, renamed, split, or deprecated.
- Domain invariant or workflow changes.
- New external dependency, runtime surface, adapter, or storage model introduced.
- Test commands, test strategy, or verification expectations change.
- Review finds a durable architecture, security, or data decision hidden only in chat.
- Active phase, acceptance artifact/source, plan, blocker, completed slice, verification
  evidence, or next action materially changes.

## Handoffs

Session about to be cleared → add/update handoff in `.ai-harness/reviews/`:

- current goal
- completed work
- decisions made
- verification evidence
- next safe action

Update `.ai-harness/CURRENT.md` with active phase and next recommended action when changed. Same
session continuing immediately → update once at end of phase, not after every step.

### `.ai-harness/CURRENT.md` Template (SSOT)

Canonical skeleton. Other skills reference this; do not redefine the format elsewhere.
Keep it short — it points to artifacts, it does not duplicate them. One line per field.

```markdown
# CURRENT — <project> 진행 상태

> 세션 시작 시 가장 먼저 읽는 상태 파일. phase 경계에서만 갱신(매 스텝 X).
> 형식 SSOT: docs-sync Handoffs. 상세는 각 artifact 경로 참조.

- **Active phase**: <discovery | spec | plan | impl:S0… | review | ship>
- **Acceptance source**: <spec / ADR / issue 경로들>
- **Plan**: <.ai-harness/plans/... 경로 | 없음>
- **Completed slice/work**: <최근 완료 단위 + 한 줄>
- **Verification**: <명령 + 결과 evidence | N/A 사유>
- **Blocker**: <없음 | 내용>
- **Next action**: <다음 안전 액션 1개>

_Updated: <YYYY-MM-DD> · <session/agent>_
```

- Create on first non-trivial phase boundary (or at `project-scaffold` time).
- Fields map 1:1 to the update triggers above (Active phase, acceptance artifact/source,
  plan, blocker, completed slice, verification evidence, next action).

## Output

Report docs updated, docs intentionally left unchanged, and remaining documentation risks.
