---
name: harness-design
description: 제품 방향은 정해졌지만 시스템 책임·경계·공유 계약이나 구조를 좌우하는 가정을 결정해야 할 때 큰 틀을 설계한다.
---

# System Design

## Inputs and Scope

- 승인된 방향 또는 동등하게 확립된 요구, 기존 코드·인터페이스·데이터·운영 제약을 읽는다. 제품 방향의 공백은 `harness-discover`로 돌려보낸다.
- [설계 기준](references/criteria.md)의 깊이와 완료 조건을 적용한다. 관찰한 현재 구조와 제안할 변경을 구분한다.
- 설계 전에 [코드 품질](../harness-review/references/code-quality.md)을 읽고 책임·의존 방향·추상화·불변식을 판단한다. 작성에는 [작성 규칙](../using-harness/references/authoring.md)과 [문서 분리 기준](../using-harness/references/storage.md)을 적용한다.

## Design and Validation

| Subject | Decisions |
| --- | --- |
| 구조 | 구성 요소의 책임·경계·의존 방향 |
| 계약 | 데이터 소유·상태·핵심 인터페이스·불변식 |
| 흐름 | 정상 동작과 중요한 실패·복구 경로에서 각 구성 요소의 역할 |
| 가정 | 구조 선택을 좌우하는 전제와 검증 결과·한계 |
| 후속 작업 | 선행 의존성·먼저 해소할 위험·상세 명세에 남길 질문 |

- 용어가 계약에 영향을 주면 [도메인 용어](references/criteria.md#domain-terms), 중요한 실패 경로에는 [실패·복구](../harness-review/references/failure-recovery.md), 신뢰·권한·보호 데이터 경계에는 [보안 기준](../harness-review/references/security.md)을 읽는다.
- 문서·기존 코드로 확인 가능한 가정은 먼저 확인한다. 실험이 필요하면 승인 범위에서 작게 수행하고 판단 기준·환경·실제 결과·설계 영향을 남긴다.
- 의례적인 계층이나 전체 구현 태스크·일정을 만들지 않는다. 다음 단계에서 풀 질문은 해결 시점과 재검토 조건을 명시한다.

## Records and Approval

문서를 새로 작성할 때 [템플릿](assets/system-design.md)을 사용한다. 안내를 실제 내용으로 채우고 무관한 항목은 제거한다. 기존 문서는 필요한 부분만 갱신한다.

- [저장 경계](../using-harness/references/storage.md)에 따라 `.harness/architecture/index.md`에는 개요·탐색 경로, 주제별 문서에는 독립적으로 검토할 설계를 둔다.
- 중요한 선택은 `.harness/decisions/<decision-id>.md`에 맥락·대안·결과를 기록한다. [식별자 규칙](../using-harness/references/identifiers.md)을 따르며 사소한 내부 선택마다 문서를 만들지 않는다.
- 제안·승인·구현 상태를 구분한다. 미승인 제안으로 현재 기준 문서를 덮어쓰거나, 승인만으로 구현됐다고 기록하지 않는다.
- [대상 보존·승인 규칙](../using-harness/references/approvals.md)에 따라 설계·요구·결정·검증 근거를 `harness-review`에 전달한다. 중요한 설계 변경은 사용자와 검토한다.

## Next Stage

- 설계 준비 조건과 필수 리뷰가 충족되고 사용자가 승인하면 `harness-roadmap`에 구조·공유 계약·의존성·위험·남은 질문을 넘긴다.
- 중요한 가정이 해소되지 않으면 영향받는 설계를 보류한다. 유효한 기존 결정을 다시 열지 않고 필요한 범위만 조사한다.
- `CURRENT.md`를 갱신한다. 실제 구현 이후의 설계 상태 갱신은 `harness-finish`의 문서 동기화로 연결한다.
