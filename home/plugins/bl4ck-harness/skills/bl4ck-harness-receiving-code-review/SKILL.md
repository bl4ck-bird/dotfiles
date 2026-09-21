---
name: bl4ck-harness-receiving-code-review
description: "리뷰 지적을 실제 요구·코드·근거로 확인해 수정·반증·후속 처리하고 수정 영향에 한정한 재검토를 연결한다."
---

# 리뷰 처리

리뷰 대상 버전과 지적의 조건·근거·해결 기준을 먼저 읽는다. 코드·요구를 확인하지 않고 무조건 수용하거나 방어하지 않는다. 모호한 지적은 필요한 근거를 묻고, 틀렸다면 반증을 남긴다.

명세나 계획이 문제를 요구하더라도 결함을 그대로 수용하지 않는다. 공통 계약이 잘못됐으면 담당 설계·명세 단계로 돌아가 승인 범위를 정리한다. 승인된 범위의 구현 결함은 수정→관련 검증→해당 지적과 영향 범위 재리뷰로 처리한다.

치명·중요 문제와 필수 검증 공백을 해결하기 전 통과 처리하지 않는다. 경미한 관찰은 필요하면 후속으로 기록하되 실제 수용 결함을 임의로 낮추지 않는다. 각 지적의 해결 근거와 누적 수정 횟수를 보존한다. 수정 한도가 끝나면 영향받는 실행을 멈추고 다음 선택을 보고한다.


## 공통 기준

[대화](../using-bl4ck-harness/references/communication.md) · [권한과 검토](../using-bl4ck-harness/references/authority.md) · [문서](../using-bl4ck-harness/references/documents.md) · [품질과 검증](../using-bl4ck-harness/references/quality.md) · [배정과 수정](../using-bl4ck-harness/references/execution.md)을 읽고 현재 작업에 해당하는 규칙을 적용한다. 단독 호출에서도 이 기준은 동일하다.
