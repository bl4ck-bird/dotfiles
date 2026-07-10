---
name: second-review
description: Use when running an independent double-check (Codex by default) on a spec, plan, diff, or security-sensitive change — catches what self-review and the first reviewer missed by reading artifacts in a fresh context. spec/plan/diff/보안 민감 변경에 대해 독립적인 double-check(기본 Codex)를 실행할 때 사용한다.
---

# Second Review

**Intent**: 신선한 컨텍스트의 다른 모델은 저자와 primary reviewer가 공유하는
사각지대를 잡아낸다 — 동일 모델의 오류 상관관계를 깨는 유일한 채널이다.
**Boundary**: 요식적인 승인 도장이 아니고, 같은 모델이 하는 `implementation-review`의
재실행도 아니다; 동일 모델 대체는 기록된 fallback일 뿐 절대 조용한 등가물이 아니다.
**Verify**: 아래 Output 블록, `.ai-harness/reviews/`에 저장.

## High-Risk Surfaces (Canonical)

harness 전체의 정식 목록 — 다른 문서는 "High-Risk Surfaces (see `second-review`)"로
참조한다:

**security · data-loss · money · auth · crypto · deletion · core architecture**

이 목록을 인라인으로 참조하는 콜사이트(동기화 유지): `using-bb-harness/SKILL.md`,
`implementation-review/SKILL.md`, `executing-plans-inline/SKILL.md`,
`subagent-driven-development/SKILL.md`, `write-spec/SKILL.md`, `write-plan/SKILL.md`,
`ship-check/SKILL.md`, spec/plan reviewer 프롬프트들,
`subagent-driven-development/implementation-reviewer-prompt.md`.

## When

- **Required**: High-Risk Surface를 건드림 · 경계/의존성 방향 변경 · 사용자가
  독립적인 double-check를 요청 · primary review는 통과했지만 아티팩트가
  primary가 완전히 검사하지 못한 모듈 경계를 넘나듦.
- **Strongly consider** (트리거 2개 이상, 또는 High-Risk Surface에서 1개): 대규모/
  다중 모듈 diff 또는 수용된 300/600줄 위험 · 취약하거나/불안정하거나/과도하게
  mock된 테스트 · primary agent가 막히거나 접근 방식을 반복적으로 바꿈 · 사용자
  대면 작업에 대해 bounded automation이 제안됨 · 제품 방향, 영속성(persistence),
  sync, concurrency, 통합 형태가 바뀜.
- Required 기준을 충족하지 않는 한 spec과 plan에는 선택 사항.

## Procedure

순서대로 선호 — 목표는 다른 모델의 리뷰어이며, 어떤 fallback을 썼든 기록한다:

1. **primary agent 안에서의 플러그인 호출.** Claude Code: Codex 플러그인 —
   High-Risk Surface나 설계 이의 제기에는 `/codex:adversarial-review`, 단순
   double-check에는 `/codex:review`; 변경 범위를 명시적으로 전달하고(예:
   `--base <ref>`) Codex의 출력을 그대로 raw appendix로 보존한다. 이 단계에서
   동일 모델 subagent로 대체하지 않는다.
2. 이 스킬을 가이드로 삼아, 같은 저장소에서 다른 에이전트의 CLI를 실행하는 별도
   터미널.
3. 같은 출력 형식을 따르는 사람 / 수동 리뷰. 동일 모델 리뷰어 subagent도 수동
   리뷰로 취급한다 — Fallback Record로 기록한다.

리뷰어는 채팅이 아니라 아티팩트를 읽는다: `AGENTS.md`, `.ai-harness/CONTEXT.md` /
`CURRENT.md` / `AGENT_WORKFLOW.md`, 수락 아티팩트, plan, primary review 기록, diff,
테스트 증거.

## Focus (not duplicating `implementation-review`)

저자와 primary reviewer가 공유하는 사각지대 · 이의 제기 없이 수용된 수락 갭 ·
주어진 것으로 취급된 아키텍처/경계 결정 · 커버리지보다 단언이 약한 테스트 ·
"괜찮아 보인다"로 넘어간 security/data-loss/money 경로 · durable docs 대비
plan-vs-reality drift. primary review에 동의한다면? 그렇다고 직접 밝히고, primary가
드러내지 못한 잔여 위험을 나열한다.

## Severity, Result, Scope

Severity SSOT: `using-bb-harness/severity-definitions.md`. Result: **Ready to merge:
Yes / With fixes / No**; 두 사이클 후 중단, 에스컬레이션(`using-bb-harness` Review
Iteration Pattern). Scope: 제공된 아티팩트/diff 범위 안에 머문다; 발견은 file:line을
인용한다; 새로운 제품 동작, 의존성, 광범위한 재작성을 필수 수정으로 요구하지 않는다;
범위 밖 하드닝은 건드린 경로에서 Critical 결함을 드러내지 않는 한 Minor.

## Fallback Record

```text
Second review: unavailable
Reason: <why>
Compensating review: <self-review / focused reviewer subagent / human review>
Accepted risk: <what could be missed>
User accepted proceeding: <yes/no>
```

독립적인 리뷰를 받을 수 없는 상황에서 Critical 위험이 있는 작업을 사용자의 명시적
수용 없이 승인하지 않는다.

## Output

```text
## Strengths
- <specific observation>

## Findings missed by primary review
### Critical (Must Fix)
### Important (Should Fix)
### Minor (Nice To Have)

## Findings primary review caught (acknowledged)
- <brief; do not re-litigate>

## Result
- Ready to merge: Yes / With fixes / No
- Double-check verdict: primary review was complete / had gaps / requires re-run
- Residual risk:
```

규모가 있는 기록은 `.ai-harness/reviews/YYYY-MM-DD-<topic>-second-review.md`에
저장한다. 리뷰어의 raw 출력이 이 템플릿과 맞지 않으면, 메인 에이전트가 템플릿을
채우고 원문 출력은 같은 기록 안에 raw appendix로 남긴다.
