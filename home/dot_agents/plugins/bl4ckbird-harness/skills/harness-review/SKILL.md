---
name: harness-review
description: 탐색·설계·로드맵·명세·계획·구현 결과와 수정 범위를 독립적으로 검토하고 근거 있는 지적 사항·미검증 사항·판정을 반환한다.
---

# Independent Review

## Assignment and Authority

- [리뷰 기준](references/contract.md)의 입력·권한·판정 규칙을 읽는다. 현재 단계의 검토 요청·합의된 절차를 사용하고, 미래 단계 문서나 새 구현 승인을 리뷰 조건으로 만들지 않는다.
- 메인 에이전트는 작성자와 다른 서브에이전트에 검토를 배정한다. [모델 선택](references/models.md)에 따라 모델·추론 수준·이유를 기록한다. 다른 모델 사용 자체를 독립성 조건으로 삼지 않는다.
- 메인 에이전트는 구현 전 리뷰도 [실행 기록 준비 조건](../harness-execute/references/runtime.md)을 확인한다. 호출 전 현재 작업·단계·대상·범위·권한을 기록하고 [호출 복구](../harness-execute/references/resources.md)을 적용한다. 구현 전 리뷰에 가짜 실행 계획·수정 시도를 만들지 않는다.
- 리뷰어는 대상 수정·추가 에이전트 호출을 하지 않는다. 허용된 검증과 자기 리뷰 보고를 맡고, 공유 실행 상태·`CURRENT.md`는 메인 에이전트가 갱신한다. 추가 권한이나 전문가 검토가 필요하면 근거와 범위를 반환한다.

## Inputs and Stage

- 대상 버전·실제 변경, 요구·관련 결정·제약, 제외·보류 범위, 근거·검증 결과, 보고 위치를 받는다. 재검토에는 이전 지적 사항·해결 조건·수정 내용을 추가한다.
- [시점별 프롬프트](references/prompt-selection.md)를 읽고 현재 시점의 지침과 공통 계약만 결합한다.

명세·계획의 축약 묶음은 두 관점을 함께 검토할 수 있다. 최종 검토 지침이 있다는 이유로 모든 완료 작업에 리뷰를 추가하지 않는다.

## Inspection and Verdict

- 작성자 보고는 보조 자료다. 실제 대상·호출자·공유 계약·근거를 확인하고, 의도적으로 미룬 미래 세부를 현재 결함으로 보고하지 않는다.
- 설계·코드 검토에는 [코드 품질·주석](references/code-quality.md), 문서에는 [작성 규칙](../using-harness/references/authoring.md)과 [문서 관리](../using-harness/references/storage.md)를 적용한다.
- 용어가 동작·경계에 영향을 주면 [도메인 용어](../harness-design/references/criteria.md#domain-terms)의 적용 범위·의미·이름 대응을 검토한다. 유효한 맥락별 차이를 보존한다.
- 검증 계획·테스트/설정 변경·근거 의심에는 [테스트 품질](references/test-quality.md)을 읽고, 중요한 오구현이 여전히 통과할 수 있는지 확인한다. 테스트 개수나 길이만으로 판단하지 않는다.
- 관련 실패·복구에는 [실패 기준](references/failure-recovery.md), 보안 경계에는 [보안 기준](references/security.md), 연결·UI 동작에는 [통합·UI 근거](references/integration.md)를 읽는다. 구현·전달 표면에는 [내부 정보 노출 금지](../using-harness/references/storage.md)를 적용한다.
- [지적 사항·판정 계약](references/contract.md#findings)에 따라 근거와 미검증 사항을 구분한다. 필수 조사·검증이 빠졌으면 지적 사항이 없어도 `Pass`가 아니다.

## Report and Re-review

- 메인 에이전트가 [식별자 규칙](../using-harness/references/identifiers.md)에 따라 `.harness/work/<work-id>/reviews/<review-id>.md`를 보고 위치로 지정한다. 리뷰어는 [보고·재검토 계약](references/contract.md#report-and-closure)과 [대상 보존](../using-harness/references/approvals.md)을 따라 작성한다.
- 메인 에이전트에 판정·주요 지적 사항·근거 공백·보고 위치를 반환한다. 수정 처리와 재검토는 같은 보고 계약을 따른다.
- 구현 전 중요한 결정은 사용자 검토로, 승인 범위의 구현 수정은 [기존 수정 한도](../harness-execute/references/retries.md) 안의 실행 루프로 연결한다. 리뷰 통과는 사용자 승인·병합·배포 권한을 대신하지 않는다.
