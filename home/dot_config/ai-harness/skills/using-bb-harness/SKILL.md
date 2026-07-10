---
name: using-bb-harness
description: Use when starting any session before non-trivial work — checks the repo for BB Harness markers, picks one of three workflow paths, and routes to the right phase. Falls back to standard agent behavior when the repo does not reference the harness, so it is safe to invoke universally. 사소하지 않은 작업 전 모든 세션 시작 시 사용한다 — 저장소에서 BB Harness 마커를 확인하고, 세 워크플로 경로 중 하나를 선택하며, 올바른 단계로 라우팅한다. 하네스를 참조하지 않는 저장소에서는 표준 에이전트 동작으로 폴백하므로 어디서나 안전하게 호출할 수 있다.
---

# Using BB Harness

보편적 진입점(universal entry point)이다. **Intent**: 사용자가 스킬명을 지정하지 않아도 모든
세션이 올바른 컨텍스트를 로드한 채 올바른 워크플로 경로에 도달한다. **Boundary**: 하네스를
채택하지 않은 저장소에 강제로 적용하지 않는다; 컨텍스트 공백을 메우기 위해
제품·도메인·아키텍처·안전 관련 결정을 임의로 지어내지 않는다. **Verify**: 아래 Output 블록이
어떤 편집보다도 먼저 생성된다.

## Bootstrap

1. 저장소 루트 마커를 확인한다: `AGENTS.md`, `CLAUDE.md`, 또는 `.ai-harness/AGENT_WORKFLOW.md`가
   `BB Harness` 또는 구별되는 BB 스킬명(`using-bb-harness`, `subagent-driven-development`)을
   언급하는지 확인한다. 일반적인 스킬명은 마커로 인정하지 않는다.
2. 마커가 있으면 → 가장 가까운 `AGENTS.md` / `CLAUDE.md`를 먼저 읽고, 이어서
   `.ai-harness/CONTEXT.md`, `.ai-harness/CURRENT.md`, `.ai-harness/AGENT_WORKFLOW.md`, 진행
   중인 인수 아티팩트/플랜, 최근 핸드오프를 읽는다. 아래 Workflow Path에서 경로를 선택한다.
   작업이 명백히 하나의 스킬에 대응하면(버그는 `bug-diagnosis`, 가벼운 동작 변경은
   `test-driven-development`) 해당 스킬을 바로 호출한다.
3. 마커가 없으면 → 한 번만 보고한다: "BB Harness not in this repo. Proceeding with standard agent
   behavior." 여기서 멈춘다.
4. 사소한 질문과 순수 대화는 부트스트랩을 건너뛴다.

핵심 컨텍스트가 없으면 → 질문하거나 최소한의 복구 단계를 제안한다.

## Workflow Path

**세 가지 경로. 세션 시작 시 한 번 결정하고 그 후 고정한다** — 범위가 선택한 경로를 명백히
벗어날 때만 재결정한다(에스컬레이션을 한 줄로 기록한다).

| Path | Criteria | Chain |
| --- | --- | --- |
| **light** | 단일 범위가 명확한 모듈; 제품/도메인/API/데이터/보안 관련 결정 없음 | 직접 편집 또는 `test-driven-development` → `ship-check` |
| **standard** | 그 외의 모든 사소하지 않은 작업(제품 동작, 사용자 워크플로, 도메인 언어, 퍼블릭 API, 퍼시스턴스, 동기화, 외부 연동) | `write-spec` (Self-Review) → `write-plan` (Self-Review) → 실행 → 슬라이스별 `implementation-review` → `ship-check` |
| **high-risk** | High-Risk Surface(`security` / `data-loss` / `money` / `auth` / `crypto` / `deletion` / `core architecture` — 정규 목록은 `second-review`에 있음) 또는 경계/의존성 방향 변경 | standard + `security-review`(트리거된 경우) + `second-review`(필수) |

light와 standard 중 확신이 서지 않으면(파일 3개 이상, 영향 범위 불명확) standard를 선택한다 —
가벼운 스펙/플랜이 무제한 편집보다 저렴하다.

standard/high-risk 체인에서는: `write-spec`은 Light Acceptance Brief 또는 full spec 중 하나를
만든다(기준은 `write-spec` Modes — 이미 명확한 요청에 full spec을 강제하지 않는다); 실행 전에
`using-git-worktrees`; `subagent-driven-development`(호스트가 서브에이전트를 디스패치할 수
없거나 작은 작업 1~3개인 경우 `executing-plans-inline`); durable docs를 건드렸다면 `ship-check`
전에 `docs-sync`.

예외 사항, 모든 경로에 적용: 신규/미구성 저장소 → 먼저 `project-scaffold` · 방향이나 용어가
미확정 → `write-spec` 전에 `product-discovery` / `pressure-test` / `domain-modeling` ·
버그/플레이키 테스트/회귀 → 구현 변경 전에 `bug-diagnosis` · 독립적인 읽기 전용 조사 2건 이상 →
`dispatching-parallel-agents` · 리뷰어가 발견 사항을 반환 → 수정 전에 `receiving-review` ·
사용자 승인된 자율 반복 → `bounded-loop` · 메모리 후보/회고 인사이트 → `retro-capture`.

## Review Channels

네 개의 관측 지점: 스펙 → 플랜 → 구현(슬라이스) → 교차 모델. 세 개의 채널:
`implementation-review`(**Spec compliant ✅/❌** + **Ready to merge? Yes / With fixes / No**,
한 번의 패스, 슬라이스마다 새 서브에이전트), `security-review`, `second-review`(둘 다
**Yes / With fixes / No**). Self-Review는 `write-spec` / `write-plan` 내부의 작성 게이트이고;
`receiving-review`는 피드백 절차이며; `docs-sync` / `ship-check`는 리뷰가 아니라 워크플로
게이트다.

구속력 있는 규칙(SSOT: 이 디렉터리의 `review-rules.md`, `severity-definitions.md` — 다른 곳에
중복 작성 금지): 채널당 리뷰-수정 사이클 **2**회 후 하드 스톱; 다룬 영역(touched surface) 밖의
발견 사항은 기본적으로 **Minor**; 채널당 자동 후속 리뷰는 최대 **1**회(`second-review`는
Required 기준을 충족하면 예외).

## Branch Policy

이번 세션에서 사용자의 명시적 동의 없이는 **보호된 베이스 브랜치**(`main`, `master`,
`develop`, `trunk`, 또는 저장소 지침이 베이스로 지정한 브랜치)에서 구현을 시작하지 않는다.
첫 코드 편집 전에 `git branch --show-current`로 확인한다; 보호된 브랜치라면 light 경로에서도
먼저 `using-git-worktrees`를 호출한다. 읽기 전용 작업은 예외다. 브랜치명: `<type>/<short-slug>`,
프로젝트 컨벤션을 따른다. 마무리는 `ship-check`의 Finishing Options를 거친다 — 조용한
commit-and-push는 없다.

## Evidence Gate

light 편집 → 대상 파일 + 인접 컨텍스트를 먼저 살펴본다. 동작/API/의존성/데이터/보안/인프라
변경 → 실행 경로, 호출부, 제약, 회귀 범위를 먼저 추적한다. 다음 행동이 승인된 플랜 밖에서
동작, API/UX, 네이밍, 퍼시스턴스, 인증, 의존성, 설정, 호환성, 범위, 도메인 언어를 변경한다면 →
먼저 질문한다.

## Phase Loop

각 단계 이후: 해당 단계의 durable artifact와 `.ai-harness/CURRENT.md`를 갱신한다(실질적 변경일
때만); 가장 좁은 범위의 유용한 검증을 실행하거나 해당 없는 이유를 말한다; 다음 단계를 정확히
하나만 추천한다. 승인이 필요한 행동(git 설정, 의존성 실행, 훅, 삭제, commit/stack, 히스토리
재작성, 범위 확장, 미해결된 제품/도메인/아키텍처 결정)에서는 멈춘다. 사용자가 승인한
엔드투엔드 bounded goal은 각 단계마다 묻지 않고 그 범위 안에서 계속 진행한다. 현재 단계의
스킬만 로드한다; 채팅 요약이 아니라 아티팩트 경로를 전달한다; 컨텍스트를 지우기 전에 핸드오프를
작성한다.

## Output

편집 전에 보고한다: 읽은 컨텍스트, 워크플로 경로, 선택한 다음 스킬, 필요한 아티팩트 또는
승인, 다음 안전한 행동.
