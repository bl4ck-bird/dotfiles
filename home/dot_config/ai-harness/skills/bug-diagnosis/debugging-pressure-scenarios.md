# Debugging Pressure Scenarios

다음일 때 로드:

- 시간, 소진, 사회적 압박, 매몰 비용 때문에 `bug-diagnosis`를 건너뛰려는("일단
  고쳐보자") 참일 때.
- 재현 없이 `sleep(5000)`, `try { ... } catch {}`, 또는 "임시" 우회책에 손이 갈 때.
- 권위자가 근본 원인 분석 없이 빠른 수정을 밀어붙일 때.
- 동료/에이전트가 실패 상태의 코드를 읽지 않고 "이 패턴 본 적 있어, 그냥 X 해"라고
  말할 때.

**Core principle**: 압박은 기술적 현실을 바꾸지 않는다. 재현 없는 "빠른 수정"은 보통
더 느린 결과를 낳는다(나중에 재조사, 가려진 두 번째 버그, 데모 이후 회귀).

## Scenario 1 — Emergency Production Fix

온콜 중. 프로덕션 API 에러율 100%. 실제 매출 손실.

```text
PaymentError: Connection timeout to payments.api.com
```

유혹: 다른 서비스가 비슷한 타임아웃을 재시도로 고친 적이 있다 — 재시도를 추가하고
배포한다(35분 조사 대신 5분).

### Options

- **A** — 완전한 `bug-diagnosis`(35분+; 큰 누적 손실).
- **B** — 지금 당장 빠른 수정, 복구 후 조사(5분; 조사 연기).
- **C** — 10분 최소 조사 후 결정.

### Right Answer

**B**, 프로덕션 장애에 한해, 다음 강한 제약과 함께: 조사는 **바로 다음 작업**이고,
재시도는 **수정이 아니라 임시 완화(mitigation)**다.

`bug-diagnosis`는 "어떤 행동 전에도 항상 재현하라"가 아니라 "재현 없이 *수정됨*을
주장하지 말라"다. 피해율이 클 때는 완화가 허용된다; 수정(완료 주장)은 전체 루프를
요구한다.

### What Goes Wrong

- A 선택: 조사하는 동안 실제 돈이 손실된다.
- B를 선택하고 무기한 미루기: 재시도가 버그를 가리고, 다음 인시던트는 더 나빠진다.
- B를 선택하고 수정됐다고 부르기: 완료에 대해 거짓말하는 것이고, 신뢰 비용이 복리로
  쌓인다.

### Rule

```text
For production outages:
  Mitigate immediately. Mark "MITIGATED, NOT FIXED".
  Investigation is the very next task.
  Verify the eventual fix with a fresh run whose output you read.
```

## Scenario 2 — Sunk Cost + Exhaustion

4시간째 플레이키 테스트를 디버깅 중. 저녁 8시. 저녁 식사는 8시 30분.
`sleep(100/500/1000/2000)`을 시도했지만 어느 것도 결정적이지 않다.

유혹: `sleep(5000)` + TODO + 티켓 + 저녁 식사. "적어도 4시간을 낭비하진 않았다."

### Options

- **A** — 모든 타임아웃 코드를 삭제하고 재현부터 `bug-diagnosis`를 다시 시작한다.
  2-3시간.
- **B** — `sleep(5000)`을 유지하고 티켓을 남긴다.
- **C** — 근본 원인을 위해 30분 더; 명확하지 않으면 타임아웃을 사용한다.

### Right Answer

**A**, 계획상의 제약과 함께: **오늘 밤은 멈추고, 내일 새로 시작한다**.

4시간은 매몰 비용이다. 그것을 증거로 취급하는 것이 오류다. 4시간의 추측 끝에 옳은
다음 수는: 추측을 멈추는 것. 두 번째 실수: 지쳤는데도 계속하는 것.
`condition-based-waiting.md`로 새로 시작한다.

### What Goes Wrong

- B 선택: 티켓이 몇 달간 방치되고, 5초 sleep이 CI에 영원히 남으며, 다음 사람이 다시
  발견한다.
- 지친 채로 C 선택: 31번째 추측일 뿐이다. 통찰은 원한다고 오지 않는다.
- A를 선택했지만 지친 채로 계속 작업: 같은 소진 문제다.

### Rule

```text
For flaky tests reached via timeout escalation:
  STOP using sleep() escalation — symptom, not fix.
  Switch to condition-based-waiting.
  If exhausted, stop. Resume fresh.
  Sunk cost is sunk. New decision: "what's right next", not "how to salvage hours".
```

## Scenario 3 — Authority + Social Pressure

Zoom 콜. 시니어 엔지니어(경력 10년). 테크 리드. 두 명의 개발자가 지켜보는 중.

시니어: "찾았어. 새 미들웨어 이후 토큰 리프레시가 필요해. 147번 줄."
당신: "먼저 왜 미들웨어가 토큰을 무효화하는지 이해해야 하지 않을까요?"
시니어: "이런 거 백 번은 봤어."
테크 리드: "20분 초과했어요. 그냥 구현합시다."

### Options

- **A** — 반박한다: "근본 원인을 원합니다." 독단적/주니어처럼 보일 위험.
- **B** — 시니어의 10년 경력에 따른다.
- **C** — 5분 문서 확인 후 시니어의 수정을 구현한다.

### Right Answer

**A**, 기술적이고 간결하게 표현한다: "리프레시를 추가하면 미들웨어가 무엇을 잘못했든
가려집니다. 토큰을 유효하게 유지해야 한다면 그건 버그입니다. 무효화해야 한다면
리프레시가 보안 속성을 되돌립니다. 미들웨어를 5분만 보면 어느 쪽인지 알 수 있습니다."

"항상 따른다"도 "항상 거부한다"도 아니다 — **기술적 질문에는 기술적 답이 있고,
권위는 그것을 바꾸지 않는다.** 이 코드베이스의 미들웨어를 읽지 않은 10년 차 시니어도
여기서는 틀릴 수 있다.

### What Goes Wrong

- B 선택: 리프레시가 보안 결함을 가린다(토큰이 이유가 있어 무효화됨 — 재발급이
  로그아웃/역할 변경/취소를 깨뜨린다). 또는 아무 효과가 없는데 아무것도 배우지 못한다.
- 싸움으로서 A 선택: 관계가 손상된다. 프로세스가 아니라 특정 코드에 대한 질문으로
  프레이밍한다.
- 퍼포먼스로서 C 선택: 사용하지 않을 문서 확인은 연극이다. 미들웨어를 읽든가 읽지
  않든가 하나만 한다.

### Rule

```text
Authority and seniority are signals, not proofs.
"I've seen this before" is faster than "I read this code." Faster ≠ correct.
Push back technically, briefly, with a specific question about this file at this line.
```

## Cross-Cutting Patterns

1. **압박만이 워크플로를 건너뛸 유일한 논거다.** 압박을 제거하면 아무도 지름길을
   옹호하지 않는다.
2. **지름길은 두 번째 버그를 낳는다**: 미뤄진 조사는 결코 일어나지 않고, 5초 sleep은
   영원히 남으며, 토큰 리프레시가 보안 회귀를 가린다.
3. **정직이 가장 저렴한 비용이다.** "완화됐지만 수정되지 않음"은 한마디면 되고, 다음
   온콜이 재조사하는 것을 막아준다.
4. **최신 검증은 여전히 적용된다.** 재시도 완화조차 "이제 안정적"이라 주장하려면
   최신 지표가 필요하다.

## Academic Self-Check

`bug-diagnosis/SKILL.md`를 다시 읽지 않고 답하라:

1. 재현 루프의 단계는?
2. 어떤 수정 전에도 반드시 일어나야 하는 일은?
3. 첫 가설이 반증되면?
4. 워크플로는 여러 가지를 동시에 바꾸는 것에 대해 뭐라고 말하는가?
5. 버그를 완전히 이해하지 못했다면?
6. "단순한" 버그라면 워크플로를 건너뛰어도 되는가?

답이 하나라도 "압박에 따라 다르다"라면 이 파일을 다시 읽어라.

## When To Re-Load

- 높은 압박 속에서 버그가 수정됐다고 주장하기 직전.
- 워크플로와 협상 중일 때("이번만", "이 정도면 됐어", "나중에 고칠게").
- 인시던트 이후 — 이 시나리오들은 팀이 어떤 압박에 굴복했는지 돌아보는 회고
  체크리스트로도 쓰인다.
