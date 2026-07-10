---
name: domain-modeling
description: Use when domain terms are unclear, overloaded, or drifting; when introducing or renaming aggregates, value objects, or bounded contexts; or when .ai-harness/CONTEXT.md / .ai-harness/CONTEXT-MAP.md / .ai-harness/DOMAIN_MODEL.md need updates before a spec or plan touches domain code. Domain-language axis is independent of product-direction; runs alongside product-discovery or pressure-test as needed. 도메인 용어가 불명확하거나 표류할 때, 애그리게잇/값 객체/바운디드 컨텍스트를 도입·재명명할 때 사용.
---

# Domain Modeling

에이전트 플랜을 제품 언어 및 경계와 일치시킨다.

도메인 용어가 불안정할 때 `write-spec` Self-Review에서, 플랜이 경계가 불명확한
도메인 코드를 건드릴 때 `write-plan` Self-Review에서 호출된다. 애그리게잇, 값 객체,
바운디드 컨텍스트를 도입하거나 재명명할 때 직접 호출할 수도 있다.

`implementation-review/ddd-operational-checks.md`는 결과 코드를 검증한다; 이 스킬은
그 체크들이 대조할 모델을 *수립한다*.

## Read First

- `.ai-harness/CONTEXT.md`
- `.ai-harness/CONTEXT-MAP.md`
- `.ai-harness/DOMAIN_MODEL.md`
- `.ai-harness/ARCHITECTURE.md`
- `.ai-harness/adr/`
- 현재 스펙 또는 플랜
- 관련 코드와 테스트

파일이 존재하지 않으면 최종 진실을 지어내는 대신 초기 버전을 제안한다.

## Interview Pattern

한 번에 하나씩 질문하되, 문서나 코드에서 추론할 수 없는 답만 묻는다. 소프트 캡: 약
7개 질문 후 확정/미해결 사항을 요약하고 계속할지 묻는다.

모호한 용어는 즉시 짚는다: "account", "user", "member", "project", "workspace",
"payment", "order", "session", "status", "sync", "delete".

모호한 용어마다 다음을 확정한다:

- 표준 용어
- 피해야 할 동의어
- 정의
- 소유 컨텍스트
- 주요 상태
- 불변식
- 사용 예시

## DDD Modeling

설계를 명확히 하는 개념만 사용한다:

- Entity: 정체성과 생애주기가 중요함.
- Value object: 값에 의한 동등성, 개념을 검증함, 독립적 생애주기 없음.
- Aggregate: 불변식을 보호하는 일관성 경계.
- Domain service: 하나의 엔티티/값 객체에 자연스럽게 속하지 않는 도메인 규칙.
- Application service: 유스케이스와 트랜잭션 경계를 오케스트레이션함.
- Repository/port: 영속성 또는 외부 시스템의 경계.
- Adapter: 도메인 밖의 구현 세부사항.

도메인이 단순하면 의례적인 레이어를 피한다.

## Context Map

여러 서브시스템 또는 바운디드 컨텍스트 → `.ai-harness/CONTEXT-MAP.md`를 갱신한다:

- 컨텍스트 이름
- 책임
- 소유 용어
- 업스트림/다운스트림 관계
- 통합 방식
- 번역 또는 anti-corruption 필요 여부

## Decision Record Rule

되돌리기 어렵고 예상 밖인 트레이드오프에만 ADR(`.ai-harness/adr/NNNN-<title>.md`,
MADR 형식)을 작성한다 — 예: 저장소나 통합 형태를 제약하는 도메인 경계.

## Outputs

**문서 생성이 이 스킬의 출력 계약이다** — 이 파일들은 스캐폴딩이 스텁을 만들어서가
아니라 이 스킬이 실행되었기 때문에 존재한다. 처음 필요할 때 생성하고, 이후 갱신한다:

- `.ai-harness/CONTEXT.md`(표준 용어집 — 이 스킬이 항상 다룸)
- `.ai-harness/DOMAIN_MODEL.md`(엔티티, 불변식, 워크플로 — 모델링될 때 생성)
- `.ai-harness/CONTEXT-MAP.md`(바운디드 컨텍스트가 2개 이상일 때 생성)
- `.ai-harness/ARCHITECTURE.md`(경계가 바뀔 때 갱신을 제안)
- `.ai-harness/adr/NNNN-<title>.md`(Decision Record Rule에 따라)

다음으로 마무리한다:

- 확정된 용어
- 미해결 용어
- 불변식
- 경계 결정
- 다음에 실행할 스킬(Self-Review에서 호출됐다면 호출한 스킬로 복귀; 그렇지 않으면
  기본값은 `write-spec`)
