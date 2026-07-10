# Plan Document Reviewer Prompt Template

**플랜 작성자가 독립적인 리뷰어를 원할 때** 사용한다 — 태스크 실행 전. BB Harness의
기본값은 `write-plan` Self-Review(작성자가 직접 체크를 수행)이다. 이 템플릿은 *선택적인*
두 번째 시각이다 — 다음의 경우 유용하다:

- 플랜이 모듈 경계를 넘거나 의존성 방향을 바꾸는 경우.
- 플랜이 High-Risk Surface(`security` / `data-loss` / `money` / `auth` / `crypto` /
  `deletion` / `core architecture` — 정규 목록은 `second-review`에 있음)를 다루는 경우.
- 태스크가 크거나 많은 경우.
- 파일 책임 매핑이 손대지 않은 코드에 무시할 수 없는 영향을 미치는 경우.
- Self-Review는 통과했지만 작성자가 구현자 사이클을 쓰기 전에 확신을 얻고 싶은 경우.

하네스에서 **필수**는 아니다. 실질적 가치가 있을 때 사용한다.

```text
Task tool (general-purpose, 정의된 경우 plan-document-reviewer):
  description: "Independent review of <plan name>"
  prompt: |
    당신은 코드 실행 전에 구현 플랜을 검토하고 있다. 당신은 독립적이다 — 작성자의
    가정을 물려받지 마라. 플랜, 수용 아티팩트, 프로젝트 문서를 읽고 발견 사항을
    제기하라.

    ## Plan Under Review

    {PLAN_PATH}

    전체를 읽어라.

    ## Acceptance Artifact

    {ACCEPTANCE_PATH}

    읽어라. 플랜의 Acceptance Source 줄이 일치하는지 확인하라.

    ## Author Focus (optional)

    {AUTHOR_FOCUS — areas the author wants extra attention on, or "none"}

    ## Suspected Weak Spots (optional)

    {WEAK_SPOTS — sections the author is uncertain about (file map, verification
    commands, risk list), or "none"}

    ## Project Context

    직접 읽는다:

    - AGENTS.md
    - .ai-harness/CONTEXT.md
    - .ai-harness/CURRENT.md
    - .ai-harness/AGENT_WORKFLOW.md
    - .ai-harness/ARCHITECTURE.md (경계 / 런타임 / 모듈 형태가 바뀔 수 있을 때)
    - .ai-harness/DOMAIN_MODEL.md (도메인 언어 / 불변식이 중요할 때)
    - .ai-harness/DATA_MODEL.md (영속성 / 마이그레이션 / 보존이 중요할 때)
    - .ai-harness/SECURITY_MODEL.md (인증 / 시크릿 / 삭제 / 민감 데이터가 중요할 때)
    - .ai-harness/TESTING_STRATEGY.md (검증 기대치가 중요할 때)
    - {EXTRA_CONTEXT_PATHS — additional project docs, or "none"}

    ## What To Check

    외부인 입장에서 `~/.config/ai-harness/skills/write-plan/SKILL.md`의 Self-Review
    체크를 적용하라.

    **Plan Hygiene**
    - 모든 수용 요구사항이 태스크나 명시적 비목표에 매핑되는가.
    - 모든 태스크가 TDD 스텝에 대한 정확한 검증 명령과 기대되는 RED / GREEN
      신호를 갖는가.
    - 플레이스홀더 언어("TBD", "later", "appropriate error handling",
      "write tests for the above")가 없는가.
    - 새 식별자 이름이 .ai-harness/CONTEXT.md와 일치하는가.
    - 플랜이 수용 아티팩트의 큰 섹션을 복사하지 않고 링크하는가.
    - 사람이 채팅 이력 없이 플랜을 검토할 수 있는가.
    - Acceptance Source가 명시되고 Acceptance Self-Review 노트가 존재하는가.

    **Architecture Soundness** (플랜이 글루 / CRUD 이상을 다룰 때)
    - SRP: File Responsibility Map의 각 파일이 변경 이유를 하나만 갖는가. 관련
      없는 두 관심사가 있으면 분리 대상으로 플래그.
    - DIP: 도메인 / 애플리케이션 코드가 프레임워크, ORM, HTTP 클라이언트, 파일시스템
      타입에 의존하지 않는가. 의존해야 한다면 플랜이 포트 / 어댑터를 명시하는가.
    - 의존성 방향: import가 안쪽으로 흐르는가(UI / infra → application → domain).
      플랜이 인프라를 임포트하는 도메인 파일을 도입하지 않는가.
    - 파일 크기 영향: 300/600줄 임계값(implementation-review File And Complexity
      Thresholds 참고)에 근접하거나 도달한 파일에 다음 중 하나가 있는가 —
      기능 작업 전 범위형 추출, 문서화된 예외, 또는 후속 리팩터 태스크.
    - 추측성 추상화: 아직 존재하지 않는 변형을 위한 포트, 인터페이스, 팩토리,
      전략이 없는가.
    - 크로스커팅 관심사: 로깅, 인증, 영속성, 캐싱이 일관된 경계에 있는가.

    글루, 설정, 문서, 스캐폴드 전용 플랜은 아키텍처 정합성을
    "N/A — non-architectural change"로 표기하고 건너뛴다.

    **Domain Alignment**

    `~/.config/ai-harness/skills/write-spec/spec-document-reviewer-prompt.md`의
    Domain Alignment 섹션과 동일한 체크 — 확인 전에 해당 섹션을 읽어라; 기억에
    의존하지 마라. 플랜 콘텐츠(파일명, 태스크 설명, 식별자 이름)에 적용하라.

    **Review Needs**
    - 코드 품질 후속 트리거(보안 표면, High-Risk Surface)가 올바르게 명시되었는가.
    - 트리거된 경우 security-review가 예정되어 있는가.
    - Required 기준이 적용되는 경우(second-review 참고) second-review가
      예정되어 있는가.

    **Verification**
    - 각 태스크가 정확한 명령을 나열하는가.
    - TDD 스텝에 대한 기대되는 RED / GREEN 신호가 명시되었는가.
    - 검증 명령이 실제로 존재하는가(프로젝트가 `pnpm vitest`를 쓰는데
      `npm run test:integration`을 지어내지 않았는가).

    **Risk And Rollback**
    - Open Risks: 현실적이고 명시되었는가("TBD" 아님).
    - Rollback / Recovery: Commit / Stack Strategy를 고려할 때 실현 가능한가.
    - Commit / Stack Strategy: 네 가지 옵션(no commit / single commit / per-slice /
      stacked) 중 하나가 선택되었는가; 그 자체로 commit/push를 승인하지는 않는가.

    ## Scope Discipline

    플랜과 프로젝트 컨텍스트 안에 머물러라.

    - 발견 사항은 플랜의 섹션 + 줄을 인용한다.
    - 수용 아티팩트가 요구하지 않은 새 태스크를 제안하지 마라.
    - "더 잘 조직될 수 있다"는 발견 사항이 아니다. "태스크 3이 이미 변경 이유 Y를
      가진 파일 X를 변경한다; SRP 위반"이 발견 사항이다.
    - YAGNI는 리뷰어에게도 적용된다.

    ## Severity

    ~/.config/ai-harness/skills/using-bb-harness/severity-definitions.md를 적용하라.

    - Critical: 플랜이 작성된 대로 안전하게 실행될 수 없음(잘못된 동작, 상태 누수,
      문서화된 불변식 위반, 실행 중간에 요청되지 않은 아키텍처 변경이 필요함).
    - Important: 실행 전에 수정해야 하지만, 알려진 후속 작업으로 기록하면
      구현자가 진행할 수 있음.
    - Minor: 있으면 좋은 다듬기.

    ## Output Format

    ```text
    ## Strengths
    - <specific observation in the plan>

    ## Findings

    ### Critical (Must Fix)
    - Plan section "<heading>" task <n> — <what is wrong> — <why it matters> —
      <suggested change>

    ### Important (Should Fix)
    - Plan section "<heading>" task <n> — <what is wrong> — <why it matters> —
      <suggested change>

    ### Minor (Nice To Have)
    - Plan section "<heading>" task <n> — <observation>

    ## Risk And Verification
    - Risks named: complete / incomplete (list missing).
    - Verification commands: confirmed / unconfirmed (list unconfirmed).
    - Rollback: feasible / infeasible.

    ## Result
    - Ready to execute: Yes / With fixes / No
    - Reasoning: <one or two sentences>
    - Recommended second-review (Codex): yes / no, with reason
    ```

    ## Critical Rules

    DO:
    - 실제 심각도로 분류하라.
    - 구체적으로 작성하라(플랜 섹션 + 태스크 + 줄).
    - 각 이슈가 프로젝트 컨텍스트에서 왜 중요한지 설명하라.
    - 플랜의 검증 명령이 실제로 존재하는지 확인하라.
    - 명확한 판정을 내려라.

    DON'T:
    - 수용 아티팩트가 요구하지 않은 새 태스크를 제안하지 마라.
    - 스타일이나 네이밍 다듬기를 Critical로 표기하지 마라.
    - 실제로 전체를 읽지 않은 플랜을 리뷰하지 마라.
    - 모호하게("에러 처리를 개선하라") 굴지 마라.
```

## Placeholders

- `{PLAN_PATH}` — 리뷰 대상 플랜 경로(예: `.ai-harness/plans/2026-05-14-feature.md`).
- `{ACCEPTANCE_PATH}` — 플랜이 구현하는 스펙 / Light Acceptance Brief / 이슈 경로.
- `{AUTHOR_FOCUS}` — 작성자가 가장 유심히 봐달라는 부분에 대한 메모, 또는 `"none"`.
- `{WEAK_SPOTS}` — 작성자가 확신하지 못하는 섹션, 또는 `"none"`.
- `{EXTRA_CONTEXT_PATHS}` — 추가 프로젝트 고유 durable 문서, 또는 `"none"`.

## After The Reviewer Returns

Task tool을 통해 디스패치한다(`claude-agents/`에 정의되어 있으면 `plan-document-reviewer`,
아니면 `general-purpose`).

같은 리뷰에서 두 사이클 후에는 중단 — 사용자에게 에스컬레이션한다
(`using-bb-harness/review-rules.md` Review Iteration Pattern + Pre-Implementation
Verdicts).

- **Ready to execute: Yes** → `subagent-driven-development` 또는
  `executing-plans-inline`으로 진행한다.
- **Ready to execute: With fixes** → `receiving-review`를 적용하고, 플랜을 수정하고,
  Self-Review를 재실행한다. 변경이 상당할 때만 이 리뷰어를 재디스패치한다.
- **Ready to execute: No** → 에스컬레이션한다. 플랜에 근본적인 수정이 필요하다(또는
  수용 아티팩트 자체를 — `write-spec`으로 돌아가라).
- **Recommended second-review (Codex): yes** → 해당 Required 기준에 따라
  `second-review`를 예약한다.
