---
name: using-bl4ck-harness
description: "bl4ck-harness을 프로젝트에 적용하거나 개발 작업을 시작·재개할 때 활성 상태와 현재 근거를 확인해 필요한 스킬로 연결한다. 일반 대화에는 전체 절차를 강제하지 않는다."
---

# bl4ck-harness 진입

프로젝트의 실제 상태와 사용자 요청에서 시작한다. 하위 에이전트로 작업을 배정받았다면 프로젝트 진입을 반복하지 말고 배정과 해당 스킬부터 수행한다.

## 시작과 적용

[대화](references/communication.md), [권한](references/authority.md), [실행 환경](references/platforms.md)을 읽는다. 지정한 프로젝트를 우선하고, 없으면 현재 Git 루트나 사용자 작업 공간을 확인한다. 프로젝트 루트를 변경하지 않는다.

`.harness/config.json`을 확인한다. 명시적 적용·활성화 요청이 있으면 [기록 도구](references/tools.md)의 초기화를 사용한다. 조회·단독 스킬 호출·폴더 존재만으로 지속 활성화하지 않는다. 설정이 손상됐거나 다른 하네스 기록이면 자동 이관하지 않는다.

재개는 [상태와 재개](references/state.md)에 따라 CURRENT·활성 변경·실제 코드·미완료 실행을 대조한다. 작업 기록의 기준 경로와 실제 워크트리가 다르면 배정된 경로를 확인한다. 문서 작성 전 [문서 기준](references/documents.md)을 읽는다.

## 단계 선택

| 현재 필요 | 연결할 스킬 |
| --- | --- |
| 만들 대상·이유·전체 기능이 불명확 | `bl4ck-harness-brainstorming` |
| 신규 제품 또는 공통 구조·기술·도메인 결정 | `bl4ck-harness-design` |
| 성과·순서·의존 관계 정리 | `bl4ck-harness-roadmap` |
| 가까운 기능·변경의 동작과 수용 기준 | `bl4ck-harness-spec` |
| 승인된 명세를 구현·검증 단위로 연결 | `bl4ck-harness-writing-plans` |
| 승인된 계획을 위임해 실행 | `bl4ck-harness-subagent-driven-development` |
| 승인된 계획을 현재 에이전트가 실행 | `bl4ck-harness-executing-plans` |
| 원인 불명 오류·반복된 실패 | `bl4ck-harness-systematic-debugging` |
| 설계·명세·계획의 독립 검토 | `bl4ck-harness-review` |
| 구현 결과의 독립 검토 | `bl4ck-harness-requesting-code-review` |
| 통합 수용·문서 동기화·전달 | `bl4ck-harness-finishing-a-development-branch` |

신규 프로젝트는 제품 탐색 → 전체 설계 → 설계 검토·사용자 합의 → 로드맵 → 가까운 변경의 명세·계획 → 실행으로 연결한다. 기술 스택 이름과 대략적인 기능만 받은 상태를 설계 완료로 판단하지 않는다. 공유 결정이 빠졌으면 scaffold를 포함한 제품 구현으로 넘어가지 않는다.

작고 명확한 기존 변경은 영향받는 명세·계획을 짧게 합칠 수 있다. 오탈자처럼 동작·중요한 결정을 바꾸지 않는 명시적 수정에는 전체 문서와 리뷰 절차를 강제하지 않는다. 중요한 미결정이 드러나면 영향받는 설계로 돌아가고, 이미 유효한 결정은 반복하지 않는다.

선택한 단계와 이유를 짧게 알리고 해당 스킬을 읽는다. 실행 권한·대상·필요한 근거를 함께 넘긴다. 다음 행동이 바뀌면 현재 상태를 맞춘다.
