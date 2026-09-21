---
name: bl4ck-harness-executing-plans
description: "승인된 계획을 현재 에이전트가 순차 실행하고 검증·독립 리뷰·상태 갱신까지 이어 간다. 위임을 사용할 수 없거나 인라인 실행을 선택했을 때 사용한다."
---

# 인라인 실행

명세·계획·승인·변경 상태와 실제 코드부터 확인한다. 재개할 때 미완료 실행과 이미 완료한 결과를 대조한다. 계획의 공유 계약·순서·검증 명령에 모순이 있으면 실행 전에 해결하고 중요한 공백은 담당 설계 단계로 돌린다.

준비된 작업을 하나씩 구현하고 필요한 실패 검증→구현→통과→정리를 수행한다. 작업의 실제 결과·검증·우려와 누적 수정 횟수를 기록한다. 코드를 그대로 계획에 복사하지 않는다. 승인 범위 안에서 매 작업마다 사용자에게 계속할지 묻지 않는다.

작업마다 리뷰어를 호출하지 않고 계획의 연속 구현과 필수 검증을 마친 뒤 `bl4ck-harness-requesting-code-review`로 전체 변경을 새 독립 리뷰어에게 한 번 검토받는다. 중요한 공유 계약·고위험 변경은 계획에 정한 중간 리뷰를 먼저 받는다. 수정이 필요하면 아래 재검토 규칙을 적용하므로 최초 전체 리뷰 한 번이 수정 후 재리뷰를 금지하는 뜻은 아니다. 독립 위임이 없는 환경이면 검사와 자기 검토 결과는 남길 수 있으나 독립 검토가 미완료임을 보고한다. 승인 없는 예외로 완료하지 않는다.

유효한 문제는 수정하고 영향받은 검증·재리뷰를 수행한다. 최대 5회 수정 원칙과 진단 전환은 공통 실행 기준을 따른다. 통합 수용·문서·전달은 `bl4ck-harness-finishing-a-development-branch`로 연결한다.


## 공통 기준

[대화](../using-bl4ck-harness/references/communication.md) · [권한과 검토](../using-bl4ck-harness/references/authority.md) · [문서](../using-bl4ck-harness/references/documents.md) · [상태와 재개](../using-bl4ck-harness/references/state.md) · [품질과 검증](../using-bl4ck-harness/references/quality.md) · [배정과 수정](../using-bl4ck-harness/references/execution.md)을 읽고 현재 작업에 해당하는 규칙을 적용한다. 단독 호출에서도 이 기준은 동일하다.
