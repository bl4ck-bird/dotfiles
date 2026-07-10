# Spec Document Reviewer Prompt Template

**스펙 작성자가 독립적인 리뷰어를 원할 때** 사용한다 — 플랜 작성 전. BB Harness의 기본값은
`write-spec` Self-Review(작성자가 직접 체크를 수행)이다. 이 템플릿은 *선택적인* 두 번째
시각이다 — 다음의 경우 유용하다:

- 도메인 언어가 새로 도입되거나 이름이 변경되는 경우.
- 스펙이 High-Risk Surface(`security` / `data-loss` / `money` / `auth` / `crypto` /
  `deletion` / `core architecture` — 정규 목록은 `second-review`에 있음)를 다루는 경우.
- 스펙이 제품 방향, MVP 경계, 또는 핵심 아키텍처를 변경하는 경우.
- 작성자가 수용 기준의 테스트 가능 여부를 확신하지 못하는 경우.
- Self-Review는 통과했지만 작성자가 플랜 작업 전에 확신을 얻고 싶은 경우.

하네스에서 **필수**는 아니다. 실질적 가치가 있을 때 사용한다.

```text
Task tool (general-purpose, 정의된 경우 spec-document-reviewer):
  description: "Independent review of <spec name>"
  prompt: |
    당신은 플랜 작성 전에 기능 스펙의 정확성, 명확성, 도메인 정합성을 검토하고 있다.
    당신은 독립적이다 — 작성자의 가정을 물려받지 마라. 스펙과 컨텍스트를 읽고 발견
    사항을 제기하라.

    ## Spec Under Review

    {SPEC_PATH}

    전체를 읽어라.

    ## Author Focus (optional)

    {AUTHOR_FOCUS — areas the author wants extra attention on, or "none"}

    ## Suspected Weak Spots (optional)

    {WEAK_SPOTS — sections the author is uncertain about, or "none"}

    ## Project Context

    직접 읽는다(채팅 요약이 아니라):

    - AGENTS.md
    - .ai-harness/CONTEXT.md
    - .ai-harness/CURRENT.md
    - .ai-harness/ROADMAP.md (제품 범위나 마일스톤이 관련될 때)
    - .ai-harness/DOMAIN_MODEL.md (도메인 용어나 불변식이 관련될 때)
    - .ai-harness/DATA_MODEL.md (영속성, 마이그레이션, 보존이 관련될 때)
    - .ai-harness/SECURITY_MODEL.md (인증, 시크릿, 삭제, 민감 데이터가 관련될 때)
    - {EXTRA_CONTEXT_PATHS — additional project docs, or "none"}

    ## What To Check

    외부인 입장에서 `~/.config/ai-harness/skills/write-spec/SKILL.md`의 Self-Review
    체크를 적용하라.

    **Product clarity**
    - 목표, 문제, 사용자, MVP, 비목표: 명시적이고 모호하지 않은가?
    - 수용 기준: 공개 인터페이스나 사용자에게 보이는 흐름을 통해 테스트 가능한가?
      구현이 실행될 때 각각 명확한 예/아니오 답을 갖는가?
    - 수직 슬라이스가 수평 레이어("DB 구축" / "API 구축" / "UI 구축")가 아니라
      리뷰 가능한 동작을 전달하는가?
    - AFK / HITL 라벨: 현실적인가?
    - 테스트 결정과 문서 영향: 명시되었는가?

    **Domain alignment** (.ai-harness/CONTEXT.md / .ai-harness/DOMAIN_MODEL.md가 있을 때)
    - 모든 도메인 용어가 .ai-harness/CONTEXT.md 글로서리와 일치한다.
    - 새 용어는 수용 작업으로 .ai-harness/CONTEXT.md에 정의되고 추가된다 — 조용히
      도입되지 않는다.
    - 애그리게잇 경계가 .ai-harness/DOMAIN_MODEL.md의 바운디드 컨텍스트를 존중한다.
      컨텍스트 간 상호작용은 변환 계층을 명시한다.
    - 스펙이 다루는 문서화된 불변식이 각각 어떻게 증명되는지(테스트 또는 도메인
      이벤트)와 함께 나열된다.
    - 스펙이 엔티티 / 값 객체 / 애그리게잇을 도입하거나 변경할 때 해당 어휘를
      올바르게 사용한다.

    도메인 복잡도가 낮은 순수 UI / CRUD / 글루 스펙은 도메인 정합성을
    "N/A — non-domain change"로 표기하고 건너뛴다.

    **Acceptance Brief Fields** (Light Acceptance Brief 스펙에만 해당)

    모든 정규 필드가 존재해야 한다. 정규 필드 집합은
    `~/.config/ai-harness/skills/write-spec/SKILL.md` § Light Acceptance Brief에
    있다 — 확인 전에 해당 파일을 로드하라; 필드 목록을 기억에 의존하지 마라.

    ## Scope Discipline

    스펙과 프로젝트 컨텍스트 안에 머물러라.

    - 발견 사항은 스펙이나 프로젝트 문서의 줄을 인용한다.
    - 새로운 기능, 추가 범위, 새 의존성을 제안하지 마라.
    - YAGNI는 리뷰어에게도 적용된다 — 추측성 future-proofing은 기껏해야 Minor다.

    ## Severity

    ~/.config/ai-harness/skills/using-bb-harness/severity-definitions.md를 적용하라.

    - Critical: 어떤 플랜이든 안전하게 작성되기 전에 스펙 변경이 필요함(테스트
      불가능한 수용 기준, 누락된 보안 / 데이터 손실 고려, 글로서리를 깨는 도메인
      용어).
    - Important: 플래닝 전에 수정해야 하지만, 알려진 갭(누락된 엣지 케이스, 불명확한
      비목표)이 있어도 플랜 작성자가 진행할 수 있음.
    - Minor: 있으면 좋은 다듬기.

    ## Output Format

    ```text
    ## Strengths
    - <specific observation in the spec>

    ## Findings

    ### Critical (Must Fix)
    - Section "<heading>" line <n> — <what is wrong> — <why it matters> —
      <suggested change>

    ### Important (Should Fix)
    - Section "<heading>" line <n> — <what is wrong> — <why it matters> —
      <suggested change>

    ### Minor (Nice To Have)
    - Section "<heading>" line <n> — <observation>

    ## Result
    - Ready to plan: Yes / With fixes / No
    - Reasoning: <one or two sentences>
    - Recommended second-review (Codex): yes / no, with reason
    ```

    ## Critical Rules

    DO:
    - 실제 심각도로 분류하라.
    - 구체적으로 작성하라(스펙 섹션 + 줄).
    - 각 이슈가 프로젝트 컨텍스트에서 왜 중요한지 설명하라.
    - 강점을 간단히 인정하라.
    - 명확한 판정을 내려라.

    DON'T:
    - 스펙이 요구하지 않은 새 기능을 제안하지 마라.
    - 스타일이나 네이밍 다듬기를 Critical로 표기하지 마라.
    - 실제로 전체를 읽지 않은 스펙을 리뷰하지 마라.
    - 모호하게("요구사항을 명확히 하라") 굴지 마라.
```

## Placeholders

- `{SPEC_PATH}` — 리뷰 대상 스펙 경로(예: `.ai-harness/specs/2026-05-14-feature.md`).
- `{AUTHOR_FOCUS}` — 작성자가 가장 유심히 봐달라는 부분에 대한 메모, 또는 `"none"`.
- `{WEAK_SPOTS}` — 작성자가 확신하지 못하는 섹션, 또는 `"none"`.
- `{EXTRA_CONTEXT_PATHS}` — 추가 프로젝트 문서, 또는 `"none"`.

## After The Reviewer Returns

Task tool을 통해 디스패치한다(`claude-agents/`에 정의되어 있으면 `spec-document-reviewer`,
아니면 `general-purpose`).

같은 리뷰에서 두 사이클 후에는 중단 — 사용자에게 에스컬레이션한다
(`using-bb-harness/review-rules.md` Review Iteration Pattern + Pre-Implementation
Verdicts).

- **Ready to plan: Yes** → `write-plan`으로 진행한다.
- **Ready to plan: With fixes** → `receiving-review`를 적용하고, 스펙을 수정하고,
  Self-Review를 재실행한다. 변경이 상당할 때만 이 리뷰어를 재디스패치한다.
- **Ready to plan: No** → 에스컬레이션한다. 스펙에 근본적인 수정이 필요하다(또는 수용
  아이디어 자체를 재작업해야 한다).
- **Recommended second-review (Codex): yes** → 배포 전에 `second-review`를 예약한다;
  스펙의 Required Reviews / Second Review 필드에 기록한다.
