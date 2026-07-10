---
name: subagent-driven-development
description: Use when executing an approved implementation plan — dispatches a fresh implementer subagent per task, with controller verification per task and a single implementation-review subagent per completed vertical slice. Preferred default for multi-task work when the host supports subagents. 승인된 구현 계획을 실행할 때 사용 — 태스크마다 새 구현자 서브에이전트를 디스패치하고 컨트롤러가 태스크별로 검증하며, 완료된 수직 슬라이스마다 구현 리뷰 서브에이전트를 한 번 실행한다.
---

# Subagent-Driven Development

**Intent**: 승인된 계획이 끊김 없이 실행된다 — 태스크마다 새로운 컨텍스트, 구현과 분리된
리뷰, 수직 슬라이스마다 한 번 디스패치되는 리뷰어.
**Boundary**: 컨트롤러는 워커의 컨텍스트를 절대 물려받지 않고, 검증 없이 워커 보고를 신뢰하지
않으며, 해결되지 않은 제품/도메인/아키텍처 결정을 위임하지 않고, Required User Checkpoints를
제외하면 태스크 사이에 절대 멈추지 않는다.
**Verify**: 태스크마다 — 컨트롤러가 테스트 + diff를 검사; 슬라이스마다 — 통과하는 이중 계약을
갖춘 `implementation-review` 한 번.

## Preconditions

- 기준(criteria)을 갖춘 승인 아티팩트; File Responsibility Map과 Plan Self-Review가 끝난 계획
  (`write-plan`).
- 핵심 문서 읽기: `AGENTS.md`, `.ai-harness/CONTEXT.md`, `.ai-harness/CURRENT.md`,
  `.ai-harness/AGENT_WORKFLOW.md`, 아티팩트/계획, 관련 코드; 존재하고 관련 있으면 모델 문서도.
- 호스트가 서브에이전트를 디스패치할 수 있어야 함(아니면 `executing-plans-inline`); 다음
  태스크가 한 번에 완료 및 검증 가능해야 함. 없으면 → 아티팩트부터 고친다.
- 계획을 벗어난 자율 반복 → 대신 `bounded-loop`.

## Workspace Isolation

**필수.** 루프 시작 전에 `using-git-worktrees`를 호출한다(탐지, 생성, 베이스라인 검증, 정리를
그 스킬이 담당). 보호 브랜치 규칙: `using-bb-harness` Branch Policy. 새 워크스페이스에서
베이스라인 테스트가 실패하면 → 기존 실패인지 회귀인지 구분하고, 진행 전에 확인을 구한다.
워크트리 안에서도 명시적 사용자 승인 없이는 의존성을 설치하지 않는다.

## Execution Loop

```text
계획을 한 번 읽고 → 모든 슬라이스와 그 안의 태스크를 전체 텍스트와 맥락과 함께 추출한다.

순서대로 각 태스크에 대해:

  1. implementer-prompt.md를 사용해 구현자 서브에이전트를 디스패치한다(새 컨텍스트, 채팅
     기록 없음). 전달할 것: 전체 태스크 텍스트, 배경 설명, 허용 파일, 검증 명령, 보고 형식.

  2. 구현자가 DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED로 보고한다.
     컨트롤러가 검증한다: 실제 diff를 검사하고, 주장된 검증을 직접 실행하고, 출력을 읽는다.
     워커 보고는 주장일 뿐 증거가 아니다. 태스크 단위 리뷰어 서브에이전트는 없다.

  3. 태스크를 완료로 표시한다. 멈추지 않고 계속한다.

각 수직 슬라이스 경계에서(모든 태스크가 완료 및 검증됨):

  4. implementation-reviewer-prompt.md를 사용해 슬라이스의 누적 diff에 대해
     구현 리뷰 서브에이전트를 하나만 디스패치한다.
     - Spec compliant ❌ 또는 Ready to merge: With fixes → 구현자가 receiving-review를
       통해 수정하고, 4단계를 재실행한다. 두 사이클 후 중단; 에스컬레이션.
     - Ready to merge: No → 계획/승인 아티팩트 수정이 필요하다. 에스컬레이션.
     - ✅ + Yes → 5단계로.

  5. 권장되는 후속 리뷰(security-review / second-review)가 있으면 실행한다.
     슬라이스당 자동 후속 리뷰는 최대 하나(Review Chain Depth Cap).

  6. 슬라이스를 완료로 표시한다. 계획 체크리스트와 변경된 문서를 업데이트한다. retro-capture를
     위해 잔여 리스크, 검증 증거, 채널별 리뷰 유용성(심각도 분포, 고유 발견 사항, 유발된
     수정)을 기록한다.

  7. 계획에 슬라이스별 커밋이 있으면 → 커밋 게이트 전에 ship-check.

  8. 묻지 않고 다음 슬라이스로 계속한다 — 사용자가 이미 계획을 승인했다.
```

## Required User Checkpoints

다음 경우에만 **중단**한다:

1. **BLOCKED** 상태를 컨트롤러가 해결할 수 없을 때(더 많은 컨텍스트도 실패, 더 강한 모델도
   실패, 분할도 실패).
2. 같은 슬라이스에서 **두 번의 리뷰-수정 사이클로도 수렴하지 않을 때**.
3. **계획이 다음 행동을 승인하지 않을 때**(범위, 파일, 의존성, 파괴적 작업, 리뷰 체인).
   계획이 명시한 설치·삭제를 포함해 계획이 승인한 행동은 체크포인트가 아니라 승인된 작업이다.
   호스트 권한 프롬프트는 호스트 UI일 뿐, 에이전트의 중단이 아니다.
4. diff에 **High-Risk Surface**(`second-review`의 표준 목록)가 나타났는데 계획에
   `second-review`가 예정되어 있지 않을 때.

## Prompt Templates

`{PLACEHOLDERS}`를 치환해 그대로 사용한다 — 즉흥적인 프롬프트는 없다:

- `implementer-prompt.md` — 전체 태스크 + 배경 설명 + 검증 + 보고 형식 + 자체 리뷰 + 워커 규칙.
- `implementation-reviewer-prompt.md` — 슬라이스별 리뷰어; "보고서가 아니라 코드를 읽는다";
  Checklist 1 스펙 준수(이진), Checklist 2 품질(다섯 영역 + 심각도).

## Model Selection

역할을 처리할 수 있는 가장 약한 모델을 쓴다; 무거운 메인 모델이 저비용 작업으로 새어들지
않도록 디스패치 시 `model` 오버라이드를 전달한다(사용량 한도 관리의 핵심 레버).

| Task | Model (Claude Code) |
| --- | --- |
| Read-only retrieval / search / file mapping | `haiku` — via the `explore-lite` agent (pinned) |
| Mechanical implementation (clear spec, 1-2 files) | `haiku` / `sonnet` |
| Integration / judgment (multi-file, debugging) | `sonnet` |
| Architecture, design, implementation / security review | `opus` (most capable) |

## Handling Implementer Status

- **DONE** → 컨트롤러가 검증한다(2단계). **DONE_WITH_CONCERNS** → 우려 사항을 읽고, 진행 전에
  정확성/범위 문제를 해결한다. **NEEDS_CONTEXT** → 맥락을 제공하고 재디스패치한다.
- **BLOCKED** → 컨텍스트 문제 → 컨텍스트 추가; 추론 문제 → 더 강한 모델; 너무 큼 → 분할;
  계획 자체가 잘못됨 → 에스컬레이션. 같은 모델을 그대로 재시도하지 않는다; 에스컬레이션을
  무시하지 않는다.

## Controller Anti-Patterns (never)

- 같은 태스크에 병렬 구현자 투입 — 쓰기 충돌이 확실히 발생한다; 병렬 디스패치는
  `dispatching-parallel-agents`(읽기 전용 / 분리된 작업에만).
- 전체 태스크 텍스트를 붙여넣는 대신 워커에게 계획 파일을 다시 읽게 하는 것.
- 슬라이스 리뷰를 건너뛰거나, 구현자의 자체 리뷰를 슬라이스 리뷰의 대체물로 취급하는 것.
- 미해결 Critical/Important 발견 사항을 두고 진행하거나, 실행 중에 계획을 조용히 확장하는 것
  ("하는 김에 고치기" → 멈추고 에스컬레이션).
- 대규모 재작성 / 새 의존성을 요구하는 필수 수정으로 제안하는 발견 사항을 수용하는 것(Review
  Scope Guard), 또는 두 번째 후속 리뷰를 자동으로 이어붙이는 것.
- 미해결 제품/도메인/아키텍처 결정을 위임하는 것 — 워커는 구현하고, 컨트롤러는 결정한다.

## Handoff And Output

세션을 정리하거나 중단하기 전에: `.ai-harness/reviews/`에 핸드오프를 작성한다 — 목표,
아티팩트/계획 경로, 완료된 슬라이스, 변경된 파일, 결정 사항, 검증 증거, 남은 리스크, 다음
태스크. 슬라이스마다 보고할 것: 완료된 태스크, 변경된 파일, 증거와 함께 실행한 검사, 결과와
함께 실행한 리뷰, 업데이트했거나 의도적으로 변경하지 않은 문서, 다음 슬라이스.

## When To Use `executing-plans-inline` Instead

호스트가 서브에이전트를 디스패치할 수 없을 때 · 디스패치 오버헤드가 새 컨텍스트의 이점을
넘어서는 1-3개의 작은 태스크 · 사용자가 인라인 유지를 요청했을 때 · 장시간 실행되는 대화형
상태에 메인 에이전트의 가시성이 필요한 작업. 동일한 리뷰 게이트를 인라인으로 실행하고,
자체 리뷰가 약해지면 계획 도중이라도 전환한다.
