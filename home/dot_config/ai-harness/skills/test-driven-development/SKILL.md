---
name: test-driven-development
description: Use when implementing any feature, behavior change, or refactor — write the failing test first, watch it fail for the right reason, then write the minimal code to pass. For bug fixes, run `bug-diagnosis` first to reproduce; then return here for the regression test and fix. 기능, 동작 변경, 리팩터를 구현할 때 사용한다 — 실패 테스트를 먼저 작성하고 올바른 이유로 실패하는지 확인한 뒤 최소 코드로 통과시킨다.
---

# Test-Driven Development (TDD)

**Intent**: 모든 프로덕션 코드 변경은 먼저 실패하는 것을 관찰한 테스트로 증명된다 —
테스트가 실패하는 것을 보지 않았다면, 그것이 올바른 것을 테스트하는지 알 수 없다.
**Boundary**: 실패 테스트 없이 프로덕션 코드를 변경하지 않는다; 이 응답에서 방금 읽은
결과 없이 RED나 GREEN을 주장하지 않는다.
**Verify**: 아래 Output 블록이 각 동작에 대한 RED와 GREEN 증거를 담는다.

## When To Use

항상 — 새 기능, 버그 수정(수정 전 회귀 테스트가 실패함), 동작 변경, 동작 보존 리팩터
(먼저 green 베이스라인). 예외는 명시적인 사용자 승인 + 기록된 잔존 리스크 노트가
필요하다: 일회성 프로토타입, 생성된 코드 / 순수 문서 / 테스트 하네스가 없는 기계적
설정, 긴급 수정. 그 기록 없이 "이번만 TDD 건너뛰기"는 합리화일 뿐이다.

## Branch Precondition

첫 프로덕션 편집 전에 현재 브랜치를 확인한다. 보호된 base 브랜치에 있다면 먼저
`using-git-worktrees`를 호출한다 — 전체 규칙은 `using-bb-harness` Branch Policy에
있으며 가벼운 수정에도 적용된다. RED 테스트는 사이클의 첫 커밋 아티팩트다; base가
아니라 피처 브랜치에서 작성한다.

## The Cycle

```text
RED → Verify RED → GREEN → Verify GREEN → REFACTOR → Verify → next behavior
```

- **RED** — 공개 인터페이스, 사용자에게 보이는 흐름, 또는 안정적인 도메인 경계를
  통한 하나의 집중된 실패 테스트. 테스트당 하나의 동작; 이름은 동작을 설명함; 실제
  코드 경로 사용, 불가피할 때만 모킹(`testing-anti-patterns.md`).
- **Verify RED** — 테스트를 실행하고 이 응답에서 결과를 읽는다. 기대한 이유로
  *실패*해야 한다(에러가 아니라). 이미 통과한다면 → 기존 동작을 테스트하는 것이니
  테스트를 고친다. 에러가 나면 → 올바른 이유로 실패할 때까지 고친다. 이 신선한
  증거 규칙은 이 스킬과 `ship-check`가 소유하며, 하네스 전반의 모든 "완료 / 수정됨
  / 통과" 주장에 적용된다.
- **GREEN** — 통과하는 가장 단순한 구현. 요청받지 않은 옵션, 플래그, "하는 김에"
  정리는 없다.
- **Verify GREEN** — 테스트와 좁은 회귀(인접 테스트, 관련 모듈)를 실행하고 결과를
  읽는다. 대상이 실패하면 → 테스트가 아니라 코드를 고친다. 다른 것이 실패하면 →
  지금 고친다; green 베이스라인은 타협 불가다.
- **REFACTOR** — green 이후에만, 새 동작 없이, 이후 다시 검증한다. 게이트는 아래
  참고.

수직으로 인터리브한다: 테스트 → 구현 → 테스트 → 구현. 구현 전에 모든 테스트를
작성하는 것은 TDD가 아니라 계획이다. 테스트보다 먼저 존재하는 코드는 검증된 의미가
없다 — 남아 있던 코드를 적응시키지 말고 테스트부터 사이클을 시작한다; 코드를
적응시키는 것은 여분의 단계가 붙은 사후 테스트일 뿐이다.

## Refactor Gate

GREEN 이후, 다음 RED 전에:

- 변경된 모듈이 변경 이유를 하나만 유지한다.
- 도메인/애플리케이션 로직이 프로젝트가 의도적으로 그 형태를 쓰지 않는 한 UI/프레임워크/
  스토리지/네트워크/파일시스템과 독립적으로 유지된다.
- 인터페이스는 작고 호출자 중심으로 유지된다; 실제 개념을 명명할 때만 중복을 추출한다.
- 남은 주석은 이름·경계로 대체 가능한지 확인한다 — why 주석만 잔존시킨다(기본값은 주석 0).
- 파일/함수 크기 임계값: `implementation-review`(File And Complexity Thresholds).

## Good Tests

선호: 공개 인터페이스와 사용자에게 보이는 동작, `.ai-harness/CONTEXT.md`의 프로젝트
도메인 언어, 내부 리팩터에도 살아남는 테스트, 불변식과 엣지 케이스, 버그에 대한 회귀
커버리지. 피할 것: 프라이빗 헬퍼나 파일 레이아웃 단언, 테스트 대상 동작을 모킹으로
치워버림, 구현 세부사항 중복, 더 작은 공개 인터페이스가 있는데도 넓은 픽스처 사용.
카탈로그: `testing-anti-patterns.md` — 테스트를 작성/변경하거나, 목을 추가하거나,
프로덕션 코드에 테스트 전용 메서드를 추가하고 싶을 때 로드한다.

## Bug Fixes — Red-Green-Revert

`bug-diagnosis`를 먼저 실행하고(재현, 가설 수립, 계측 정리), 여기로 돌아온다. 회귀
테스트는 수정을 되돌렸을 때 실패해야만 수정을 증명한 것이다:

```text
1. Write the regression test.  2. Run on the fix → PASS.  3. Revert the fix.
4. Run → MUST FAIL for the right reason.  5. Restore the fix.  6. Run → PASS.
```

3-4를 건너뛰면 회귀 커버리지는 검증되지 않은 것이다.

## Refactors (behavior-preserving)

먼저 green 베이스라인(스위트를 실행하고 결과를 읽는다); 공개 동작 테스트는 변경되지
않음; 책임, 의존성 방향, 네이밍, 테스트 용이성을 개선하는 작은 단계; 위험한 추출마다
집중 체크.

## Red Flags — stop and restart the cycle

테스트 전 코드 · 첫 실행에 테스트가 통과함 · RED 실패를 설명할 수 없음 · "테스트는
나중에" · 이 응답에서 방금 읽은 결과 없이 RED/GREEN을 주장함.

## Output

완료된 동작마다: 추가/수정된 테스트 · RED 증거(이 응답에서 읽은 실패 메시지) · 구현
요약 · GREEN 증거(이 응답에서 읽은 통과 결과) · 리팩터 완료 또는 생략(이유) · 남은
테스트 갭.
