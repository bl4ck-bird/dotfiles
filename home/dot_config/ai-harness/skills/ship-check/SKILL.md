---
name: ship-check
description: Use when preparing to hand off, commit, merge, open a PR, or release after implementation and focused reviews. 구현과 집중 리뷰 이후 handoff/commit/merge/PR/release를 준비할 때 사용한다.
---

# Ship Check

**Intent**: 오래된 근거, 미검토 위험, 하네스 어휘 유출 상태로는 아무것도 배포하지 않는다.
**Boundary**: 명시적 사용자 승인, 프로젝트 로컬 요구사항, 또는 승인된 bounded goal 없이는
commit/push/PR/history 액션을 수행하지 않는다; 기존에 있던 실패를 이번 변경 탓으로 돌리지 않는다;
필수 리뷰를 수행할 수 없었던 경우 조용히 통과시키지 않는다. **Verify**: 모든 체크리스트 주장은 이
응답 안에서 읽은 명령 출력으로 뒷받침된다.

## Preconditions (standard / high-risk paths)

기준(criteria)이 있는 acceptance artifact(Self-Review 완료) · plan 또는 소규모 작업 근거 · 동작이
바뀐 경우 TDD 또는 회귀 커버리지 · 슬라이스별 `implementation-review` 통과(Spec compliant ✅,
Ready to merge: Yes — 수정 후 재실행일 수도 있음) · `security-review` 실행 또는 트리거되지 않았음을
명시 · High-Risk Surface에 대한 `second-review` 실행(정식 목록은 `second-review`) 또는 대체 조치
기록 · 리뷰어 수정사항에 `receiving-review` 적용 · `docs-sync` 검토 · 다음 단계로 commit/PR/release
액션이 승인됨.

필수 리뷰를 사용할 수 없는 경우 → 이유, 대체 리뷰, 수용한 위험, 명시적 사용자 수락을 기록한다 —
조용한 통과 금지.

## Light Pass

light 경로(하나의 bounded module, product/domain/API/data/security 결정 없음, High-Risk Surface
없음): **1, 3, 12, 14**단계만 실행하고 나머지는 "N/A — light scope"로 표시한다. 변경 범위가 light를
벗어나면 계속하기 전에 전체 체크리스트로 격상한다.

## Checklist

1. `git status` — 변경 범위가 요청 범위와 일치하는지 확인.
2. diff를 읽는다 — 관련 없는 사용자 변경사항이 되돌려지지 않았는지 확인.
3. 가장 좁은 의미 있는 tests/typecheck/lint/build를 실행한다. **"Green"이라는 판단은 이 응답 안에서
   명령을 실행하고 그 최신 출력을 읽었을 때만 성립한다** — 기억에 의존한 실행이나 구현자의 말만으로는
   안 된다. 이 체크리스트의 모든 완료 주장에 적용된다.
4. 동작/아키텍처/테스트/보안/사용자 노출 동작이 변경된 경우 `docs-sync` 실행 — 아니면 "no durable
   docs touched"로 명시.
5. `.ai-harness/CURRENT.md`가 최신 상태인지(필드는 `docs-sync` Handoffs 기준).
6. **CURRENT.md 상한**: 80줄 초과 또는 Done 항목 5개 초과 → `docs-sync` Routing Rules에 따라
   초과분을 지금 이관한다(결정 사항 → `adr/`, 작업 기록 → `reviews/`). 선택적 정리가 아니라 필수.
7. **ADR 안전망**: 이번 작업에서 확정된 되돌리기 어려운 결정(저장 구조, 인증 구조, 외부 의존성,
   도메인 경계)이 있는데 `adr/NNNN-*.md`가 없다면 → 지금 생성(MADR).
8. `.ai-harness/ROADMAP.md`(존재하는 경우)가 여전히 배포된 범위와 일치하는지 — 마일스톤/non-goal이
   바뀌었으면 갱신.
9. 슬라이스별 `implementation-review` 결과 확인; `security-review` 실행 또는 트리거되지 않았음을
   명시.
10. 필수 High-Risk 변경에 대해 `second-review` 실행, 또는 선택적으로 건너뛴 이유 명시.
11. `implementation-review`의 File And Complexity Thresholds를 넘긴 소스 파일이 미검토 상태로
    남지 않았는지.
12. 검증이 조작되지 않았는지: assertion 약화, 커버리지 축소, 체크 생략, 또는 깨진 동작에 맞춰
    테스트를 바꾸지 않았는지.
13. Commit 상태 결정: not requested / ready / committed / blocked.
14. 검증 근거와 잔여 위험을 요약한다.

이번 작업 이전부터 이미 실패하던 체크 → 있는 그대로 명시한다. 변경 후 체크가 실패 → 원인이
명확하면 targeted fix 1건, 아니면 멈추고 근거와 함께 보고한다.

## Finishing Options

테스트 통과 및 슬라이스 리뷰 완료 → 구조화된 선택지를 제시한다: **merge locally / push + PR /
keep as-is / discard**(detached HEAD는 merge 불가). Merge → merge 성공 *이후에* worktree와 branch를
정리. PR → 리뷰 반복을 위해 worktree 유지. Discard → 삭제 전 명시적 사용자 확인(타이핑된 토큰 권장).
Worktree 정리 출처: `using-git-worktrees` Cleanup — 하네스가 생성한 경로만, 먼저 main root로
`cd`, 순서는 merge → worktree 제거 → branch 삭제.

## Commit / Stack Gate

사용자가 요청했거나, 프로젝트 지침이 요구하거나, 승인된 goal에 포함된 경우에만:

1. staging 전에 `git status`와 diff를 검사; 완료된 슬라이스가 소유한 파일만 stage.
2. history가 중요한 경우 vertical slice당 커밋 1개를 선호.
3. **Vocabulary gate**: 커밋 메시지, staged diff 안의 코드 주석, PR body에 하네스 어휘가 없어야
   함 — slice/task ID(`M1`, `I1`, `S0`…), 스킬명, "BB Harness", `.ai-harness/` 경로 없음. 변경사항은
   사용자/도메인 용어로 기술; 발견되면 커밋 전에 다시 작성.
4. Stacked branches: branch당 리뷰 관심사 1개; PR 설명에 stack 순서 기록.
5. pre-commit / commit-msg hook 실행; commit hash, PR URL, 또는 블로커를 보고.

가능하면 host의 commit/PR 헬퍼를 우선 사용. commit이 승인되지 않은 경우 → "ready to commit"과
제안 메시지를 보고.

## Retro

상당한 작업 이후, 1-3줄을 기록한다(무엇이 효과적이었는지, 무엇이 뜻밖이었는지, 지킬 가치가 있는
규칙 하나). 메모리 후보나 retro 인사이트 → `retro-capture`에 전달(채널별 리뷰 유용성도 함께
기록); 아니면 해당 줄은 리뷰 기록에 남긴다.

## Do Not Ship If

필수 체크 실패 · 구현이 승인된 동작과 다름 · 미해결 Critical/Important 발견사항 · 검증이
약화되거나 생략됨 · 최종 답변이 불확실성을 숨기게 됨.

## Rollback And Incident Response

배포된 변경이 production / downstream / 승인된 동작을 깨뜨린 경우:

1. **전진 작업을 멈춘다** — 먼저 되돌리고, 그 다음 디버깅.
2. 파급 범위에 따라 되돌리기 경로를 선택: 단일 커밋 → `git revert <sha>`; 얽혀 있음 →
   `git revert -m 1 <merge-sha>`; merge 전 → PR을 닫거나 fix를 push(공유 브랜치에 force-push
   금지); 배포된 아티팩트 → 이전 아티팩트를 먼저 재배포한 뒤 소스를 되돌림.
3. rollback이 증상을 해소했는지 검증 — 트리거된 체크를 재실행하고 출력을 읽는다.
4. 재시도 전에 실패를 재현하는 회귀 테스트를 작성(`bug-diagnosis` 기준).
5. `.ai-harness/reviews/YYYY-MM-DD-<topic>-incident.md`에 사고를 기록: 무엇이 배포/파손됐는지 /
   파급 범위, 탐지 신호, revert 명령 + 검증, 근본 원인 또는 가설, 후속 조치.
   `.ai-harness/CURRENT.md` 갱신.

history rewrite 금지; 근본 원인 + 회귀 커버리지 없이 같은 변경을 재시도 금지. 프로젝트별
deploy/revert 명령은 `.ai-harness/AGENT_WORKFLOW.md`에 있다.

## Output

무엇이 바뀌었는지 · 무엇이 검증됐는지(근거) · 완료된 리뷰 · 독립 리뷰 상태 · 문서 업데이트 여부
또는 의도적으로 변경하지 않음 · commit 상태(hash 또는 제안 메시지) · 잔여 위험 · 메모리 후보.
