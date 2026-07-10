---
name: executing-plans-inline
description: Use when executing an approved implementation plan in the main agent session — for hosts that cannot dispatch subagents, for 1-3 small tasks where dispatch overhead is not worth it, or when the user explicitly asked to keep execution inline. 메인 에이전트 세션에서 승인된 구현 계획을 실행할 때 사용 — 서브에이전트를 디스패치할 수 없는 호스트, 디스패치 오버헤드가 아까운 1-3개의 작은 태스크, 또는 사용자가 인라인 실행을 명시적으로 요청한 경우.
---

# Executing Plans Inline

**Intent**: 승인된 계획이 `subagent-driven-development`와 동일한 게이트를 갖추고 메인
세션에서 실행된다 — 리뷰 스킬이 서브에이전트 디스패치 대신 인라인으로 실행된다.
**Boundary**: 인라인 모드는 리뷰 게이트를 절대 생략하지 않는다; 자신의 작업을 스스로
리뷰하는 동일한 에이전트는 아래의 자체 리뷰 규율을 반드시 적용해야 한다.
**Verify**: 태스크마다 — 새로 실행한 테스트 출력 + diff; 슬라이스마다 — 통과하는 이중
계약을 갖춘 인라인 `implementation-review`.

폴백 스킬. 호스트가 서브에이전트를 안정적으로 디스패치할 수 있다면
`subagent-driven-development`를 우선한다. 다음 중 하나라도 해당하면 대신 이것을
사용한다: 서브에이전트 디스패치 불가 · 1-3개의 작은 태스크 · 사용자가 인라인 유지를
요청함 · 장시간 실행되는 대화형 상태(dev 서버, 감시 중인 테스트 러너, REPL)에 메인
에이전트의 가시성이 필요한 작업.

인라인 모드의 비용: 컨텍스트가 누적되고 태스크 3-4개를 넘기면 자체 리뷰가 약해진다.
계획 도중에 이 문제가 발생하면 `.ai-harness/reviews/`에 핸드오프를 작성하고 남은
태스크는 `subagent-driven-development`로 전환한다 — 계획과 아티팩트가 이미 존재하므로
전환 비용은 핸드오프 작성 한 번뿐이다.

## Preconditions

`subagent-driven-development`와 동일: 기준을 갖춘 승인 아티팩트; File Responsibility
Map + Plan Self-Review를 갖춘 계획; 핵심 문서 읽음; 다음 태스크가 한 번에 완료 가능함.
워크스페이스 격리 필수 — 첫 태스크 전에 `using-git-worktrees`; 보호 브랜치 규칙은
`using-bb-harness` Branch Policy에.

## Execution Loop (Inline)

```text
순서대로 각 태스크에 대해:

  1. 메인 세션에서 구현한다 — 동작 변경에는 test-driven-development, 편집은 File
     Responsibility Map 범위 내로, 각 TDD 단계마다 새 출력을 읽는다.
  2. 다음으로 넘어가기 전에 diff(`git diff`)를 승인 기준 및 계획 태스크와 대조해
     스스로 검사한다.
  3. 태스크를 완료로 표시한다. 계속한다.

각 수직 슬라이스 경계에서:

  4. 누적된 슬라이스 diff에 대해 implementation-review를 실행한다 — 낯선 사람의
     작업을 리뷰하듯 회의적으로. Spec compliant ❌ 또는 With fixes →
     receiving-review, 수정, 재실행; No → 에스컬레이션(계획/승인 아티팩트 수정);
     두 사이클로도 수렴하지 않으면 → 에스컬레이션.
  5. 트리거되면 security-review / second-review를 실행한다(Chain Depth Cap = 자동
     후속 리뷰 1개).
  6. 슬라이스를 완료로 표시한다; 계획 체크리스트와 문서를 업데이트한다; 잔여
     리스크와 검증 증거를 기록한다. 슬라이스별 커밋 → 먼저 ship-check.
  7. 묻지 않고 다음 슬라이스로 계속한다.
```

## Required User Checkpoints

`subagent-driven-development`와 동일한 네 가지: 해결 불가능한 BLOCKED · 같은
슬라이스에서 두 번의 리뷰-수정 사이클로도 수렴하지 않음 · 계획이 승인하지 않은 행동 ·
예정된 `second-review` 없이 diff에 나타난 High-Risk Surface.

## Inline Self-Review Discipline

코드를 작성한 것과 지금 리뷰하는 것이 같은 에이전트다 — 명시적으로 보정한다:

- diff를 기억이 아니라 항상 새 눈으로(`git diff`) 읽는다.
- 각 승인 기준을 있는 그대로 다시 읽고 증거(테스트, 출력, 관찰)와 대조한다.
- 새 증거 없이는 주장하지 않는다 — 명령을 실행하고 이 응답에서 출력을 읽는다.
- 자신의 발견 사항에도 `receiving-review`를 적용한다: 검증하고, 반박하고, 한 번에
  하나씩 적용한다.
- 발견 사항을 선언하기 전에 `using-bb-harness` Review Scope Guard를 확인한다;
  범위 밖 → Minor.
- 각 태스크는 태스크 N-1을 기억하는 것이 아니라 자신의 기준을 다시 읽는 것으로
  시작한다. "이건 괜찮은 걸 안다"는 리뷰를 흉내 내는 것이다 — 게이트를 실제로
  실행한다.

## Output

태스크마다: 완료됨, 변경된 파일, 새 증거와 함께 실행한 검사. 슬라이스마다: 결과와
함께 실행한 리뷰, 업데이트했거나 의도적으로 변경하지 않은 문서, 다음 슬라이스.
`subagent-driven-development`로 전환할 때: 전환 사유와 핸드오프 경로.
