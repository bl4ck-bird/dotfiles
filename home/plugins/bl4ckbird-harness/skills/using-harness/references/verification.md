# Verification Targets and Evidence

## Code Identity

코드 대상과 검증 실행을 분리한다. 작업의 `snapshots/code/<code-target-record-id>/manifest.json`에 다음 정보를 보존한다. `<code-target-record-id>`는 `code_target` 기록의 `record_id`다.

| Information | Required Content |
| --- | --- |
| 식별 | `schema_version`, `record_id`, `work_id`, `workspace_id`, `created_at` |
| 기준·범위 | 기준 커밋·캡처 당시 `HEAD`, 검토/검증 범위와 포함·제외 기준 |
| 파일 | 경로·유형·실행 권한·내용 해시, staged·unstaged·untracked·삭제 상태 |
| 복원 근거 | 보존 변경 내용·필수 외부 입력 참조, 미검증 사항 |

검사한 작업 트리와 커밋할 index를 구분한다. 내용이 다르면 작업 트리 검사 통과를 커밋 대상의 통과로 쓰지 않는다.

## Reconstructability

기준 커밋에서 복원할 수 있는 내용은 참조하고 필요한 변경·신규 내용과 삭제를 명시적으로 보존한다. 커밋 ID만으로 기준 코드를 복원할 수 있다고 가정하지 않는다. 기준 커밋이 없으면 `null`과 범위 내 파일 목록·내용을 보존하며 캡처를 위해 커밋하지 않는다. 같은 대상은 여러 검증에서 재사용할 수 있다.

검증에 필요한 ignored 설정·데이터·빌드 출력을 무조건 제외하지 않는다. 입력 역할·안전한 버전 참조를 기록하되 비밀정보 값이나 대체용 비밀정보 해시는 보존하지 않는다. 재구성할 수 없는 입력의 한계를 남긴다.

## Execution Record

작업의 `evidence/<verification-record-id>/verification.json`에 실행별로 기록한다. `<verification-record-id>`는 `verification` 기록의 `record_id`다.

| Information | Required Content |
| --- | --- |
| 연결 | 코드 대상·태스크/시도·검증하는 수용 기준 |
| 실행 | 명령·인자·작업 디렉터리·시작/종료 시각 |
| 환경 | 관련 런타임/도구 버전·의존성·설정·외부 서비스 식별 |
| 결과 | 종료 코드·검사 결과·기대 결과 충족 여부, 출력·보고·스크린샷 참조 |
| 한계 | 미실행·중단·잘리거나 누락된 출력·환경 불확실성 |

환경 전체를 덤프하지 않고 관련 정보와 비밀정보를 제거한 근거만 보존한다. 예상한 TDD 실패는 해당 단계의 기대 결과일 수 있지만 제품 동작 통과는 아니다.

`assertion_failed`의 기대 실패 완료 수용 조건은 [기록 도구](record-tools.md#target-identity-and-verification)를 따른다. 근거가 부족한 실패 기록은 보존해도 완료로 수용하지 않는다.

## Changes and Reuse

- 관련 입력을 바꾸는 배정을 겹치지 않게 하고 검증 전후 대상을 비교한다. 입력과 의도된 테스트 출력을 구분한다. 변경이 있으면 결과를 보존하되 새 대상의 통과 근거로 쓰지 않는다.
- 전후 해시 일치만으로 실행 중 임시 변경이 없었다고 단정하지 않는다. 동시 변경이 의심되면 격리된 대상에서 다시 검증한다.
- 재사용 전 코드·필수 입력 일치, 의존성·설정·환경 적용성, 실제 검사한 수용 기준, 결과·출력 완전성 및 필수 검사 충족을 확인한다.
- 무관한 문서 변경만으로 전체 검사를 반복하지 않는다. 공유 코드·설정 변경의 영향을 판단할 수 없으면 관련 검증을 다시 한다.

[기록 도구](record-tools.md)의 `capture-code`·`verify-target`·`publish`를 사용한다. 중첩 필드는 `schema code_target`·`schema verification`으로 확인하고 [게시 순서](../../harness-execute/references/runtime.md#publication)를 따른다.
