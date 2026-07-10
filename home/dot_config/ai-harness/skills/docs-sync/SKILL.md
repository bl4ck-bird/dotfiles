---
name: docs-sync
description: Use when project documentation may need updates after code, architecture, scope, testing, security, or user-facing behavior changes. 코드/아키텍처/범위/테스트/보안/사용자 노출 동작이 변경된 뒤 프로젝트 문서 업데이트가 필요할 때 사용한다.
---

# Docs Sync

**Intent**: durable docs가 프로젝트 실제 상태와 일치하고, 세션 산출물 모두가 routing table이
지정한 바로 그 장소에 도착한다. **Boundary**: README는 high-level이고 사용자 노출 중심을 유지;
spec과 plan은 single-work-item 문서를 유지; 오래된 주장은 caveat이 아니라 제거; `stub` 문서는
저장소 대비 검증되거나 사용자가 확인한 뒤에만 `draft`/`ready`로 승격(상태 마커 메커니즘:
`project-scaffold` Defaults). **Verify**: 보고서에 업데이트된 문서, 의도적으로 변경하지 않은 문서,
남은 문서화 위험을 나열한다.

동작/아키텍처/테스트/보안/사용자 노출 동작이 변경되면 `ship-check`에서 트리거된다; 눈에 띈 drift에
대해 직접 호출되기도 한다. `implementation-review`는 리뷰 중 문서 drift를 *발견(flag)*하고, 이
스킬은 그것을 *해결(resolve)*한다.

## Routing Rules (what goes where)

콘텐츠 유형별로 라우팅한다 — 후보 문서를 나열하지 않는다:

| Content produced this session | Destination |
| --- | --- |
| 되돌리기 어려운 결정(저장 구조, 인증 구조, 외부 의존성, 도메인 경계) | `.ai-harness/adr/NNNN-<title>.md` (MADR) — 보통 `write-spec`/`write-plan`이 생성; 누락됐다면 여기서 생성 |
| 작업 기록, 세션 서사, 리뷰 결과, handoff | `.ai-harness/reviews/YYYY-MM-DD-<topic>-*.md` |
| 도메인 용어 추가/변경/폐기 | `.ai-harness/CONTEXT.md` (정식 glossary) |
| 제품 범위, 마일스톤, non-goal 변경 | `.ai-harness/ROADMAP.md` (`product-discovery` 실행 후 존재) |
| 아키텍처 / data / security / testing 관심사 결정 | 해당 model 문서 — 이번 세션에서 결정됐다면 지금 생성 |
| 현재 phase, acceptance source, plan, blocker, verification, next action | `.ai-harness/CURRENT.md` (하한/상한은 아래) |
| 사용자 노출 동작 변경 | `README.md` / `docs/` (사람이 쓰는 어휘만) |

### CURRENT.md Hard Caps (enforced here and at `ship-check`)

파일 전체 ≤ **80줄**; Done 섹션 ≤ **최근 5개 항목**. 초과분은 위 표를 따라 이관 — 결정 형태 →
`adr/`, 작업 로그 형태 → `reviews/` handoff. 이 마이그레이션은 `ship-check`에서 필수이며 선택적
정리가 아니다.

## Handoffs

세션이 곧 clear될 예정 → `.ai-harness/reviews/`에 handoff를 추가/갱신: 현재 goal, 완료된 작업,
결정 사항, 검증 근거, 다음 안전 액션. `.ai-harness/CURRENT.md`는 실질적 변경이 있을 때만 갱신 —
같은 세션이 계속되는 경우 → phase 종료 시 한 번.

### `.ai-harness/CURRENT.md` Template (SSOT)

정식 골격 — 다른 스킬은 이것을 참조하며, 다른 곳에서 재정의하지 않는다. 아티팩트를 가리킬 뿐
복제하지 않는다; 필드당 한 줄.

```markdown
# CURRENT — <project> 진행 상태

> 세션 시작 시 가장 먼저 읽는 상태 파일. phase 경계에서만 갱신(매 스텝 X).
> 형식 SSOT: docs-sync Handoffs. 상세는 각 artifact 경로 참조.

- **Active phase**: <discovery | spec | plan | impl:S0… | review | ship>
- **Acceptance source**: <spec / ADR / issue 경로들>
- **Plan**: <.ai-harness/plans/... 경로 | 없음>
- **Completed slice/work**: <최근 완료 단위 + 한 줄>
- **Verification**: <명령 + 결과 evidence | N/A 사유>
- **Blocker**: <없음 | 내용>
- **Next action**: <다음 안전 액션 1개>

_Updated: <YYYY-MM-DD> · <session/agent>_
```

첫 non-trivial phase 경계(또는 scaffold 시점)에 생성한다. 필드는 update trigger와 1:1 대응하며,
위의 상한이 적용된다.

## Output

업데이트된 문서 · 의도적으로 변경하지 않은 문서 · 남은 문서화 위험.
