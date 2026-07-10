# Review Rules

**리뷰가 어떻게 반복되고, 언제 멈추며, 무엇을 추천할 수 있는지**에 대한 하네스 전역 SSOT다.
모든 리뷰 채널(`implementation-review`, `security-review`, `second-review`)과
`receiving-review`는 이 규칙을 따른다.

심각도 분류: 이 디렉터리의 `severity-definitions.md`를 참고한다.

## Review Iteration Pattern

각 리뷰 채널(implementation, security, second)에 대해:

1. **아티팩트를 작성하거나 실행한다**(슬라이스, diff, 플랜, 스펙).
2. **리뷰를 실행한다**.
3. **결과에 따라 행동한다**:
   - **`implementation-review` Checklist 1 (spec compliance)** — 이진(binary) 결과:
     - ✅ Spec compliant → 같은 패스에서 Checklist 2 (quality)로.
     - ❌ Issues found → 구현자가 `receiving-review`를 통해 수정을 적용하고, 재실행한다.
   - **`implementation-review` Checklist 2 / `security-review` / `second-review`** — 세 가지
     상태:
     - **Yes** → 다음 채널 또는 `ship-check`로.
     - **With fixes** → 구현자가 `receiving-review`를 통해 Critical/Important를 적용하고,
       재실행한다.
     - **No** → 플랜 또는 인수 아티팩트 수정이 필요하다. 사용자에게 에스컬레이션한다;
       반복하지 않는다.
4. 같은 채널에서 수렴하지 않으면 **2 사이클 후 하드 스톱**.
   - 3번째 사이클은 자동으로 실행하지 않는다.
   - 미해결 발견 사항을 요약한다.
   - 사용자가 선택한다: 범위 축소, 현재 상태 수용, 또는 아티팩트 수정.
   - 사이클 1에는 없었는데 사이클 2에서 새로 나온 발견 사항은 이유와 함께
     `introduced-in-cycle-2`로 표시해야 한다 — 아티팩트가 실패한 게 아니라 리뷰 범위가
     확장되고 있음을 나타낸다.

Minor 발견 사항은 막지 않는다. 목록에는 넣되 추적을 요구하지는 않는다.

## Review Result Contract

모든 리뷰 스킬은 이 게이트를 사용한다. 어휘: 세 가지 답을 갖는 **`Ready to merge?`**:

- **Yes** — Critical이나 Important가 남아 있지 않다. Minor는 나열할 수 있으며, 추적은
  권장이지 필수는 아니다.
- **With fixes** — 구현자가 직접 적용할 수 있는 Critical/Important가 남아 있다.
  `receiving-review`로 수정한다; 리뷰어는 변경된 diff에 대해 재실행한다.
- **No** — 코드만이 아니라 플랜/인수 아티팩트 수정이 필요한 근본적 문제다. 사용자에게
  에스컬레이션한다; 반복하지 않는다.

`implementation-review` Checklist 1(spec compliance)은 이진 결과다: ✅ → Checklist 2로
진행, ❌ → `With fixes`. 예외: ❌의 원인이 아티팩트 수준의 오해(스펙/플랜 자체가 잘못되었거나
모호함)일 때는 `No`로 취급한다 — 수정 사이클을 소모하는 대신 즉시 사용자에게 또는
`write-spec`으로 에스컬레이션한다.

**2 사이클 후 하드 스톱** — 위 참고. 두 사이클이 지나도 수렴하지 않으면, 사용자가 경로를
선택할 때까지 결과는 사실상 `No`다.

### Pre-Implementation Verdicts

`write-spec`와 `write-plan`의 리뷰어 프롬프트는 (merge가 아니라) 아티팩트에 대해 동일한 세
가지 상태의 판정을 낸다:

- `Ready to plan: Yes / With fixes / No` (spec reviewer)
- `Ready to execute: Yes / With fixes / No` (plan reviewer)

`Ready to merge?`와 동일한 세 가지 상태 의미론이다 — Yes / With fixes / No, 2 사이클 후
하드 스톱, Critical / Important / Minor 심각도. 차이는 리뷰 대상 아티팩트(diff가 아니라 스펙
또는 플랜)와 다음 게이트(merge가 아니라 plan 또는 implementation)뿐이다. 이 파일의 모든
규칙은 이 판정들에도 동일하게 적용된다.

## Review Chain Depth Cap

포커스드 리뷰(focused review)는 자동으로 **최대 하나의** 후속 리뷰만 추천할 수 있다.

- `implementation-review`가 `security-review`를 추천(auth 관련 변경) → 허용.
- `implementation-review`가 `security-review`*와* `second-review`를 모두 추천 → 하나만
  자동으로 실행하고, 나머지는 사용자 확인이 필요한 추천으로 명시한다.

두 번째 홉(자동 `security-review`가 또 다른 리뷰를 추천하는 것)은 **사용자 확인이
필요하다**. "review of review of review" 루프로 부풀려지는 것을 막는다.

**예외**: `second-review`는 Required 기준을 충족하면(High-Risk Surface, 명시적 이중 확인,
경계/의존성 방향 변경 — `second-review`의 When 참고) 이 상한에서 면제된다.

## Review Scope Guard

발견 사항은 승인된 인수 아티팩트, 플랜, 다룬 영역(touched surface) 안에 머문다.

- 새로운 제품 동작, 광범위한 재작성, 새 의존성, 새로운 스토리지/API 형태, 무관한 정리 작업을
  필수 수정으로 제안하지 않는다.
- 승인된 범위 밖의 실제 이슈는 → 다룬 경로의 **Critical** 결함이 아닌 한 **Minor**
  (`severity-definitions.md`의 Untouched-Code Rule 참고).
- 필수 수정이 범위를 확장하려면 명시적 사용자 승인이나 플랜에 갱신된 accepted-risk 기록이
  있어야만 한다.
- "더 잘 정리될 수 있다"는 발견 사항이 아니다. "이 diff는 `file:line`의 기존 책임과 충돌하는
  변경 이유(reason-to-change)를 추가한다"는 발견 사항이다.
- YAGNI는 리뷰어에게도 적용된다. 투기적인 future-proofing은 기껏해야 Minor다.
- 현재 설계가 요청된 작업을 막지 않는 한 대규모 재작성을 추천하지 않는다. 테스트를 green
  상태로 유지하는 작은 리팩터 슬라이스를 선호한다.

## When Review Says "Plan Needs Revision"

`No` 결과는 시스템이 정상 작동하는 것이지 실패가 아니다. 수정하기 적절한 곳은 작성
스킬(`write-spec` / `write-plan`)이다. 사이클 2 수정으로 억지로 버티지 않는다.

플랜이 정말로 수정이 필요하다는 신호:

- 계획된 파일 구조로는 인수 기준을 충족할 수 없다.
- 플랜이 `.ai-harness/ARCHITECTURE.md`와 충돌하는 아키텍처 결정을 전제하고 있다.
- 구현에 `.ai-harness/CONTEXT.md` / `.ai-harness/DOMAIN_MODEL.md`에 없는 도메인 변경이
  필요하다.
- 두 슬라이스가 같은 파일에 쓰며 어느 순서로도 실행할 수 없다.

에스컬레이션하고, 플랜을 수정하고, 영향받은 슬라이스부터 다시 시작한다. 이미 완료된 이전
슬라이스는 완료 상태를 유지한다(해당 리뷰는 이미 통과했다).

## Receiving Review Feedback

리뷰어가 발견 사항을 반환하면, 어떤 수정을 적용하기 전에도 `receiving-review`를 거쳐야
한다:

- 모든 발견 사항을 먼저 읽는다; 즉각 반응하지 않는다.
- 각 발견 사항의 기술적 요구사항을 다시 서술한다.
- 코드베이스/인수 아티팩트에 대해 검증한다.
- 틀렸다면 기술적 근거로 반박한다.
- 한 번에 한 항목씩 적용하고, 매번 검증을 실행하며, 수정 완료를 주장하기 전에 그 출력을
  읽는다.

`receiving-review` SKILL.md가 전체 절차를 소유한다. 이 파일은 순서만 명시한다: 리뷰 반환 →
`receiving-review` → 수정 → 리뷰 재실행.

## Cross-Reference

이 파일을 참조하는 곳:

- `using-bb-harness` SKILL.md가 여기로 링크한다.
- 각 리뷰 스킬은 iteration rule과 scope guard를 인용한다.
- `subagent-driven-development`와 `executing-plans-inline`은 자신의 루프에서 Hard Stop
  After 2 Cycles를 사용한다.
- `claude-agents/*-reviewer.md`는 리뷰어에게 scope guard를 적용하도록 지시한다.

여기서 규칙을 변경하면, 같은 변경에서 해당 호출자들을 감사(audit)한다.
