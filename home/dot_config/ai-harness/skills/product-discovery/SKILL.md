---
name: product-discovery
description: Use when brainstorming, starting a new product, side project, major feature, MVP, roadmap, or product direction before writing specs or code. First phase when goal/MVP/non-goals are unsettled; precedes pressure-test and write-spec. 스펙·코드 작성 전 제품 방향(목표/MVP/비목표)을 정리하는 첫 단계에서 사용.
---

# Brainstorming / Product Discovery

아키텍처나 코드 이전에 제품 목표를 명확히 한다. 제품 대면 진입점; 가벼운
브레인스토밍을 포함한다.

## Questions To Resolve

먼저 기존 문서를 확인한다. 실제 모호함을 제거하는 질문만 한다.

- 제품 목표: 어떤 유용한 결과가 존재해야 하는가?
- 주 사용자: 누가 반복적으로 사용할 것인가?
- 페인 또는 job: 이것이 없으면 어떤 문제가 생기는가?
- MVP 경계: 가장 작은 유용한 버전은?
- 비목표: 지금 명시적으로 만들지 않는 것은?
- 성공 신호: 무엇이 MVP가 통했음을 증명하는가?
- 차별점: 범용 클론 대신 왜 이것을 만드는가?
- 제약: 시간, 예산, 스택, 플랫폼, 프라이버시, 오프라인/온라인, 배포.
- 위험: 제품, 기술, UX, 데이터, 보안, 법적, 운영.
- 첫 수직 슬라이스: 가장 먼저 만들고 테스트할 수 있는 것은?

## Output Documents

**`.ai-harness/ROADMAP.md`가 이 스킬의 출력 계약이다**: 디스커버리가 제품 범위,
마일스톤, 비목표를 확정하면 단계를 끝내기 전에 이를 생성하거나 갱신한다 — 로드맵을
채팅에만 남겨두지 않는다. `ship-check`는 이것이 실제 전달 범위와 여전히 일치하는지
확인한다.

다음도 정당하다면 생성하거나 갱신한다:

- 세션이 3개 이상의 결정을 확정하거나 세션이 정리될 때
  `.ai-harness/reviews/YYYY-MM-DD-<topic>-discovery.md`
- 활성 단계, 다음 단계, 블로커, 또는 수용 산출물/플랜이 바뀔 때 `.ai-harness/CURRENT.md`

디스커버리로부터 스펙을 직접 만들지 않는다. 수용 산출물이 필요하면 `write-spec`을
통해 출력을 라우팅한다. 더 깊은 모델 문서(`DOMAIN_MODEL.md`, `DATA_MODEL.md`,
`SECURITY_MODEL.md`, `ARCHITECTURE.md`, `CONTEXT-MAP.md`)는 이를 생성하는 스킬
(`domain-modeling` 등)의 소관이다 — 디스커버리에서 미리 만들지 않는다.

스캐폴딩되지 않은 프로젝트는 먼저 `project-scaffold`를 실행한다(초기 세트:
`CONTEXT.md`, `CURRENT.md`, `adr/` + 호스트 파일).

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

- 제품 디스커버리에서 구현하지 않는다.
- 구체적인 첫 슬라이스 없이 넓은 로드맵을 만들지 않는다.
- 불확실성을 숨기지 않는다. 모르는 것은 open question으로 표시한다.
- 사용자 job을 설명하지 않고 경쟁사 기능을 그대로 복사하지 않는다.
- 얕은 기능 여러 개보다 훌륭한 MVP 워크플로 하나를 우선한다.

## Next Step

1. 결정 사항에 여전히 압박 테스트가 필요하면 `pressure-test`.
2. 도메인 언어가 중요하면 `domain-modeling`.
3. 방향이 수용 산출물을 만들 준비가 되면 `write-spec`.

정확히 하나의 다음 단계를 추천하고 확인을 요청한다. 예: "제품 방향이 정리됐습니다.
다음 단계로 스펙 초안을 작성할까요?"
