---
name: harness-plan
description: 승인된 상세 명세를 수직 슬라이스·구현 태스크·통합 검증과 실행 권한으로 연결하는 계획을 작성한다.
---

# Implementation Planning

## Inputs

- 승인된 명세 버전·수용 기준·설계·위임된 선택 범위를 읽고 관련 코드·테스트·빌드 명령을 확인한다. 기존 경로·명령과 새로 제안하는 항목을 구분한다.
- [계획 기준](references/criteria.md), [코드 품질](../harness-review/references/code-quality.md), [작성 규칙](../using-harness/references/authoring.md)을 적용한다. 중요한 계약 공백은 `harness-spec`으로 돌려보낸다.

## Work Breakdown

문서를 새로 작성할 때 [템플릿](assets/implementation-plan.md)을 사용한다. 안내를 실제 내용으로 채우고 무관한 항목은 제거한다. 기존 문서는 필요한 부분만 갱신한다.

| Unit | Responsibility |
| --- | --- |
| 슬라이스 | 연결된 동작과 수용 기준·통합 검증·독립 리뷰 경계 |
| 태스크 | 한 구현 에이전트가 구현·필요한 검증까지 끝낼 응집된 작업 |
| 실행 순서 | 태스크 안의 테스트·구현·정리 행동. 별도 ID·파일·배정 없음 |

- `.harness/work/<work-id>/plan.md`에 명세·목표·슬라이스·태스크·의존성·완료 범위를 연결한다. [저장 경계](../using-harness/references/storage.md)와 [식별자 규칙](../using-harness/references/identifiers.md)을 따른다.
- 태스크에는 변경 위치·행동·소비/제공 계약·검증·기대 결과를 적는다. 명령 기반 검증은 구체적인 명령·실행 위치·필요한 준비 조건을, 수동 검증은 확인 절차를 명시한다. 실제 호출·데이터 흐름을 연결하는 작업과 통합 검증을 포함한다.
- 테스트·구현·리팩터링마다 태스크를 나누거나 모델→API→화면 순서를 기본으로 삼지 않는다. 공통 기반은 의존성이 정당화할 때 분리한다.
- 큰 계획은 독립적으로 읽을 슬라이스 문서로 나누고 계획을 실행 로그로 바꾸지 않는다. 완성 코드·고정 소요 시간·파일 수를 태스크 조건으로 요구하지 않는다.

## Verification and Authority

- 각 수용 기준을 구현 슬라이스와 검증에 연결한다. [품질 게이트](../harness-review/references/contract.md#quality-gates)의 적용 조건·근거·통과 조건·실패 처리를 계획에 포함한다.
- 검증 선택 전 [테스트 품질](../harness-review/references/test-quality.md)을 읽는다. 보호할 동작·실제 결함 탐지·독립 기대값·기존 검증 대비 가치를 확인한다.
- 유효한 동작 테스트는 실패 확인→구현→통과 확인→필요한 정리 순서로 계획한다. 문서·기계적 수정에 무의미한 테스트를 추가하지 않고 프로젝트 필수 검사는 유지한다.
- 연결된 결과·UI 변경은 [통합·UI 검증](../harness-review/references/integration.md), 관련 실패·복구는 [실패·복구 기준](../harness-review/references/failure-recovery.md), 보안 경계는 [보안 기준](../harness-review/references/security.md)을 읽고 필요한 실제 환경·검증을 정한다.
- [워크트리·병행 작업](../harness-execute/references/worktrees.md)을 검토해 격리 필요성·공유 계약·데이터·테스트 자원과 정리 범위를 명시한다. 파일이 겹치지 않는다는 이유만으로 병행 가능하다고 판단하지 않는다.
- 실제 전달 지점·권한·환경·외부 의존성·사용자 체크포인트를 정한다. 배포가 전달 지점이면 [정상 동작 확인·복구 조건](../harness-finish/references/delivery.md#authorized-delivery)을 계획에 포함한다.
- [수정 한도](../harness-execute/references/retries.md)와 [호출 복구](../harness-execute/references/resources.md)를 적용한다.

## Review and Execution

- [승인 근거](../using-harness/references/approvals.md)를 보존한다. 계획에 적힌 “승인” 문구만으로 권한을 만들지 않는다.
- `harness-review`에 명세·계획·관련 설계·검증 근거를 전달해 요구 누락·연결·순서·검증·병행 충돌·미결정을 검토한다.
- 필수 리뷰 후 사용자가 계획을 승인하면 대상 버전·리뷰·실행 권한·의존성을 `harness-execute`에 넘긴다. 승인 범위의 태스크 사이에서 반복 확인하지 않는다.
- [축약 작업](../using-harness/references/entry.md)은 명세와 계획을 함께 검토·승인할 수 있다. `CURRENT.md`에는 다음 실행과 관련 기록을 연결한다.
