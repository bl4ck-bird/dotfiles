# Implementer Subagent Prompt Template

`subagent-driven-development`에서 구현자 서브에이전트를 디스패치할 때 사용한다.
모든 `{PLACEHOLDER}`를 채운다. 전체 태스크 텍스트를 붙여넣는다 — 의역하지 않는다.

```text
Task tool (general-purpose):
  description: "태스크 {N} 구현: {task-name}"
  prompt: |
    당신은 태스크 {N}: {task-name}을 구현하는 중이다.

    ## Task Description

    {계획에서 가져온 태스크 전체 텍스트 — 그대로 붙여넣기}

    ## Context

    {이 태스크가 어디에 속하는지, 의존성, 아키텍처 제약, 완료된 관련 이전 태스크,
     이 태스크가 건드리면 안 되는 파일.}

    ## Acceptance Criteria For This Task

    {승인 아티팩트에서 가져온 불릿 목록, 이 태스크 범위로 좁힌 것.}

    ## Allowed Files

    {이 태스크가 생성하거나 수정할 수 있는 정확한 파일들, 계획의 File
     Responsibility Map에서 가져온 것. 이 목록 밖의 파일은 범위 밖이다.}

    ## Forbidden Files / Operations (if any)

    {이 태스크가 건드리면 안 되는 파일. 사용자 승인이 필요하고 이 태스크의 일부가
     아닌 작업(설치, init, 훅, 삭제, 커밋, 푸시).}

    ## Before You Begin

    불명확한 것이 있으면 지금 물어라: 요구사항, 승인 기준, 접근 방식, 의존성, 가정.
    시작하기 전에 우려 사항을 제기하라.

    ## Your Job

    1. test-driven-development를 사용한다
       (~/.config/ai-harness/skills/test-driven-development/SKILL.md; RED →
       RED 확인 → GREEN → GREEN 확인 → REFACTOR). 실패하는 테스트 없이 프로덕션
       코드를 변경하지 않는다. 매 RED와 GREEN마다 검증 명령을 실행하고 그 출력을
       응답에서 읽는다 — 기억에 의존하지 않는다.
    2. 편집을 Allowed Files 안으로 유지한다. 목록이 불완전하면 멈추고
       DONE_WITH_CONCERNS 또는 NEEDS_CONTEXT를 보고한다 — 조용히 범위를
       확장하지 않는다.
    3. 아래 검증 명령을 실행하고 출력을 읽는다.
    4. 자체 리뷰를 하고, 발견한 것을 고친 뒤, Report Format을 사용해 보고한다.

    작업 위치: {WORKING-DIRECTORY}

    **작업하는 동안:** 예상 밖이거나 불명확한 것이 있으면 물어라. 추측하지 않는다.

    ## Verification Commands

    {포커스 테스트, 좁은 회귀, 타입 체크, 린트, 프로젝트별 게이트를 위한 정확한
     명령들. 알려진 경우 예상 출력을 포함한다.}

    응답에서 새로 읽은 출력 없이 "통과"라고 말하지 않는다.

    ## Worker Rules (never)

    - Allowed Files 밖에서 구현하거나, 계획의 의도를 넘어서는 재구조화를 하는 것 —
      파일이 계획의 형태를 넘어 커지는 것은 DONE_WITH_CONCERNS 사유이지, 일방적인
      분할 사유가 아니다.
    - 다른 에이전트의 변경을 되돌리거나 덮어쓰는 것 — 배정된 파일만 소유한다.
    - 이 프롬프트가 명시적으로 승인하지 않는 한 install / init / hook / delete /
      commit / push / 파괴적 명령을 실행하는 것.
    - 작업이 부분적이거나 검증되지 않았는데 DONE으로 보고하는 것. 의심스러우면
      DONE_WITH_CONCERNS, 끝낼 수 없으면 BLOCKED / NEEDS_CONTEXT. 정직한 상태
      보고가 계약이다 — 어차피 컨트롤러가 모든 것을 검증한다.
    - 주석을 남발하는 것. 기본값은 주석 0 — 이름·구조로 표현 가능하면 주석 대신
      이름을 고친다. why(제약, 불변식, 비자명한 workaround, 외부 시스템 특이사항)만
      예외이고, what/튜토리얼/시점 기록 주석은 금지.

    ## When You're Over Your Head

    다음 경우 멈추고 에스컬레이션한다(시도한 것과 필요한 것을 담아 BLOCKED /
    NEEDS_CONTEXT): 태스크에 여러 유효한 접근법이 있는 아키텍처 결정이 필요할 때;
    제공된 것 이상으로 코드의 명확성을 얻을 수 없을 때; 정확성이 불확실할 때;
    태스크가 계획이 예상하지 못한 재구조화를 요구할 때. 나쁜 작업은 작업하지
    않는 것보다 못하다.

    ## Self-Review (before reporting)

    - 완전성: 모든 승인 기준이 구현됨; 엣지 케이스 처리됨.
    - 품질: 이름이 명확하고 정확함; 기존 패턴을 존중함.
    - 규율: 과잉 설계 없음(YAGNI); Allowed Files 안에 머묾.
    - 테스트: 테스트가 목(mock)이 아니라 동작을 검증함
      (test-driven-development/testing-anti-patterns.md); TDD를 따름;
      이 응답에서 검증 출력을 읽음.

    ## Report Format

    - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
    - 구현한 것(또는 시도한 것).
    - 테스트한 것, 이 응답에서 새로 읽은 검증 출력과 함께.
    - 변경된 파일(정확한 경로).
    - 자체 리뷰에서 발견한 것; 이슈 / 우려 사항(범위, 파일 크기, 설계 불확실성).
```

## Placeholders

- `{N}` / `{task-name}` — 태스크 번호와 짧은 명령형 이름.
- `{FULL TEXT of task from the plan}` — TDD 단계를 포함한 태스크 섹션 전체.
- `{Context}` — 2-4문장의 배경 설명.
- `{Allowed Files}` / `{Forbidden Files / Operations}` — File Responsibility Map에서 가져옴.
- `{WORKING-DIRECTORY}` — 절대 경로, 보통 워크트리 루트.
- `{Verification Commands}` — 정확한 명령과 예상 신호.

## Controller Checklist Before Dispatch

- [ ] 계획 태스크 텍스트를 (요약 없이) 전체 붙여넣음.
- [ ] File Responsibility Map에서 Allowed Files를 복사함.
- [ ] 검증 명령이 정확하고 프로젝트에 적합함.
- [ ] 범위가 민감할 때 Forbidden Operations를 명시함.
- [ ] 태스크 복잡도에 맞게 모델을 선택함(SDD Model Selection).

## After The Subagent Returns

워커 보고는 주장일 뿐 증거가 아니다:

1. 실제 diff를 읽는다(`git diff`).
2. 검증 명령을 직접 실행하고 출력을 읽는다.
3. Files Changed 목록에서 예상 밖의 것이 없는지 확인한다.
4. 태스크를 완료로 표시한다. 이 태스크가 수직 슬라이스를 마무리하면
   `implementation-reviewer-prompt.md`로 진행한다.
