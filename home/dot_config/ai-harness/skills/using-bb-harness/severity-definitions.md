# Severity Definitions

리뷰 발견 사항 심각도에 대한 하네스 전역 SSOT다. 모든 리뷰 채널(`implementation-review`,
`security-review`, `second-review`)과 `claude-agents/`의 리뷰어 서브에이전트는 이 어휘를
사용한다. 로컬 동의어를 새로 만들지 않는다.

## The Three Levels

- **Critical (Must Fix)** — 배포(shipping)를 막는다.
  - 정확성 결함(잘못된 동작, 잘못된 출력, 잘못된 상태).
  - 데이터 손실 위험(확인 없는 삭제, 승인 없는 비가역적 작업, 유실된 쓰기, 손상된
    퍼시스턴스).
  - 보안/인증/암호 취약점(인젝션, 트래버설, 인증 우회, 유출된 시크릿, 취약한 암호화,
    올바른 경계에서의 인가 누락).
  - 승인 없는 파괴적 작업.
  - 인수 아티팩트의 승인된 동작을 충족하지 못함.
  - 침묵 실패(swallowed exception, 버그를 가리는 폴백).
  - diff가 구현했다고 주장하는 동작에 대한 테스트 누락.

- **Important (Should Fix)** — 다음 단계를 막는다.
  - 다룬 경로의 아키텍처 결함: 잘못된 경계, 프레임워크가 도메인으로 누수, 의존성 방향
    역전, 문서화된 예외 없이 300/600 임계값을 넘긴 파일/함수.
  - 테스트 설계 결함: 목(mock)이 테스트 대상 동작을 제거함, Red-Green-Revert 없이 통과하는
    회귀 테스트, 주장된 기준에 대한 엣지 케이스 커버리지 누락.
  - 이미 거짓이 된 durable doc 주장(`.ai-harness/CONTEXT.md` 글로서리가 최신 상태와
    불일치, `.ai-harness/ARCHITECTURE.md`가 옛 형태를 기술).
  - 실제로 실패할 수 있는 경로에 에러 처리 누락.
  - 다룬 경로의 DDD 위반: ubiquitous-language 드리프트, 누락된 애그리게이트 불변식 테스트,
    번역 없는 cross-context import.

- **Minor (Nice To Have)** — 막지 않는다.
  - 스타일, 네이밍 다듬기, 주석 정리.
  - 최적화 기회(측정된 영향 없음).
  - 범위 밖 개선.
  - 투기적인 future-proofing 우려.
  - 측정된 중복 비용 없는 DRY.
  - 더 명확할 수 있는 주석(정보 손실 없음).

## Untouched-Code Rule

**현재 diff나 아티팩트가 건드리지 않은** 코드에 대한 발견 사항은 기본적으로 Minor다.

예외: 변경이 그 코드를 안전하지 않게 만들 때는 건드리지 않은 코드에서도 Critical이나
Important일 수 있다 — 예를 들어 새 호출부가 이전에는 안전했던 함수에 잘못된 값을 전달하는
경우. 발견 사항은 추측이 아니라 **새로운 unsafety의 명시적 증거**를 제시해야 한다.

이 규칙은 리뷰 범위 크리프(scope creep)를 막는다. "본 모든 문제"를 고치고 싶은 리뷰어가
그것들을 Critical로 승격시키면 사이클이 끝나지 않는다.

## Do Not Promote A Finding

리뷰어는 수정을 관철시키기 위해 발견 사항을 실제 영향보다 높게 승격시켜서는 안 된다.
리뷰어가 "정말 고치고 싶은" 진짜 Minor 발견 사항은 Minor로 남는다 — 구현자의 재량으로
적용하는 것이지, 손을 강제하기 위한 가짜 Important가 아니다.

심각도 인플레이션의 징후:

- 배포 리스크 설명 없이 Critical 발견 사항이 많음.
- 영향이 "더 깔끔할 수 있다" 정도인 Important 발견 사항.
- 사이클에 걸친 재승격("이거 안 고쳤으니 이제 Critical이다").

스스로 escalate하고 있음을 알아차리면 강등한다. hard-stop-after-two-cycles 규칙은
부분적으로 이를 잡기 위해 존재한다.

## Cross-Reference

- `using-bb-harness`의 Review Result Contract(`review-rules.md` 안에 있음)는 `Ready to
  merge?` 답을 게이팅하기 위해 이 정의들을 사용한다.
- `implementation-review`, `security-review`, `second-review`의 Severity 섹션은 여기를
  가리킨다("SSOT: using-bb-harness/severity-definitions.md") — 이 포인터들을 최신 상태로
  유지한다.
- 각 `claude-agents/*-reviewer.md`는 리뷰어에게 이 정의들을 적용하도록 지시한다.

여기서 정의를 변경하면, 같은 변경에서 해당 호출자들을 감사한다.
