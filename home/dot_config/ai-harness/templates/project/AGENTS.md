# Project Agent Instructions

Document status: stub. TODO claims are not project truth yet. Non-TODO workflow, safety, and quality
rules apply immediately.

이 파일, `CLAUDE.md`, `GEMINI.md`, `.ai-harness/`는 gitignore 처리된 에이전트 컨텍스트다 — 자세한 내용은
`project-scaffold`의 Gitignore Policy 참고.

## Project Shape

- Product goal: TODO
- Primary users: TODO
- MVP boundary: TODO
- Explicit non-goals: TODO
- 이 파일은 매 세션 에이전트가 따라야 할 지침에만 집중한다.
- 장기적인 설계 세부사항은 `.ai-harness/CONTEXT.md`와 `.ai-harness/`로 옮긴다.

## Required Reading

비자명한(non-trivial) 수정 전에 다음을 읽는다:

- `.ai-harness/CONTEXT.md`
- `.ai-harness/CURRENT.md`
- `.ai-harness/AGENT_WORKFLOW.md`
- 수정 대상 영역과 관련된 `.ai-harness/adr/` 항목
- 관련 acceptance artifact, 플랜, 리뷰 노트

존재하고 관련 있을 때 조건부로 읽는다 (이 문서들은 생성 스킬 — `product-discovery`, `domain-modeling`
등 — 이 만들며, 없는 것이 정상이다):

- `.ai-harness/ROADMAP.md`, `.ai-harness/CONTEXT-MAP.md`, `.ai-harness/ARCHITECTURE.md`,
  `.ai-harness/DOMAIN_MODEL.md`, `.ai-harness/DATA_MODEL.md`, `.ai-harness/SECURITY_MODEL.md`,
  `.ai-harness/TESTING_STRATEGY.md`

필수/조건부 문서가 `stub` 상태면 non-TODO 규칙을 가이드로 삼고, TODO 항목은 확인 전까지 unknown으로
취급한다.

## Communication

- 시니어 엔지니어링 동료처럼 행동한다: 직접적이고, 구체적이고, 간결하게.
- 리뷰에서는 근거와 findings를 먼저 제시한다.
- 구현 작업에서는 변경 파일, 검증 결과, 문서 영향, 남은 리스크를 보고한다.
- 일반적인 칭찬, 동기부여성 filler, 채팅 전용의 긴 추론은 피한다.

## Evidence And Safety

- 경로, 커밋, API, 설정 키, 환경 변수, 테스트 결과, 도구 동작, 역량을 지어내지 않는다.
- assertion을 약화하거나, 커버리지를 좁히거나, 관련 체크를 건너뛰거나, 깨진 동작에 맞춰 테스트를
  바꿔서 검증을 조작하지 않는다.
- 승인된 플랜이 이미 다루지 않는 한, 동작, API/UX, 네이밍, persistence, 인증, 의존성, 설정, 호환성,
  제품 범위, 도메인 언어를 변경하기 전에 확인을 구한다.
- 인프라 작업에서는 동작 변경 전에 환경, 서비스, 설정, 로그를 점검한다. reload나 restart 전에 설정을
  검증하고, 안전할 때는 reload를 우선한다.
- 프로젝트별 서비스명, 배포 경로, reload 명령, 환경 세부사항은 이 파일이나 전용 프로젝트 문서에
  둔다.

## Architecture Rules

- 도메인 로직은 TODO에 속한다.
- 애플리케이션 오케스트레이션은 TODO에 속한다.
- 인프라 어댑터는 TODO에 속한다.
- UI/인터페이스 로직은 TODO에 속한다.
- 허용된 의존성 방향: TODO.
- 금지된 패턴:
  - TODO

## Quality Rules

- 수평적 기술 단계보다 수직 슬라이스(vertical slice)를 우선한다.
- Behavior 테스트는 public interface, 사용자에게 보이는 흐름, 안정적인 도메인 경계를 검증한다.
- 파일 및 복잡도 임계값은 `~/.config/ai-harness/skills/implementation-review/SKILL.md`
  (File And Complexity Thresholds)를 따른다. 여기서 수치를 다시 정의하지 않는다.
- SOLID를 책임, 의존성 방향, interface 크기에 대한 구체적 체크로 사용한다.
- 도메인 복잡도가 정당화할 때만 DDD를 사용한다.
- 투기적(speculative) 추상화를 도입하지 않는다.

## Development Workflow

`~/.config/ai-harness/skills/using-bb-harness/SKILL.md`를 라우팅 소스로 사용한다. 세션 시작 시 세
가지 워크플로 경로(light / standard / high-risk) 중 하나를 선택하고, 이후 고정한다.

프로젝트별 오버라이드 (프로젝트가 harness 기본값과 다를 때만 추가):

- TODO: 프로젝트별 phase 추가, 스킵, 필수 리뷰.

light와 standard 사이에서 확신이 없다면 (파일 3개 이상, blast radius 불명확)? standard를 선택한다.
변경이 High-Risk Surface나 경계/의존성 방향에 닿으면 high-risk로 격상한다.

Accepted-risk 예외는 사용자가 명시적으로 승인했거나 이미 승인된 플랜에 기록된 경우에만 일반 게이트를
건너뛸 수 있다. 건너뛴 게이트, 이유, 리스크, 보완 체크, 사용자 승인, 후속조치/만료를 기록한다.

비자명한 phase가 끝날 때마다, 활성 phase, 활성 acceptance artifact/source, 활성 플랜, blocker, 완료된
슬라이스, 검증 근거, 다음 액션 중 하나라도 실질적으로 바뀌면 `.ai-harness/CURRENT.md`를 갱신한다.
같은 세션이 바로 이어지면 phase 종료 시점에 한 번만 갱신한다.

## Verification

- Install: TODO
- Test: TODO
- Typecheck: TODO
- Lint: TODO
- Build: TODO
- E2E/manual: TODO
- Config validate/reload: TODO

의존성 설치는 기본적으로 사용자가 관리한다. 에이전트는 패키지/부트스트랩 명령을 제안할 수는 있지만
명시적으로 요청받지 않는 한 실행해서는 안 된다.

## Session Handoff

긴 세션을 정리하기 전에 `.ai-harness/reviews/YYYY-MM-DD-<topic>-handoff.md`를 작성/갱신하며 다음을
담는다:

- 현재 목표
- 완료된 슬라이스
- 열려 있는 질문
- 검증 근거
- 다음 안전한 액션

세션을 정리하거나 일시중지하기 전에 `.ai-harness/CURRENT.md`도 갱신한다.
