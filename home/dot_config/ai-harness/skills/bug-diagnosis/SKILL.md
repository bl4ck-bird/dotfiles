---
name: bug-diagnosis
description: Use when fixing bugs, flaky tests, production-like failures, unexpected behavior, or regressions before changing implementation code. After reproduction, hand off to `test-driven-development` for the regression test and fix. 버그·플레이키 테스트·프로덕션 유사 장애·회귀를 구현 코드 수정 전에 진단할 때 사용.
---

# Bug Diagnosis

**Intent**: 버그가 증거로부터 이해된다 — 재현, 가설 수립, 근본 원인 규명 — 어떤 구현
변경보다도 먼저. **Boundary**: 재현 루프가 가능한 동안에는 직관만으로 패치하지 않는다;
버그를 이해하기 전에 리팩터로 범위를 넓히지 않는다; 사용자 동의 없이 깨진 동작에 맞춰
테스트를 바꾸지 않는다; 수정 자체는 `test-driven-development`의 몫이다. **Verify**: 수정
반영 후 재현 재실행이 통과한다(출력 확인).

## Workflow

1. 관찰된 동작과 기대 동작을 다시 서술한다.
2. 가장 짧은 재현 루프를 구축한다 — 대략 다음 순서로: 지점(seam)에서 실패하는 테스트 →
   curl/HTTP 스크립트 → 정상 출력과의 CLI diff → 헤드리스 브라우저 스크립트 → 캡처된
   트레이스 재생 → 버그 경로의 즉석 하네스 → 속성/퍼즈 루프("가끔 틀림") →
   이분(bisection) 하네스(두 상태 사이에서 나타남) → 차분(differential) 루프(동일 입력에
   대한 구/신 비교). 비결정적 버그: 하나의 깔끔한 재현을 쫓기보다 디버깅 가능한 수준까지
   재현율을 끌어올린다.
3. 재현이 올바른 이유로 실패하는지 확인한다.
4. 반증 가능한 가설을 3-5개 세우고, 가장 저렴한 증거부터 확인한다:

```text
Hypothesis: <specific mechanism>
Prediction: <what should be observed if true>
Check: <command/file/log/test>
Result: <confirmed/refuted/unknown>
```

5. 필요할 때만 집중된 계측을 추가한다 — 고유 프리픽스, 정리 계획 포함.
6. 근본 원인을 식별한 뒤 Red-Green-Revert를 위해 `test-driven-development`로 넘긴다
   (수정 전에 회귀 테스트가 실패하고, 최소 변경으로 통과한다).
7. 수정 후: 이번 응답에서 재현을 재실행하고 통과 출력을 읽는다. 임시 계측을 제거하고,
   버그가 규칙을 드러냈다면 durable docs를 갱신한다.

보안/금전/데이터 손실/인증/암호/동시성 버그 → 더 강한 회귀 테스트 또는 명시적 잔존
위험(residual-risk) 노트. 재현이 불가능한 경우 → 이유를 말하고 대신 사용한 증거를
나열한다. 서로 다른 근본 원인을 가진 독립 서브시스템이 2개 이상 →
`dispatching-parallel-agents`, 에이전트별로 이 워크플로를 적용한다.

## Companion Techniques (load on demand, not by default)

- `root-cause-tracing.md` — 콜스택 깊숙이 있는 버그; 트리거까지 역추적한다.
- `defense-in-depth.md` — 잘못된 데이터가 여러 레이어를 통과함; 버그가 구조적으로
  불가능해지도록 검증을 추가한다(근본 원인 식별 후).
- `condition-based-waiting.md` — 플레이키/비동기 경쟁 상태; sleep을 조건 폴링으로
  대체한다.
- `test-pollution.md` — 단독 실행 시 통과, 스위트에서 실패; `find-polluter.sh` 이분 탐색.
- `debugging-pressure-scenarios.md` — 시간/매몰비용/사회적 압박 속에서 워크플로를
  건너뛰고 싶은 충동.

## Output

재현 경로 · 근본 원인 · 수정 요약(`test-driven-development`로 전달) · 회귀 커버리지 ·
검증 명령과 결과 · 잔존 위험.
