---
name: bl4ck-harness-subagent-driven-development
description: "승인된 계획을 파일 인계와 독립 리뷰를 사용해 하위 에이전트에 배정·검증하며 실행한다. 위임 도구와 권한이 있을 때 적용한다."
---

# 하위 에이전트 기반 실행

## 준비

명세·계획·공유 제약과 실제 승인 범위를 읽는다. [실행 방식](../using-bl4ck-harness/references/execution.md)과 [상태 복원](../using-bl4ck-harness/references/state.md)을 적용한다. 계획별 status가 해당 변경을 가리키는지 확인하고 미완료 실행을 먼저 대조한다. 다른 변경의 완료 기록으로 작업을 건너뛰지 않는다.

전체 변경의 기준 Git 커밋과 기존 사용자 변경을 기록한다. Git이 없거나 커밋하지 않는 작업은 영향받는 파일의 기준 사본·목록을 기록한다. 리뷰에서 새 파일·미추적 변경도 누락하지 않는다. 격리가 필요하면 `bl4ck-harness-using-git-worktrees`를 사용한다.

실행 전 공유 파일·생산/소비 인터페이스·작업 순서가 충돌하지 않는지 실제 계획을 대조한다. 사소한 계획 오류는 명세에 맞춰 근거와 수정 내용을 기록한다. 중요한 설계·권한 변경은 해당 단계로 되돌린다.

## 작업 반복

1. `evidence/`에 해당 작업의 목표·공유 제약·입출력 계약·검증·권한을 담은 짧은 배정 파일을 만든다. 전체 계획이나 대화 이력을 복사하지 않는다. 기준 명세와 해당 작업의 참조를 연결한다.
2. [구현자 인계](references/implementer.md)에 따라 구현자를 배정하고 호스트 식별자와 보고 위치를 status에 기록한다. 동일 형태의 작은 수정은 묶는다. 기본 구현은 순차로 수행한다.
3. 구현 보고의 실제 파일·테스트·우려를 확인한다. `완료`, `우려 있음`, `정보 필요`, `보류`를 구분해 부족한 근거를 보완한다.
4. 실제 시작점부터 현재 변경까지 검토 자료를 파일로 준비한다. 마지막 커밋 하나만 사용하지 않는다. `bl4ck-harness-requesting-code-review`로 독립 리뷰어 한 명에게 명세·품질 두 판정을 받는다.
5. 유효한 문제는 원 구현자 재개→관련 검증→수정 범위 재리뷰로 처리한다. 동일 작업에서 최대 5회이며 실패를 자동 수용하지 않는다. 수정·호출 횟수는 status에서 유지한다.
6. 실제 근거를 확인한 뒤 상태와 CURRENT를 갱신하고 다음 준비된 작업을 진행한다. 승인 범위의 작업마다 계속할지 묻지 않는다.

구현자·리뷰어는 추가 위임과 공유 상태 변경을 하지 않는다. 메인은 검토를 피하려고 직접 고친 결과를 통과 처리하지 않는다. 직접 수정해야 하면 동일한 독립 검토를 다시 받는다.

## 통합

작업별 통과만으로 전체 완료하지 않는다. 계획된 통합 검증과 변경 전체의 독립 검토를 수행하고, 같은 근거에 충분히 포함된 검토를 형식상 반복하지 않는다. 최종 검토는 연결·수용 기준·남은 지적과 내부 정보 노출을 확인한다. `bl4ck-harness-finishing-a-development-branch`로 문서와 전달을 마무리한다. 기록을 자동 삭제하지 않는다.


## 공통 기준

[대화](../using-bl4ck-harness/references/communication.md) · [권한과 검토](../using-bl4ck-harness/references/authority.md) · [문서](../using-bl4ck-harness/references/documents.md) · [상태와 재개](../using-bl4ck-harness/references/state.md) · [품질과 검증](../using-bl4ck-harness/references/quality.md) · [배정과 수정](../using-bl4ck-harness/references/execution.md) · [실행 환경](../using-bl4ck-harness/references/platforms.md)을 읽고 현재 작업에 해당하는 규칙을 적용한다. 단독 호출에서도 이 기준은 동일하다.
