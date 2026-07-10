---
name: write-plan
description: Use when turning a reviewed acceptance artifact, PRD, issue, review finding, or vertical slice into a compact implementation plan before editing code. 검토된 수용 아티팩트나 이슈를 코드 편집 전 컴팩트한 구현 플랜으로 전환할 때 사용한다.
---

# Write Plan

**Intent**: 미래의 에이전트나 사람이 추측 없이 실행할 수 있는 컴팩트한 플랜 — 작업을
제약하되, 수용 아티팩트를 중복 서술하거나 코드를 한 줄씩 서술하지 않는다. **Boundary**:
검토된 수용 아티팩트(또는 기록된 accepted risk) 없이는 플랜 없음; 플레이스홀더 언어 없음;
사용자가 승인한 범위를 넘어서는 commit/push/PR 권한 부여 없음. **Verify**: Plan Self-Review
통과; 모든 수용 요구사항이 태스크나 명시적 비목표에 매핑됨; 플랜이 확정하는 되돌리기 어려운
결정에는 ADR 작성.

`.ai-harness/plans/YYYY-MM-DD-<feature-or-slice>.md`(또는 프로젝트가 정한 위치)에 저장한다.

## Preconditions

- 읽기: `AGENTS.md`, `.ai-harness/CONTEXT.md`, `.ai-harness/CURRENT.md`,
  `.ai-harness/AGENT_WORKFLOW.md`, 수용 아티팩트, 기존 테스트와 패키지 스크립트; 해당 문서가
  존재하고 관련 영역을 다룰 때 모델 문서와 ADR.
- 수용 가중치 확인: 풀 스펙 → `write-spec` Self-Review 완료; 명확한 이슈/발견 사항/승인된
  작업 → 모든 Acceptance Brief 필드(정규 집합은 `write-spec` Light Acceptance Brief)와 함께
  수용 소스 기록; 채팅으로만 존재하는 요청 → 해당 필드 + 날짜를 담은 Approved Request Anchor
  섹션.
- High-Risk Surface(정규 목록은 `second-review`) → `second-review` 필수; 목표나 용어가
  불명확 → 먼저 `pressure-test` / `domain-modeling`.
- Accepted-risk 기록은 사용자의 명시적 승인이 있을 때만 게이트를 건너뛴다; 게이트, 이유,
  리스크, 보완 체크, 후속 조치/만료를 기록한다.

## Required Sections

```markdown
# <Feature> Implementation Plan

**Acceptance Source:** <spec/issue/review/user-approved task>
**Acceptance Self-Review:** <note in artifact / accepted-risk record / why unnecessary>
**Goal:** <one sentence>
**Slice:** <vertical slice or issue id>
**Review Needs:** <implementation-review per slice (default) / security-review when security surface touched / second-review when High-Risk Surface or boundary change>

## Approved Request Anchor

수용 소스가 채팅에만 존재할 때만 필요: date, request summary, approved scope, all
Acceptance Brief Fields.

## File Responsibility Map

| File | Create/Modify | Responsibility | Risk |
| --- | --- | --- | --- |

## Tasks

### Task 1: <small behavior>

- [ ] Step 1: Write failing behavior test
- [ ] Step 2: Run test and confirm expected failure
- [ ] Step 3: Implement minimal code
- [ ] Step 4: Run narrow verification
- [ ] Step 5: Refactor after green
- [ ] Step 6: Update docs or explain why not needed
- [ ] Step 7: Review checkpoint

## Verification

## Docs Impact

## Commit / Stack Strategy

다음 중 하나: ship-check 후 요청이 있을 때만 커밋 / ship-check 후 단일 커밋 / 완료된 수직
슬라이스마다 커밋 하나 / 브랜치 순서와 리뷰 대상을 명시한 stacked branches-PRs.

## Rollback / Recovery

## Open Risks
```

## Planning Rules

- 태스크보다 먼저 파일을 매핑한다 — 파일 경계가 플랜의 형태를 결정한다. 순수 인프라 슬라이스가
  아닌 이상 수평 단계가 아니라 수직 슬라이스로 나눈다.
- 각 태스크는 독립적으로 검증 가능해야 하며, 동작 변경에는 정확한 명령과 기대되는 RED/GREEN
  신호를 포함한 TDD 스텝이 있어야 한다 — "테스트는 나중에"는 없다.
- 수용 아티팩트를 재서술하는 대신 링크한다.
- 기본 리뷰: 슬라이스당(태스크당이 아니라) `implementation-review` 1회. 추가 리뷰만
  계획한다 — 보안 표면에는 `security-review`, `second-review`는 해당 Required / Strongly
  Consider 규칙에 따라.
- ADR 출력 계약: 되돌리기 어려운 결정(스토리지 구조, 인증 구조, 외부 의존성, 도메인 경계)을
  확정하는 플랜은 이 스킬 출력의 일부로 `.ai-harness/adr/NNNN-<title>.md`(MADR)를 작성하고
  링크한다.
- 파일 크기 계획: 임계값은 `implementation-review`(File And Complexity Thresholds)에서
  가져온다; 300/600줄에 근접하거나 도달한 대상 파일은 다음 중 하나가 필요하다 — 선행 범위형
  추출, 문서화된 예외, 또는 좁은 편집 + 후속 리팩터 이슈.

## Edit-On-Findings Mode

`implementation-review`가 플랜 수준의 결함을 발견했거나 사용자가 범위를 변경해서 플랜을
수정하는 경우 → 같은 경로의 기존 플랜을 업데이트하고, 각 발견 사항을 처리하고, 플래그되지
않은 태스크는 보존하며, Plan Self-Review를 재실행한다.

## Self-Review

제시하기 전에 점검한다. 이 체크를 인라인으로 사용하는 콜사이트:
`plan-document-reviewer-prompt.md`.

**Plan Hygiene** — 모든 수용 요구사항이 태스크나 명시적 비목표에 매핑됨; 모든 태스크가
정확한 검증 명령과 기대되는 RED/GREEN 신호를 가짐; 플레이스홀더("TBD", "appropriate error
handling") 없음; 새 식별자가 `.ai-harness/CONTEXT.md`와 일치함; 플랜이 채팅 이력 없이도
읽힘.

**Architecture Soundness** (플랜이 글루/CRUD 이상을 다룰 때) — 매핑된 파일마다 SRP(변경
이유가 하나임); DIP(도메인/애플리케이션 코드가 프레임워크/ORM/HTTP/파일시스템 타입에
의존하는 대신 포트를 명시함); 의존성 방향이 안쪽으로 흐름; 대상 파일별 파일 크기 영향이
추정됨; 아직 존재하지 않는 변형을 위한 추측성 추상화 없음; 크로스커팅 관심사(로깅, 인증,
영속성, 캐싱)가 일관된 경계에 위치함. 글루/설정/문서 전용 → `N/A — non-architectural
change`로 표기.

**Domain Alignment** — 플랜이 도메인 코드를 다룰 때 `write-spec` Self-Review Domain
Alignment를 적용한다; 플랜이 스펙에서 이미 해결된 불변식을 재논쟁하지 않고 존중하는지
확인한다.

## Independent Review (optional)

- `plan-document-reviewer-prompt.md`(이 디렉터리) — 같은 호스트에서 새로운 시각으로 보는
  서브에이전트. 다음의 경우 가치가 있다: 플랜이 모듈 경계를 넘거나 의존성 방향을 바꿀 때,
  태스크 수/파일 맵이 클 때, High-Risk Surface, 또는 파일 매핑/검증 명령에 대한 불확실성.
- `second-review` — 다른 모델을 이용한 재검증; High-Risk Surface에는 필수.

Self-Review 단독이 기본값이다. 다음 게이트: 구현된 슬라이스마다 `implementation-review`.

## Output

보고: 플랜 경로 · 슬라이스 수 · 최고 위험 파일 · 생성된 ADR(또는 없음) · 필요한 리뷰 ·
권장 다음 명령 · 다음 단계 질문 하나(예: 첫 슬라이스를 시작할지?).
