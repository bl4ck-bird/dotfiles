---
name: security-review
description: Use when reviewing auth, permissions, secrets, crypto, deletion, destructive operations, sensitive data, external integrations, or data-loss risk. auth, secrets, crypto, deletion 등 보안에 민감한 변경을 검토할 때 사용한다.
---

# Security Review

**Intent**: 보안에 민감한 변경은 명시된 의도가 아니라 코드, 설정, 검증에서 나온
증거를 가지고 출시된다. **Boundary**: 필수 수정은 제공된 diff 안에 머문다; 광범위한
보안 재작성, 새 의존성, 무관한 하드닝을 필수 수정으로 요구하지 않는다. **Verify**:
아래 findings/result 블록, 규모가 있는 리뷰는 저장한다.

보안에 민감한 표면이 건드려졌을 때 보통 `implementation-review`의 follow-on으로
실행되며, slice가 처음부터 보안 비중이 크면 직접 호출한다.

## Triggers

다음을 건드리는 작업: 인증 / 인가 / 세션 / 토큰 / 자격 증명 · secrets, `.env`,
private key, 로깅, 텔레메트리 · crypto, 해싱, 서명, 키 관리 · 삭제, 파괴적 명령,
백업/복원, import/export, 보존(retention) · 외부 통합, webhook, sync, concurrency,
민감 데이터 노출 · 신뢰할 수 없는 입력(검증, injection, path traversal, command
construction, deserialization, SSRF, redirect, upload) · auth/payment/crypto/network/
native 경로의 새 의존성 또는 교체된 의존성(audit 결과, 서플라이체인 평판, post-install
스크립트).

## Checks

- 신뢰 경계와 검증 지점이 명시적인지; 인가가 올바른 경계에서 일어나는지.
- 민감 데이터가 출력, 로그, 커밋, 에러에 노출되지 않는지.
- 파괴적 작업이 명시적인 사용자 승인 또는 제품 차원의 승인을 요구하는지.
- 암호화와 secret 처리가 프로젝트 문서나 1차 출처(primary-source) 가이드를 따르는지.
- denial, 잘못된 입력, 실패 동작이 실무적으로 가능한 범위에서 테스트되었거나(또는
  수동으로 확인되었는지).
- durable security 동작이 바뀌면 `.ai-harness/SECURITY_MODEL.md`가 갱신되었는지.

"입력이 검증됨", "secret이 redacted됨" 같은 주장은 구현자의 설명이 아니라 실제
코드 경로를 읽어 검증한다.

## Severity And Result

(SSOT: `using-bb-harness/severity-definitions.md`)

- **Critical**: 악용 가능한 취약점, secret 유출, 인증 우회, 데이터 손실 위험, 승인
  안 된 파괴적 작업, crypto/key 결함.
- **Important**: 취약한 검증, 올바른 경계에서 인가가 빠짐, 로그/에러/텔레메트리 속
  민감 데이터, 보안 관련 경로에 대한 denial/failure 테스트 누락.
- **Minor**: 심층 방어(defense-in-depth) 또는 하드닝 제안, 네이밍 명확성.

Result: **Ready to merge: Yes / With fixes / No**. With fixes → 구현자가
`receiving-review`를 거쳐 Critical/Important를 반영하고 재실행; 두 사이클 후 중단,
에스컬레이션(`using-bb-harness` Review Iteration Pattern).

## Output

발견 사항을 먼저, severity 순으로, 각각 file:line, impact, evidence, mitigation와
함께 제시한 뒤 result와 잔여 위험을 적는다. 규모가 있는 기록은
`.ai-harness/reviews/YYYY-MM-DD-<topic>-security-review.md`에 저장한다.
