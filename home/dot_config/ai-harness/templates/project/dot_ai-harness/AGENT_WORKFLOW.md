# Agent Workflow

Document status: stub. TODO claims are not project truth yet. Non-TODO workflow, safety, and quality
rules apply immediately.

프로젝트는 로컬 BB Harness를 사용한다. 전역 워크플로 규칙은 harness 스킬에 있다; 이 파일은 프로젝트
로컬 사용법, 명령, 오버라이드를 기록한다. 호스트 파일(`CLAUDE.md`, `GEMINI.md`)은 호스트 전용
wiring만 담고, 일반적인 내용은 모두 여기를 가리킨다.

## Skill-First

관련 워크플로 스킬을 ad-hoc 프로세스보다 우선한다.

- 모든 세션을 `using-bb-harness`로 시작한다 (universal bootstrap; 마커가 없으면 self-disable).
- 태스크가 명백히 어떤 스킬에 매핑되면 해당 direct matching 스킬을 사용한다.
- 워크플로 경로에 필요한 최소한의 스킬 집합만 사용한다.
- light 태스크에서 관련 스킬을 건너뛸 때는 최종 보고서나 플랜에 스킵 이유를 기록한다.

## Session Start

Prompt:

```text
using-bb-harness를 사용하라.
Task: <태스크 설명>.
AGENTS.md, .ai-harness/CONTEXT.md, .ai-harness/CURRENT.md, .ai-harness/AGENT_WORKFLOW.md, 이 태스크와
관련된 현재 acceptance artifact, 플랜, 리뷰를 읽어라.
편집 전에 워크플로 경로, 선택한 다음 스킬, 필요한 artifact나 승인, 다음 안전한 액션을 보고하라.
```

## Workflow Path

세 가지 경로. 세션 시작 시 한 번 결정하고 이후 고정한다 (SSOT:
`~/.config/ai-harness/skills/using-bb-harness/SKILL.md` Workflow Path):

- **light**: 단일 bounded 모듈, product/domain/API/data/security 결정 없음. 직접 편집이나
  `test-driven-development` → `ship-check`.
- **standard**: 그 외 모든 비자명한 작업. `write-spec` (Self-Review) → `write-plan`
  (Self-Review) → 실행 → 슬라이스마다 `implementation-review` → `ship-check`.
- **high-risk**: High-Risk Surface(canonical list는 `second-review`에) 또는 경계/의존성 방향 변경.
  standard + `security-review` (트리거될 때) + `second-review` (필수).

## Default Standard / High-Risk Flow

```text
product-discovery → pressure-test → domain-modeling      (필요 시, discovery)
  ↓
write-spec      (Self-Review 포함; hard-to-reverse 결정에 대한 ADR output contract)
  ↓
write-plan      (Self-Review 포함; 동일한 ADR contract)
  ↓
using-git-worktrees                                       (isolated workspace)
  ↓
subagent-driven-development   OR   executing-plans-inline
  태스크마다: test-driven-development + controller verification (tests + diff)
  슬라이스마다:
    implementation-review         (spec compliance ✅/❌ + Ready to merge? Yes / With fixes / No)
    security-review               (트리거될 때)
    second-review                 (high-risk 경로: 필수)
    receiving-review              (reviewer 피드백과 수정 사이)
  ↓
docs-sync                        (durable docs가 변경됐을 때)
  ↓
ship-check                       (검증 근거, vocabulary gate, ADR safety net, CURRENT caps)
  ↓
commit / stack / PR / release    (명시적으로 승인됐을 때만)
```

인접 스킬:

- 버그 / flaky 테스트 / 회귀(regression)에는 `bug-diagnosis`.
- 2개 이상의 독립적인 동시 조사에는 `dispatching-parallel-agents`.
- 사용자 승인 하의 자율 반복에는 `bounded-loop` (goal, scope, allowed actions, iteration budget,
  verification gate, stop conditions가 명시된 후에만).
- harness scaffold 추가/갱신에는 `project-scaffold`.

## Acceptance Artifacts

비자명한(non-trivial) 작업은 적절한 무게(weight)로 승인/리뷰된 artifact 하나가 필요하며, 동작과
acceptance criteria를 명시해야 한다. 다음 중 하나일 수 있다:

- `.ai-harness/specs/YYYY-MM-DD-<feature>.md`
- PRD나 issue
- 리뷰 finding
- 테스트 가능한 acceptance criteria를 가진 사용자 승인 태스크

제품 범위, 도메인 언어, API, 데이터/저장소, 인증/보안, 삭제, 동기화, 외부 연동, 사용자 워크플로가
아직 결정 중일 때는 full spec을 사용한다. 이미 명확한 태스크를 다시 서술하기 위해서만 spec을
만들지 않는다.

`~/.config/ai-harness/skills/write-spec/SKILL.md` (Light Acceptance Brief template)의 canonical
Acceptance Brief 필드를 사용한다. 여기서 필드를 다시 나열하지 않는다.

## Review Routing

- Spec 정확성: `write-spec` Self-Review. Plan 정확성: `write-plan` Self-Review.
- 슬라이스마다: `implementation-review` — 단일 reviewer, 한 번의 패스, 두 개의 체크리스트 (spec
  compliance binary ✅/❌, 이어서 quality Ready to merge? Yes / With fixes / No).
  `subagent-driven-development`에서 fresh reviewer subagent로 실행되거나
  (`executing-plans-inline`을 따를 때는 inline skill invocation으로 실행). DDD operational
  checks, SOLID, 파일 크기, Coverage Matrix, durable docs drift의 SSOT.
- diff가 인증, 시크릿, 암호화, 삭제, 신뢰할 수 없는 입력, 민감한 데이터, 파괴적 작업에 닿을 때
  후속으로 `security-review`.
- High-Risk Surface가 닿거나, 경계/의존성 방향이 바뀌거나, 사용자가 독립적인 double-check를 요청할
  때 `second-review`. 기본적으로 다른 모델의 reviewer (`second-review` 참고); 사용 불가할 때는
  fallback을 기록한다.
- reviewer가 finding을 반환할 때마다 `receiving-review` — 구현 전에 검증하고, 틀렸으면 반박하고,
  한 번에 한 항목씩 적용한다.

### Severity And Result Vocabulary

- **Severity**: Critical / Important / Minor (정의는
  `~/.config/ai-harness/skills/using-bb-harness/severity-definitions.md`에).
- **Result**: Spec compliant ✅/❌ + `Ready to merge? Yes / With fixes / No`
  (`implementation-review` dual contract).
- **Stop condition**: 채널당 리뷰-수정 사이클 2회 후 hard stop
  (`using-bb-harness/review-rules.md`).

### When To Ask `second-review` (different-model)

- Required: 변경이 High-Risk Surface(security, data-loss, money, auth, crypto, deletion, core
  architecture)에 닿거나 경계/의존성 방향을 바꿀 때.
- Strongly consider: 큰 diff + 약한 테스트, 여러 모듈을 가로지르는 광범위한 리팩터, primary agent가
  막혔을 때, 사용자에게 보이는 작업에 대해 bounded automation이 제안될 때.
- 그 외에는 Optional. 일상적인 작업에는 Self-Review + `implementation-review`로 충분하다.

## Workflow Continuation

비자명한 phase가 끝날 때마다:

1. 현재 phase, 활성 acceptance artifact/source, 플랜, done, next, blocker, 마지막 검증 중
   하나라도 실질적으로 바뀌면 `.ai-harness/CURRENT.md`를 갱신한다. 같은 세션이 바로 이어지면
   phase 종료 시점에 한 번만 갱신한다. CURRENT.md의 hard cap을 지킨다 (≤ 80줄, Done ≤ 5개 항목 —
   초과분은 `docs-sync` 규칙에 따라 이동).
2. 경로가 명확할 때는 다음 phase 하나만 추천한다.
3. 승인이 필요할 때는 간결한 확인 질문을 한다.

승인된 bounded goal이 명시적으로 다루지 않는 한, setup, 의존성 실행, hook, 삭제, git-history,
commit/stack, product, domain, architecture, data, security 결정을 자동으로 진행하지 않는다.

Accepted-risk 예외는 사용자가 명시적으로 승인했거나 이미 승인된 플랜에 기록된 경우에만 일반 게이트를
건너뛸 수 있다. 건너뛴 게이트, 이유, 리스크, 보완 체크, 사용자 승인, 후속조치/만료를 기록한다.

## Commit And Stack Gate

`ship-check` 이후, commit이나 stack 작업은 사용자, 프로젝트 로컬 지침, 또는 승인된 bounded goal이
명시적으로 허가할 때만 허용된다.

기본 정책:

- 완료된 태스크나 슬라이스가 소유한 파일만 stage한다.
- 히스토리가 중요할 때는 완료된 수직 슬라이스마다 커밋 하나를 우선한다.
- stacked 작업에서는 플랜에 브랜치 순서와 리뷰 대상을 명시한다.
- 커밋이 승인되지 않았으면 제안 메시지와 함께 "ready to commit"으로 보고한다.
- 커밋 메시지, 코드 주석, PR 본문에는 harness vocabulary를 절대 포함하지 않는다: slice/task ID
  (M1, I1, S0…), 스킬명, "BB Harness", `.ai-harness/` 경로 없음 (`ship-check`의 vocabulary gate).

## Required Checks

프로젝트별 명령:

- Install: TODO
- Test: TODO
- Typecheck: TODO
- Lint: TODO
- Build: TODO
- E2E/manual: TODO
- Config validate/reload: TODO

자동화된 커버리지에는 TDD와 프로젝트 훅(예: lefthook)을 우선한다. 자동화된 테스트나 훅으로 동작을
잘 커버할 수 없을 때만 manual/browser 검증을 추가한다.

## Artifact Rules

문서는 사전 scaffold된 폴더가 아니라 스킬 output contract에 의해 생성된다. 초기 집합은
`CONTEXT.md`, `CURRENT.md`, `adr/`이며, 나머지는 생성 스킬이 실행될 때 나타난다.

- 현재 phase, 활성 acceptance artifact/source, blocker, 마지막 검증, 다음 액션 →
  `.ai-harness/CURRENT.md` (위의 hard cap).
- 되돌리기 어려운 결정(저장소 형태, 인증 구조, 외부 의존성, 도메인 경계)
  → `.ai-harness/adr/NNNN-<title>.md` (MADR; `write-spec` / `write-plan`이 생성, `ship-check`에서
  safety-net).
- 제품 범위, 마일스톤, non-goal → `.ai-harness/ROADMAP.md` (`product-discovery`가 생성;
  `ship-check` 체크리스트로 갱신).
- 도메인 언어 → `.ai-harness/CONTEXT.md`; 더 깊은 모델(`DOMAIN_MODEL.md`, `CONTEXT-MAP.md`)은
  `domain-modeling`이 실행될 때 생성.
- 아키텍처/데이터/보안/테스팅 모델 → 해당 관심사가 실제로 결정될 때 트리거 스킬이 생성. 없는 것이
  정상이며 gap이 아니다.
- 단일 기능의 구현 세부사항 → `.ai-harness/plans/`.
- 리뷰 기록과 handoff → `.ai-harness/reviews/`.
- README는 사용자 대상, 상위 수준 내용을 유지한다.

## Bounded Loop Prompt

```text
bounded-loop를 사용하라.
Goal: <구체적인 결과>.
Allowed scope: <파일/모듈/문서/명령>.
Allowed autonomous actions: <정확한 파일 영역, 명령, 리뷰/수정 범위, worker-agent 사용 여부>.
Forbidden actions: <설정/의존성/훅/git 히스토리/삭제/배포 등>.
Iteration budget: <최대 반복 횟수나 timebox>.
Verification gate: <test/typecheck/lint/build/manual check>.
범위가 확장되거나, 같은 이유로 검증이 두 번 실패하거나, product/domain/architecture 결정이
바뀌거나, 승인되지 않은 worker 범위가 필요하거나, setup/destructive/git-history 액션이 필요하면
멈추고 확인을 구하라.
```
