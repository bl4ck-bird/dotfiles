---
name: write-spec
description: Use when converting resolved product context, PRDs, feature ideas, issues, or review findings into an acceptance artifact, acceptance criteria, and vertical implementation slices. Direction must already be settled — run product-discovery / domain-modeling first if not. 확정된 제품 컨텍스트나 이슈, 리뷰 발견 사항을 수용 아티팩트와 수직 슬라이스로 변환할 때 사용한다.
---

# Write Spec

**Intent**: 구현 및 리뷰가 가능한 가장 가벼운 수용 아티팩트를 수직 슬라이스로 나눈 것.
**Boundary**: 이미 명확한 작업을 재서술하려고 풀 스펙을 만들지 않는다; Self-Review 없이 아티팩트를
준비 완료로 선언하지 않는다; 방향이 아직 모호하면 먼저 `pressure-test` / `domain-modeling`을
실행한다. **Verify**: Self-Review 체크리스트 통과; 모든 Acceptance Brief 필드 존재; 되돌리기
어려운 결정에는 ADR 작성.

## Modes And Inputs

- **Light artifact mode** (default): 명확한 이슈, 리뷰 발견 사항, PRD 섹션, 또는 승인된 요청이
  수용 소스가 된다. 동작을 확장할 때는 `.ai-harness/CONTEXT.md`, `.ai-harness/CURRENT.md`,
  소스, 기존 코드/테스트를 읽는다.
- **Full spec mode** (`.ai-harness/specs/YYYY-MM-DD-<feature>.md`): 제품 범위, 도메인 언어,
  공개 API, 데이터/스토리지, 인증/보안, 삭제, 동기화, 외부 통합, 또는 사용자 워크플로가 아직
  결정 중일 때. `.ai-harness/ROADMAP.md`와 디스커버리 노트도 함께 읽는다.
- 어느 모드든: 해당 문서가 존재하고 관련 영역을 다룰 때 모델 문서(`DOMAIN_MODEL`, `DATA_MODEL`,
  `SECURITY_MODEL`, `CONTEXT-MAP`)와 관련 ADR을 읽는다.
- 채팅으로만 존재하는 요청 → 플랜은 아래 필드를 Approved Request Anchor에 기록해야 한다.

## Light Acceptance Brief

하네스 전역에서 쓰이는 표준 필드 집합 — 다른 문서는 필드를 다시 나열하는 대신 "Acceptance
Brief Fields (see `write-spec`)"를 참조한다. 필드명을 인라인으로 사용하는 콜사이트(동기화
유지): `using-bb-harness/SKILL.md`, `write-plan/SKILL.md` Preconditions. 아래 필드는 모두
수용 소스(이슈, 리뷰 기록, 플랜 앵커, 또는 짧은 `.ai-harness/specs/` 노트)에 필수로 존재해야
한다:

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

슬라이스는 처음부터 끝까지 리뷰 가능한 하나의 동작을 전달하고, 필요한 모든 레이어를 포함하며,
수용 기준과 테스트 기대치를 갖고, 하나의 집중된 플랜에 담길 만큼 작으며, **AFK**(에이전트가
단독으로 완료) 또는 **HITL**(사용자 판단, 취향, 자격 증명, 배포, 수동 검증이 필요)로
라벨링된다. 수평 슬라이스("DB / API / UI 구축")는 피한다; "사용자가 검증과 영속성을 갖춘 첫
워크스페이스를 생성할 수 있다"와 같은 형태를 선호한다.

## ADR Output Contract

되돌리기 어려운 결정(스토리지 구조, 인증 구조, 외부 의존성, 도메인 경계)을 확정하는 스펙은
이 스킬 출력의 일부로 `.ai-harness/adr/NNNN-<title>.md`(MADR; 템플릿은
`adr/0000-template.md`)를 작성하고 스펙에서 링크한다. 그런 결정이 없으면 → ADR 없음.
안전망 게이트는 `ship-check`가 담당한다.

## Edit-On-Findings Mode

`implementation-review`가 스펙 드리프트를 발견했거나 사용자가 범위를 변경해서 스펙을 수정하는
경우 → 같은 경로의 기존 아티팩트를 업데이트한다(새 파일 없음, 재시작 없음), 각 발견 사항을
처리하고, 변경되지 않은 섹션은 보존하며, Self-Review를 재실행한다.

## Self-Review

아티팩트를 준비 완료로 선언하기 전에 점검한다; 이후 `implementation-review`가 다시
검증한다. 이 체크를 인라인으로 사용하는 콜사이트: `spec-document-reviewer-prompt.md`.

**Product Clarity** — 목표/문제/사용자/MVP/비목표가 명시적임(또는 모든 Brief 필드가 존재);
수용 기준이 공개 인터페이스나 사용자에게 보이는 흐름을 통해 테스트 가능함; 슬라이스가
수직적임; AFK/HITL 라벨이 현실적임; 테스트 및 문서 영향이 명시됨.

**Domain Alignment** (`.ai-harness/CONTEXT.md` / `DOMAIN_MODEL.md`가 존재할 때) — 모든
도메인 용어가 글로서리와 일치함, 새 용어는 수용 작업으로 `CONTEXT.md`에 추가됨; 애그리게잇
경계가 `DOMAIN_MODEL.md`를 존중함, 컨텍스트 간 상호작용은 변환 계층을 명시함; 다루는 불변식이
증명 방법(테스트 또는 도메인 이벤트)과 함께 나열됨 — 증명되지 않은 불변식은 기준이 아니라
미해결 질문임; 엔티티 / 값 객체 / 애그리게잇 어휘가 올바르게 사용됨. 순수 UI/CRUD/글루 →
`N/A — non-domain change`로 표기.

## Independent Review (optional)

- `spec-document-reviewer-prompt.md`(이 디렉터리) — 같은 호스트에서 새로운 시각으로 보는
  서브에이전트. 다음의 경우 가치가 있다: 새로운/이름이 바뀐 도메인 언어, High-Risk Surface
  (정규 목록은 `second-review`에 있음), 제품 방향이나 아키텍처 변경, 또는 Self-Review 후에도
  작성자가 확신이 없을 때.
- `second-review` — 다른 모델을 이용한 재검증; 스펙이 High-Risk Surface를 다룰 때는 필수,
  그 외에는 선택.

Self-Review 단독이 기본값이다. 구현 후 다음 게이트: `implementation-review`.

## Output

보고: 아티팩트 경로 또는 소스 · 슬라이스 · 생성된 ADR(또는 "none — no hard-to-reverse
decision") · AFK/HITL 분할 · 필요한 리뷰 · 권장 다음 단계 · 다음 단계 질문 하나(예:
`write-plan`으로 진행할지?).
