---
name: dispatching-parallel-agents
description: Use when 2+ genuinely independent investigations, bug repros, or read-only research tasks can run concurrently without shared state — for breadth, not for plan execution. Plan-task execution stays in subagent-driven-development. 진짜로 독립적인 조사·버그 재현·read-only 리서치 작업 2개 이상을 공유 상태 없이 동시에 실행할 때 사용한다(범위 확장 목적, plan 실행 목적 아님).
---

# Dispatching Parallel Agents

**Intent**: 동시적 breadth — 독립적인 조사들이 각자의 context, scope, return format을 가지고
병렬로 실행되며, controller가 통합한다. **Boundary**: plan 실행에는 절대 사용하지 않는다(그것은
`subagent-driven-development`이며, 슬라이스별 리뷰와 함께 순차 실행); 같은 파일에 대한 병렬 쓰기
절대 금지; fresh verification 없이 subagent 보고서에 따라 행동하지 않는다. **Verify**: 발견사항은
충돌 여부를 교차 검증하고, controller는 행동하기 전에 결정적 repro를 직접 재실행한다.

## When

2개 이상의 문제가 **서로 다른 근본 원인**을 가지고, **서로의 context 없이도** 이해 가능하며,
공유 상태가 없을 때 사용한다 — 예: 관련 없는 실패 테스트 파일들, 독립적으로 깨진 서브시스템들,
서로 다른 관심사에 걸친 read-only 리서치. 두 도메인이 왜 무관한지 설명할 수 없다면 → 관련 있다고
간주하고 agent 1개로 처리한다. 도메인이 agent 1개로 충분히 작을 때, 조사들이 대부분의 상태를
공유할 때, 이미 답을 대부분 알고 있을 때는 건너뛴다 — dispatch 오버헤드는 실재한다.

| Aspect | this skill | `subagent-driven-development` |
| --- | --- | --- |
| Purpose | 독립적 조사 / 리서치 | 순차적 plan-task 구현 |
| Concurrency | Parallel | Sequential |
| Write scope | Read-only or disjoint | 각 task가 쓰기; 절대 병렬 아님 |
| Review | Controller integrates | 슬라이스별 `implementation-review` |

## Dispatch

1. **독립 도메인별로 그룹화** — 도메인당 agent 1개, 각각 구체적인 scope, 명확한 goal,
   제약(기본은 read-only), 구조화된 return format을 가진다. 범용 복사-붙여넣기 프롬프트 금지.
2. **적합한 가장 저렴한 agent로 라우팅**(Claude Code; 주요 사용량 제한 레버):

| Task shape | Agent | Model |
| --- | --- | --- |
| 순수 조회 — 코드 위치 찾기, call site 매핑, grep/log 스윕, 웹 조회 | `explore-lite` | haiku (pinned) |
| 근본 원인 분석, 가설, 판단 | `general-purpose` | main을 상속; main model이 task를 초과할 때 `model: sonnet` 전달 |

   혼합 조사는 분리: 사실 → `explore-lite`, 가설 → `general-purpose`. 병렬 dispatch가 없는 host는
   같은 프롬프트를 순차 실행한다.
3. **동시 dispatch** — Claude Code: 한 응답에 여러 Task 호출. 병렬 dispatch가 없는 host: 같은
   프롬프트를 순차 실행하고 순서대로 병합.

Prompt template:

```text
Task tool (explore-lite for pure retrieval, else general-purpose):
  description: "Investigate <domain>"
  prompt: |
    Investigate <specific problem> in <specific files>.

    ## Context
    {Background, related code, what is already known}

    ## What To Find
    1. Root cause (file:line, mechanism).
    2. Reproduction (smallest failing input or test).
    3. Affected scope (other tests / call sites).
    4. Hypothesis for the fix (do NOT apply it).

    ## Constraints
    - Do NOT modify code. Investigation only.
    - Stay inside: <file list>.
    - When running any repro command, read the output in your response.

    ## Return Format
    Root cause / Repro / Affected scope / Suggested fix / Files inspected.
```

## Integrate

각 요약을 읽는다 → 충돌 해결(두 agent가 의견이 다르면 보통 한쪽이 사실을 잘못 알고 있다는 뜻이다
— 재-dispatch하지 말고 논쟁이 되는 사실을 직접 재확인) → 후속 작업은
`subagent-driven-development`나 `test-driven-development`로 라우팅 → 전체 검증을 실행하고
출력을 읽는다. agent 1개가 BLOCKED → 더 많은 context로 재-dispatch; 쓸모없는 결과 → 더 날카로운
프롬프트로 단일 교체.

## Output

dispatch된 agent와 도메인 · 도메인별 발견사항 · cross-cutting observation · 권장 다음 단계
(SDD를 통한 순차적 fix / TDD를 통한 단일 도메인 fix / 추가 조사).
