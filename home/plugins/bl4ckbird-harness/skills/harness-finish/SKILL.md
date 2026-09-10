---
name: harness-finish
description: 승인된 목표의 통합 결과·필수 검증·문서·사용자 수용을 확인하고 허용된 전달과 정리까지 실제 완료 상태를 확정한다.
---

# Final Acceptance and Delivery

## Prerequisites

- [완료 기준](references/delivery.md)의 수용·전달·정리 조건을 읽는다.
- 승인 명세·계획, 합의한 전달 지점, 실제 통합 대상, 리뷰·지적 사항 해결·검증 근거, 필요한 사용자 확인과 정리 권한을 받는다. 배포가 전달 지점이면 서비스 정상 동작 확인 방법과 사전 합의한 복구 조건·권한·절차도 확인한다.
- 미완료 작업·실행 중 작업을 [실행 복원](../harness-execute/references/runtime.md)에 따라 확인한다. 완료 플래그만으로 준비됐다고 판단하지 않는다.

## Integrated Verification

- 수용 기준마다 구현 위치·검증 방법·실제 결과·남은 공백을 연결한다. [품질 게이트](../harness-review/references/contract.md#quality-gates)와 [근거 유효성](../using-harness/references/approvals.md)을 확인한다.
- 유효한 기존 결과는 재사용하고 통합·후속 변경으로 영향받은 검증과 프로젝트 필수 검사를 수행한다. 미실행·건너뜀·테스트 미발견·환경 실패를 통과로 처리하지 않는다.
- [코드 품질·주석](../harness-review/references/code-quality.md)과 [테스트 무결성](../harness-review/references/test-quality.md)을 적용해 실제 계약과 검증의 일치를 확인한다.
- 연결·UI 동작은 [통합·UI 검증](../harness-review/references/integration.md), 관련 실패·복구는 [실패·복구 기준](../harness-review/references/failure-recovery.md), 보안 경계는 [보안 기준](../harness-review/references/security.md)에 따라 결과를 확인한다. 대체된 연결·스크린샷·필수 환경 부재의 한계를 남긴다.
- 필요한 사용자 문서·설정·운영 변경, 무관한 파일, [내부 ID·작업 기록 노출](../using-harness/references/storage.md)을 확인한다.

## Documentation and Records

- [작성 규칙](../using-harness/references/authoring.md)과 [문서 관리](../using-harness/references/storage.md)에 따라 영향받은 현재 설계·결정·로드맵·사용자 문서·`CURRENT.md`를 실제 결과와 맞춘다.
- 중요한 용어가 바뀌었다면 [도메인 정의](../harness-design/references/criteria.md#domain-terms)와 코드의 의미도 대조한다. 무관한 기준 문서를 다시 쓰거나 구현 세부마다 문서를 만들지 않는다.
- 구현한 위치·대상을 명시한다. 로컬·브랜치의 구현을 통합·배포 완료로 기록하지 않는다. 승인된 미구현 부분과 남은 수용 기준을 유지한다.
- [승인 적용](../using-harness/references/approvals.md)에 따라 검증된 사실은 갱신하되 과거 승인·리뷰 대상을 보존한다. 결함을 정당화하려고 명세나 수용 기준을 바꾸지 않는다.

## Delivery and Failure Handling

- 유효한 권한 안의 커밋·PR·병합·배포를 합의한 지점까지 수행하고 실제 결과를 확인한다. 배포는 [정상 동작 확인·복구 조건](references/delivery.md#authorized-delivery)을 적용한다. 권한이 부족하면 먼저 검토 가능한 결과를 준비한 뒤 필요한 승인만 요청한다.
- 승인 범위 결함은 `harness-execute`, 원인 불명은 `harness-diagnose`, 계약 변경은 해당 설계·사용자 검토로 연결한다. 필수 리뷰가 없으면 `harness-review`를 요청한다.
- [수정 한도](../harness-execute/references/retries.md)와 [호출 복구](../harness-execute/references/resources.md)을 유지한다. 최종 확인을 이유로 한도를 초기화하거나 최고 성능 리뷰를 일괄 추가하지 않는다.
- 정리 전 [보존·권한·대상별 정리](references/delivery.md#cleanup)를 확인한다. 사용자 변경·유일한 근거·다른 작업 자원을 보존한다.

## Completion Report

`.harness/work/<work-id>/evidence/finish.md`에 대상·수용 근거·지적 사항 해결·문서 동기화·남은 검사·전달 결과·다음 행동을 기록하고 기존 로그·리뷰를 연결한다.

| Aspect | Recorded State |
| --- | --- |
| 검증 | 충족·실패·미검증 수용 기준 |
| 문서 | 실제 대상과의 일치 및 남은 공백 |
| 사용자 수용 | 필요한 확인의 결과 또는 대기 |
| 전달 | 허용된 지점과 실제 수행 결과 |
| 정리 | 제거·보존 대상과 이유 |

필수 조건이 남으면 전체 완료로 선언하지 않는다. 필요한 사용자 수용이 없는 작업에 의례적 확인을 추가하지 않는다. 사용자에게 변경·검증·남은 제약·실제 전달 상태를 간결하게 보고한다.
