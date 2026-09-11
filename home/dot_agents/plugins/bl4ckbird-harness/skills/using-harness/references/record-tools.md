# Record Tools

## Scope and Invocation

공용 도구는 메인이 선택한 입력의 형식·참조·게시 순서를 검사하고 기록한다. 에이전트 호출, 테스트 실행, 실행 종료, 사용자 승인 해석, 설계 수용, 전달·배포를 대신하지 않는다. 기존 승인 범위 안에서 필요한 기록을 작성하며 도구 사용 때문에 승인을 다시 요청하지 않는다.

플러그인 루트의 `scripts/records.py`를 Python 3.9 이상으로 실행한다. 로컬 파일 시스템의 `dir_fd`, `O_NOFOLLOW`, 원자적 교체를 사용한다. Git 코드 캡처에는 로컬 Git이 필요하다. 외부 패키지·네트워크는 사용하지 않는다. 지원하지 않는 플랫폼·파일 형식·크기는 숨기지 않고 보류한다.

```sh
python3 -B scripts/records.py --help
python3 -B scripts/records.py schema dispatch
python3 -B scripts/records.py template dispatch
python3 -B scripts/records.py state-update --help
```

다른 작업 디렉터리에서는 설치된 플러그인의 실제 `scripts/records.py` 경로를 쓴다. 조회 두 명령 외에는 `--root`에 대상 프로젝트의 `.harness` 경로를 명시한다. 없으면 해당 디렉터리만 생성한다. 프로젝트 지속 활성화 권한은 [진입 규칙](entry.md)을 따른다.

정확한 필드·타입·허용 값·필수 여부는 `schema KIND`가 출력하는 버전 1 JSON Schema가 기준이다. 모든 typed record의 공통 식별자는 `record_id`다. `template KIND`는 작성할 구조만 제공하며 빈 값은 유효한 기록이나 승인으로 취급하지 않는다. 모든 필드는 명시하며 알 수 없는 값은 해당 필드가 허용하는 `null`과 한계 설명으로 남긴다. 임의 필드·불명확한 시각·누락 필드·지원하지 않는 버전은 거부한다.

## Commands

| Command | Input and Result |
| --- | --- |
| `reserve` | `--kind`, `--name`, `--timezone`, 작업 소속 종류에는 `--work-id`. 영구 예약 ID와 예약 참조 반환 |
| `reference` | `--path`: `.harness` 안에 이미 존재하는 파일의 상대 경로와 SHA-256 반환 |
| `put-evidence` | `--source`의 명시한 일반 파일을 `--path work/<work-id>/evidence/...`에 불변 보존. source 경로의 모든 구성요소에 기존 비밀 후보 규칙을 적용 |
| `capture-docs` | `--work-id`, 예약한 `--record-id`, `--documents` JSON 파일. 항목은 `path`, `role`(`target`/`basis`). 문서 묶음 참조 반환 |
| `capture-code` | `--work-id`, 예약한 `--record-id`, `--workspace`, `--workspace-id`, `--scope`, 반복 `--file`. 선택 `--base-commit`, 반복 `--exclude`, `--external-inputs` JSON 목록. 코드 대상 참조 반환 |
| `verify-target` | `--reference`의 `{path, sha256}` JSON 파일. 보존 사본 무결성과 현재 명시 입력의 차이 반환 |
| `publish` | `--input` JSON 파일. 종류·예약·참조·의미상 연결을 검증해 새 불변 기록 게시 |
| `state-update` | `--input` 상태 JSON, `--expected-revision`. 최초는 `-1` → revision `0`, 다음은 기존 값 → 정확히 다음 값 |
| `state-repair` | `--input` 재구성 상태, 예약한 `--record-id`, 실제 원본의 `--expected-sha256`, `--reason`, 근거 참조 목록 `--evidence`. 손상 원본·후보 상태·수리 판단을 보존한 뒤 조건부 교체 |
| `reconcile` | `--work-id`. 원 배정·호스트 관측·결과·시도·라운드에서 불확실 실행, 누락 근거와 상태 불일치 반환 |
| `update-current` | `--input`의 명시한 안내 내용만 게시. 기존 파일 교체에는 `--expected-sha256` 필수 |

성공한 기계적 작업은 JSON과 종료 코드 `0`, 거부는 표준 오류의 JSON과 `2`를 반환한다. `reconcile`의 `status=needs_reconciliation`, `verify-target`의 `matches=false`은 조회 실행 성공과 별개다. 종료 코드 `0`을 작업 수용·실행 종료·검증 통과로 읽지 않는다. dispatch 게시에서는 미완료 배정 충돌과 호출·수정 한도를 검사한다.

## Publication Preconditions

JSON Schema는 필드 구조를 검사한다. `publish`는 실제 경로·참조·다른 기록과의 의미 관계도 검사하므로 구조 검사 통과만으로 게시 가능하다고 판단하지 않는다.

- `dispatch.workspace`는 존재하는 작업 디렉터리의 절대 경로다. `write_paths`는 그 디렉터리 기준 상대 경로이며 reviewer는 `[]`로 둔다. 리뷰 보고 작성 위치는 `.harness` 기준 `report_path`로 지정하며 해당 `work/<work-id>/` 안에 있어야 한다.
- `host.execution_state`가 `unknown`이 아니면 관측을 뒷받침하는 `evidence_refs`가 필요하다. `not_started` 관측의 `background_state`는 `not_applicable` 또는 `ended`다. 실행·종료 관측을 추정으로 채우지 않는다. `not_started`를 참조하는 결과의 `applied=true` 또는 `outcome=completed`는 모순으로 거절한다.
- `state-update`의 `--expected-revision`은 읽은 기존 값이며 입력 상태의 `revision`은 그 다음 값이다. 최초 게시에만 각각 `-1`과 `0`을 사용한다.

## Publication Order

1. [식별자 규칙](identifiers.md)에 따라 종류·상위 범위·실제 시간대를 확인하고 ID를 예약한다. 기존 기록과 예약의 당일 최대 번호 다음을 쓴다. 원문 계획 안에만 있는 기존 식별자는 메인이 함께 대조한다. 사용하지 못한 예약도 보존한다.
2. 입력·권한·코드 대상·실제 근거를 먼저 보존한다. 참조는 `.harness` 기준 `{path, sha256}`이며 자료가 이미 존재해야 한다. `dispatch.report_path`만 앞으로 작성할 위치이므로 아직 없어도 된다.
3. 수정 가설은 `attempt`, 호출 전 의도는 `dispatch`로 게시한다. `attempt`는 문제·가설·시작 대상이고 배정·실제 결과·검증은 후속 기록의 `attempt_ref`로 연결한다. 같은 가설의 남은 검증은 같은 시도를 유지한다.
4. 메인이 실제 호스트 도구를 호출한 뒤 관측은 `host`, 결과는 `result`, 검증은 `verification`, 리뷰 처리 판단은 `disposition`, 라운드는 `round`로 각각 새로 게시한다. 호출 전 기록에 호스트 ID를 추측해 넣지 않는다.
5. 메인이 필수 검증·리뷰·사용자 결정을 확인한 후 `state-update`로 현재 상태를 게시한다. 기록 갱신은 순차 처리한다. `revision`은 낡은 입력을 탐지하며 동시 쓰기를 잠그지 않는다.
6. `update-current`로 파생 안내를 갱신한다. 실패해도 게시된 결과를 덮어쓰거나 에이전트·코드 변경·테스트·배포를 재실행하지 않는다.

승인·리뷰도 JSON 입력으로 작성한다. 도구는 본문을 분리해 JSON frontmatter가 있는 Markdown으로 보존한다. 요청·사용자 응답은 원문이며 알 수 없는 메시지 참조는 `null`이다. 새 grant, 변경 amend, 철회 withdraw는 각각 새 기록이며 뒤의 두 기록은 이전 승인을 참조한다. 응답의 의미와 현재 적용되는 권한은 [승인 계약](approval-records.md)에 따라 메인이 확인한다. 도구의 `Pass` 연결 검사만으로 권한을 생성하지 않는다.

기존 일반 Markdown 리뷰·승인은 바꾸지 않고 원문 참조로 보존할 수 있다. 예약된 typed 기록을 일반 Markdown으로 덮어쓰면 손상으로 거부한다. 과거 자료를 현재 형식에 맞춘 가짜 실행·승인으로 재작성하지 않는다. 읽기·게시·참조 검사는 현재 스키마와 기록 경로를 사용한다. 현재 실행 경로의 미지원 형식이나 손상된 기록은 보류하고 새 빈 상태로 대체하지 않는다.

## Target Identity and Verification

문서 묶음은 명시한 대상·근거의 원본 경로, 사본 경로, 해시, 역할을 보존한다. 검토·승인은 같은 보존 묶음을 참조한다. 현재 원문 편집으로 과거 묶음을 갱신하지 않는다.

코드 캡처는 명시한 상대 파일 경로만 읽는다. 각 파일의 내용·모드·삭제·심볼릭 링크 자체, Git index와 작업 트리, HEAD를 구분한다. 기준 커밋은 실제 확인 가능한 전체 객체 ID만 지정하고 없으면 `null`로 둔다. 별도 커밋을 만들지 않는다. 같은 검증 입력인지 비교할 때 파일 내용·모드·index·HEAD·실행 위치·외부 입력 식별을 함께 확인한다.

입력 목록의 완전성은 메인이 판단한다. 제품 코드 외에 실제 테스트·설정·의존성 잠금 등 필요한 파일을 명시한다. `--exclude`는 생략 사실의 설명이며 `--file`에 지정한 파일을 자동으로 제거하지 않는다. 외부 입력은 `role`, `safe_identity`, `limitation`을 기록한다. 비밀정보는 복사하거나 환경 전체를 덤프하지 않는다. `capture-code`는 명시한 workspace-relative path의 모든 구성요소에 알려진 비밀 후보 규칙을 적용하고 코드 leaf symlink는 따라가지 않고 링크 자체를 보존한다. `put-evidence`는 source 경로의 모든 구성요소에 같은 후보 규칙을 적용하며 leaf symlink를 포함한 일반 파일이 아닌 입력을 거절한다. 내용 자동 비밀 탐지는 보장하지 않으므로 메인이 `put-evidence` 입력도 확인한다.

검증 명령 실행 전·후 각각 코드 대상을 캡처하고 실제 출력 근거를 보존한다. `verification`에는 원문 argv·cwd·시각·환경 식별·수용 기준·기대 결과·실제 결과를 넣는다. 전후 입력은 `target_match=same/changed/unverified`로 구분하며 도구가 선언과 캡처의 일치를 검사한다. 실행 중 입력이 달라졌어도 관측한 test pass는 보존할 수 있으나 완료 증거로 쓰지 않는다. 전후 일치는 중간의 일시적인 동시 변경이 없었다는 보장이 아니다.

실패·러너 오류·테스트 없음·미실행·중단을 passed로 바꾸지 않는다. 태스크 `completion_kind`는 구현, 재현 등 검증 전용, 문서를 구분한다. implementation 완료는 같은 task/slice의 dispatch, completed result, 해당 result가 참조하는 passed verification을 연결하고 `completion_refs`에 결과와 검증을 함께 넣는다. 완료 근거가 되는 result가 직접 참조한 host는 같은 dispatch의 `execution_state=ended`, `background_state=ended/not_applicable` 관측이어야 한다. 미시작 실패 후 재호출 이력은 보존할 수 있지만 미시작 결과 자체는 완료 근거가 아니다. 인라인 구현도 같은 연결을 기록한다. verification의 `task_id`와 `attempt_ref`는 실제 작업과 같아야 한다. 기대한 `assertion_failed`는 `verification_only`에 한해 실제 종료 시각·0이 아닌 종료 코드·출력 참조를 가진 같은 태스크의 typed 검증일 때만 완료 근거가 되며 제품 구현 성공 근거가 되지 않는다. implementation 완료가 `attempt_ref`를 가지면 결과의 `applied=true`가 필요하다. 시도가 없는 정상 no-op 완료에는 `applied=null`을 허용한다. documentation은 메인이 확인한 문서·리뷰 근거를 사용한다. 슬라이스 수용에는 완료된 태스크와 별도 Pass 리뷰가 필요하다.

구현 태스크가 포함된 슬라이스는 `integration_verification_ref`에 최종 통합 검증을 연결한다. 이 검증은 `task_id=null`, `result=passed`, `target_match=same`, `expectation_met=true`여야 하며 리뷰의 코드 대상과 같은 최종 입력을 검증해야 한다. 도구는 `same_code_target`으로 캡처 내용을 비교하므로 같은 코드의 별도 캡처를 허용하며 태스크별 중간 캡처를 모두 최종 코드와 같게 강제하지 않는다. 문서·재현 검증 전용 슬라이스에는 구현 통합 검증을 강제하지 않는다. 최종 대상·수용 기준의 범위 충분성과 리뷰어 독립성 자체는 메인이 확인한다.

## Recovery and Counters

`reconcile`은 로컬 원기록을 읽을 뿐 호스트를 조회하지 않는다. 배정 기록만 있거나 종료 관측이 없거나 백그라운드 종료가 불명확하면 `needs_reconciliation`이다. 보고서가 있어도 실행 종료를 뜻하지 않는다. 메인이 호스트·실제 파일·검증 근거를 대조하고 새 관측과 결과를 게시한다. 실행 종료를 확인하지 못하면 충돌하는 배정·작업 공간 재사용·최종 완료를 보류한다.

동일 logical dispatch의 복구 호출은 이전 배정과 연속 call index를 유지한다. 복구는 `role`, `task_id`, `slice_id`, `attempt_ref`, `scope`, `authority`, `authority_refs`를 유지한다. `model`·`effort`, host/workspace, 보고 위치 같은 실행 환경은 바꿀 수 있다. 최초 호출 외 복구는 두 번이며, 문제 수정 시도는 기본 두 번과 새 근거·다른 접근이 있는 세 번째까지, 슬라이스 수정 라운드는 다섯 번이다. 원기록을 다시 읽어도 숫자를 추가하거나 초기화하지 않는다. 실행 여부가 불명확한 수정 시도는 예약을 유지한다. 명확한 미시작 관측이 있는 경우에만 수정 횟수에서 제외한다. 메인이 문제의 연속성과 변경 권한을 확인하며 새 ID로 한도를 우회하지 않는다.

상태가 손상되면 `state-update`로 덮어쓰지 않는다. `state-repair`에 메인이 원근거로 재구성한 상태와 판단 근거를 제공한다. 도구는 원본 바이트·후보 상태·수리 판단을 불변 보존한 뒤 실제 원본 해시가 같은 경우에만 교체한다. 읽을 수 있는 기존 revision은 정확히 다음 값으로 유지하고, 읽을 수 없는 값은 수리 기록에 `null`로 남긴다. 미확인 배정은 재구성 상태에서도 지울 수 없다. 미지원 버전은 명시적 이관 없이 수리하지 않는다.

수리 기록 게시 후 상태 교체가 실패해도 근거와 원본을 남긴다. 다음에는 실제 파일·이미 게시된 수리 기록을 대조하고 새 수리 판단이 필요하면 새 ID를 쓴다. 불완전한 임시 파일은 유효한 원기록이 아니다. 수리·재조회의 `automatic_actions`는 항상 빈 목록이며 외부 실행을 재생하지 않는다.

`finish_ref`를 게시할 때는 `active_dispatch_refs`도 비어 있어야 한다. 활성·미대조 실행, 미수용 슬라이스, blocker를 finish 기록으로 숨기지 않는다.

## Limits and Checks

한 기록·캡처 내용은 최대 32 MiB다. 디렉터리·장치·경계 밖 경로·기록 내부 심볼릭 링크는 거부한다. 코드 안의 심볼릭 링크는 대상 파일을 따라가지 않고 링크 자체를 보존한다. 미해결 Git index 충돌·서브모듈 내용은 자동 캡처하지 않는다. 해당 입력의 별도 근거와 한계를 메인이 처리한다. 정전 시 무손실 복구는 보장하지 않는다.

도구의 검증 명령은 플러그인 루트에서 `python3 -B -m unittest discover -s tests/records -v`다. 실제 파일 게시·임시 Git 작업 공간·중단과 불확실 실행 반례를 검사한다. 통과 결과는 호스트 세션 종료 조회나 실제 에이전트 행동의 검증을 대체하지 않는다.
