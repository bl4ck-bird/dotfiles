---
name: implementation-review
description: Use when reviewing an implemented slice against its acceptance artifact and quality bar in a single pass — spec compliance (binary ✅/❌) plus code quality, architecture (DDD/SOLID), file size, testing, and durable docs drift. Returns Spec compliant ✅/❌ and Ready to merge? Yes / With fixes / No. 구현된 slice를 수락 아티팩트와 품질 기준에 대해 한 번의 패스로 검토 — 스펙 준수 여부와 코드 품질을 함께 확인한다.
---

# Implementation Review

**Intent**: 리뷰어 한 명, 패스 한 번, 체크리스트 두 개 — slice가 요청받은 것과 정확히
일치하는지 *그리고* 잘 만들어졌는지를 함께 확인한다. **Boundary**: 코드를 직접 읽는다,
구현자의 보고는 절대 신뢰하지 않는다; 스펙 준수를 통과하지 못한 diff는 품질을 채점하지
않는다; 발견 사항은 diff와 수락 아티팩트 범위 안에 머문다. **Verify**: 아래 dual-contract
Output 블록.

**Granularity: task가 아니라 slice.** vertical-slice 경계에서 dispatch한다; task 단위
검증(테스트 + 컨트롤러의 diff 검사)은 컨트롤러 몫으로 남는다.

DDD operational checks(동반 파일 `ddd-operational-checks.md`), SOLID checks, File And
Complexity Thresholds, Coverage Matrix, durable docs drift에 대한 harness 전체 SSOT. 다른
스킬은 부분집합을 참조하며, 정의는 이 파일이 소유한다.

## Inputs

수락 아티팩트 · 구현자 보고서 **와** 실제 diff(둘이 다르면 diff가 우선) ·
`AGENTS.md`, `.ai-harness/CONTEXT.md`, `.ai-harness/CURRENT.md`, plan · 존재하고 관련
있으면 model docs · 테스트/검증 출력. diff 또는 artifact 경로가 없으면 물어본다; 채팅
기록에서 추론하지 않는다.

## Checklist 1 — Spec Compliance (binary)

세 가지 분류, 존재 여부만 판단 — 심각도 채점 없음:

| Class | Definition |
| --- | --- |
| **Missing** | Acceptance criterion with no (or partial) implementing code. |
| **Extra** | Code not required by the artifact — features, flags, abstractions, refactors, renames. |
| **Misunderstood** | Right feature, wrong semantics / domain term / contract — letter over intent. |

도메인 용어 드리프트(`.ai-harness/CONTEXT.md` 밖의 동의어)는 **Misunderstood**로 분류한다.
판정: **✅ Spec compliant / ❌ Issues found**. ❌ → 패스를 중단하고, 구현자가
`receiving-review`를 거쳐 수정한 뒤 재실행한다. 예외: spec/plan 자체가 틀렸거나 모호해서
생긴 ❌는 수정 사이클을 소모하지 말고 사용자 / `write-spec`으로 에스컬레이션한다.

## Checklist 2 — Quality (five areas, only when Checklist 1 is ✅)

각 발견 사항은 diff 내 file:line을 인용한다.

**1. Code quality** — 관심사 분리; 에러 처리(예외를 삼키거나, 광범위한 catch, 실패를
가리는 fallback 없음); 타입 안전성(경계를 넘는 `any`/`unknown` 금지, stringly-typed
상태 금지); 과도한 조기 추상화 없이 DRY; 엣지 케이스가 처리되었거나 명시적으로
수용됨; 주석 위생(왜(why)-주석만 허용; 튜토리얼성/내용을 그대로 반복하는/일시적인
주석과 주석 속 harness ID는 플래그 처리).

**2. Architecture** —

- *DDD operational checks*: `.ai-harness/CONTEXT.md` 또는 `.ai-harness/DOMAIN_MODEL.md`가
  존재하고 **동시에** diff가 도메인 코드를 건드릴 때만 `ddd-operational-checks.md`를
  로드한다; 그 외에는 건너뛴다 — CRUD/glue/UI는 DDD 리뷰가 필요 없다.
- *SOLID*: SRP(변경 이유는 하나), OCP(실제 변형이 있는 지점에만 확장 포인트), LSP(계약
  보존), ISP(뚱뚱한 인터페이스 금지), DIP(도메인은 프레임워크가 아니라 포트에 의존).
- *File And Complexity Thresholds*: **300줄**(소스 파일) → 책임 검토; **600줄** →
  생성/vendored/fixture/migration/데이터 테이블/문서화된 예외가 아니면 findings 처리;
  **50~80줄 함수** → 추출 고려; 한 개념에 대한 **3회 이상 반복되는 조건문** → 도메인
  개념이나 정책 객체 고려. 이 임계값을 인라인으로 참조하는 콜사이트 — 변경 시 감사할
  것: `second-review/SKILL.md`, `write-plan/SKILL.md`,
  `write-plan/plan-document-reviewer-prompt.md`,
  `subagent-driven-development/implementation-reviewer-prompt.md`.
- 경계의 명확성, 결합 방향, 도메인으로의 프레임워크 누수 없음, 실제 복잡도로 정당화된
  추상화, UI/네트워크/DB/파일시스템 없이도 테스트 가능한 핵심 동작.

**3. Testing** — 테스트가 private helper나 파일 배치가 아니라 공개 동작이나 도메인
불변식을 증명하는지; mock이 검증 대상 동작을 제거하지 않는지; 회귀 테스트가 수정 전에는
실패하는지; 검증 명령과 기대 신호가 기록되어 있는지.

**Coverage Matrix (required)** — 모든 수락 기준을 그 증명과 매핑한다:

| Acceptance criterion | Proof (test file:line, command output, or `ACCEPTED` reason) |
| --- | --- |

빈틈은 `MISSING`; `ACCEPTED`는 수락 소스가 해당 케이스를 명시적으로 제외한 경우에만
사용; 커버되지 않은 엣지/에러 케이스는 별도로 나열한다.

**4. Durable docs drift** — README는 사용자용 문서로 유지; `.ai-harness/CONTEXT.md`가
정식 용어를 소유; `.ai-harness/CURRENT.md`가 현재 상태를 반영; model docs는 존재하고
해당 관심사가 바뀐 경우에만 갱신(없는 것이 정상 상태다 — 이 문서들은 각자를 생성하는
스킬이 만든다); `.ai-harness/adr/` — 이 slice에 ADR 없이 되돌리기 어려운 결정이 있으면
플래그.

**5. Production readiness** — 스키마가 바뀌었다면 마이그레이션 전략; 공개 API의 하위
호환성; 새 동작에 대한 문서; 인접한 수정 코드에 뻔한 버그가 없는지.

## Scope And Severity

Scope Guard(SSOT: `using-bb-harness/review-rules.md`): 건드리지 않은 코드에 대한
발견은 그 변경이 해당 코드를 안전하지 않게 만드는 경우가 아니면 Minor(그 경우 명시적
증거를 인용); 새로운 제품 동작, 광범위한 재작성, 새 의존성, 무관한 정리 작업을 필수
수정으로 요구하지 않음; YAGNI는 리뷰어에게도 적용; "더 잘 구성될 수 있다"는 finding이
아님.

Severity(SSOT: `using-bb-harness/severity-definitions.md`): **Critical** — 버그, 보안
결함, 데이터 손실 위험, 수락된 동작의 파손, 조용한 실패, 주장된 동작에 대한 누락된
테스트. **Important** — 건드린 경로의 아키텍처 문제, 문서화된 예외 없는 임계값 위반,
누락된 에러 처리, 취약한 테스트 설계, 이미 거짓이 된 durable doc 주장. **Minor** —
스타일, 네이밍, 최적화, 주석 위생, 범위 밖 개선.

## Result

두 부분으로 된 계약 — 압축 금지:

- **Spec compliant: ✅ / ❌** (Checklist 1)
- **Ready to merge: Yes / With fixes / No** (Checklist 2, ✅일 때만) — Yes: 남아 있는
  Critical/Important 없음 · With fixes: 구현자가 고칠 수 있는 Critical/Important, 리뷰어가
  재실행 · No: 코드가 아니라 아티팩트 자체의 수정이 필요한 근본적 문제.

Minor 발견은 절대 blocking이 아니다. ❌ 또는 With fixes → `receiving-review`를 거쳐
수정, 재실행; 같은 slice 안에서 **두 사이클 뒤에는 중단**하고, cycle-2에서만 나온 발견은
이유와 함께 `introduced-in-cycle-2`로 라벨링한다(전체 규칙:
`using-bb-harness/review-rules.md`).

## Follow-On

자동 follow-on은 최대 **하나**(Review Chain Depth Cap): diff 안에 보안에 민감한 표면이
있으면 → `security-review`; High-Risk Surface(정식 목록은 `second-review`) 또는
double-check 요청 → `second-review`(Required 기준을 충족하면 cap에서 예외). 두 번째
follow-on은 사용자 확인이 필요한 권고 사항일 뿐 — 절대 자동으로 연쇄시키지 않는다.

## Output

```text
## Spec Compliance
- Result: ✅ Spec compliant / ❌ Issues found
- Acceptance criteria covered: <list>                          (✅)
- Missing / Extra / Misunderstood: <file:line — why>           (❌; 여기서 패스 종료)
- Files inspected: <list>
- Verification evidence read: <commands run / outputs read>

## Strengths
- <specific observation with file:line>

## Findings
### Critical (Must Fix)
- <file:line> — <what> — <why it matters> — <how to fix>
### Important (Should Fix)
### Minor (Nice To Have)

## Coverage Matrix
| Acceptance criterion | Proof |

## Follow-On
- Required: <security-review / second-review / none>
- Recommended (needs user confirmation): <none / one named review>

## Result
- Spec compliant: ✅ / ❌
- Ready to merge: Yes / With fixes / No
- Reasoning: <one or two sentences>
```

규모가 있는 리뷰 → `.ai-harness/reviews/YYYY-MM-DD-<topic>-implementation-review.md`에
저장하며, `retro-capture`를 위한 채널별 리뷰 유용성(심각도 분포, 고유 발견 수, 유발된
수정)도 함께 담는다.

Subagent dispatch template: `subagent-driven-development/implementation-reviewer-prompt.md`.
