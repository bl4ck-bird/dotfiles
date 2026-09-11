---
name: harness-spec
description: 가까운 작업의 요구와 기존 구조를 바탕으로 정상·실패 동작, 데이터·인터페이스 계약, 수용 기준과 구현 선택 범위를 구체화한다.
---

# Behavior Specification

## Inputs and Scope

- 선택한 성과·승인된 요구와 설계·관련 코드와 인터페이스를 읽는다. 작은 변경은 요청과 기존 구조로 맥락이 충분하면 로드맵 없이 시작할 수 있다.
- [상세 명세 기준](references/criteria.md)에 따라 보존할 동작과 바꿀 동작을 구분한다. 중요한 제품·구조 결정은 해당 상위 단계로 돌려보낸다.
- 작성 전 [코드 품질](../harness-review/references/code-quality.md), [작성 규칙](../using-harness/references/authoring.md), [저장 경계](../using-harness/references/storage.md)를 적용한다.

## Specification

문서를 새로 작성할 때 [템플릿](assets/specification.md)을 사용한다. 안내를 실제 내용으로 채우고 무관한 항목은 제거한다. 기존 문서는 필요한 부분만 갱신한다.

`.harness/work/<work-id>/spec.md`에 다음을 작업에 필요한 깊이로 작성한다. 새 작업 식별자는 [식별자 규칙](../using-harness/references/identifiers.md)을 따른다.

| Contract | Content |
| --- | --- |
| 목적·범위 | 결과·포함·제외·상위 요구 |
| 동작 | 정상·실패·경계 조건에서 관찰할 결과 |
| 데이터·상태 | 소유·전이·불변식 |
| 인터페이스 | 입력·출력·오류·부수 효과 |
| 호환성·전환 | 기존 사용자·데이터·호출자 영향 |
| 수용 기준 | 사전 조건·행동·기대 결과와 필요한 근거 종류 |
| 선택 범위·미결정 | 구현 에이전트가 선택할 범위와 먼저 해결할 질문 |

- 기존 공유 계약은 참조하고 긴 정의만 [문서 분리 기준](../using-harness/references/storage.md)에 따라 나눈다. 구체적인 구현 순서·검증 명령은 `harness-plan`에 맡긴다.
- 용어가 동작·상태에 영향을 주면 [도메인 용어](../harness-design/references/criteria.md#domain-terms)를 확인한다. 실패·재시도·취소에는 [실패·복구](../harness-review/references/failure-recovery.md), 권한·보호 데이터 변경에는 [보안 기준](../harness-review/references/security.md)을 적용한다.
- 중요한 실패는 남는 상태·사용자 결과·재시도 허용 여부까지 정한다. 검증할 수 없는 표현이나 모든 입력 조합의 나열을 피한다.
- 확정 계약·위임된 선택 범위·미결정을 구분한다. 중요한 동작 결정을 “적절히 구현”으로 넘기지 않는다.

## Review and Handoff

- [대상 보존·승인 규칙](../using-harness/references/approvals.md)에 따라 요구·설계·명세·근거를 `harness-review`에 전달한다.
- 필수 리뷰를 통과하고 사용자가 승인하면 대상 버전·수용 기준·공유 계약·선택 범위를 `harness-plan`에 넘긴다. 동작을 바꿀 미결정이 남으면 영향받는 계획 확정을 보류한다.
- [축약 기준](../using-harness/references/entry.md)에 맞는 작업은 명세·계획을 구분해 한 문서로 작성하고 함께 검토·승인할 수 있다.
- 명세 승인은 계획 작성의 근거다. 구현에는 검토·승인된 계획도 필요하며, 계획에서 계약이 바뀌면 해당 명세를 다시 검토한다. `CURRENT.md`에 다음 행동을 연결한다.
