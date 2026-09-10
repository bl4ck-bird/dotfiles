# Approval Records

## Document Bundle

작업의 `snapshots/<bundle-record-id>/manifest.json`에 검토 전에 문서 묶음을 보존한다. `<bundle-record-id>`는 `bundle` 기록의 `record_id`이며, 필요한 판단 문서만 포함하고 각 사본은 해당 snapshot 안에 둔다.

| Information | Required Content |
| --- | --- |
| 식별 | `schema_version`, `record_id`, `work_id`, `created_at` |
| 문서 | 원본 경로·사본 경로·`sha256`, 검토 대상 또는 판단 기준의 역할 |

리뷰는 이 묶음을 참조한다. 변경한 내용이 새 검토·승인 대상이 되면 원본을 덮어쓰지 않고 새 묶음으로 보존한다. 매 편집마다 캡처하거나 내용 변경만으로 재승인을 요구하지 않는다.

## Approval Record

작업의 `approvals/<approval-record-id>.md`에 식별 필드와 짧은 본문을 둔다. `<approval-record-id>`는 `approval` 기록의 `record_id`다.

| Information | Required Content |
| --- | --- |
| 연결 | `schema_version`, `record_id`, `work_id`, `bundle_ref`, 해당 묶음의 리뷰 참조 |
| 근거 | 짧은 승인 요청 원문·사용자 응답 원문, 확인 가능한 세션·메시지 참조 |
| 권한 | 승인 범위·조건, 설계 수용·구현·전달 작업의 구분 |

실행 상태는 승인 기록을 참조한다. 상세 권한이 승인된 계획에 있으면 보존된 해당 절을 연결하고 경쟁하는 권한 목록을 만들지 않는다.

명확한 요청에 연결된 “응”도 유효하다. 별도 승인 문구를 강제하지 않는다. 여러 제안 때문에 모호하면 대화를 먼저 확인하고, 중요한 불확실성이 남을 때만 묻는다. 메시지 식별자 부재를 명시하고 참조를 만들거나 기록 생성 시각을 실제 응답 시각으로 대체하지 않는다.

## Later Instructions and Resumption

승인·문서 묶음·리뷰·실제 상태를 함께 확인한다. 유효한 승인 안의 코드 변경은 정상 진행이며 자동 승인 무효화 사유가 아니다. 부족한 승인 근거는 기존 대화·기록에서 먼저 복구한다.

후속 사용자 범위 제한·철회가 우선한다. 기존 승인 기록을 보존하고 변경·철회는 이전 승인과 영향 범위를 연결한 별도 기록으로 남긴다. 변경 후 기존 승인 적용 여부는 [승인 적용](approvals.md#continued-authorization)을 따른다. 적용 판단을 새 사용자 승인이나 과거 리뷰 대상의 변경으로 기록하지 않는다.

위 의미와 위치를 [기록 도구](record-tools.md)의 `capture-docs`·`publish`로 보존한다. 중첩 필드는 `schema bundle`·`schema approval`로 확인하고 [게시 순서](../../harness-execute/references/runtime.md#publication)를 따른다.
