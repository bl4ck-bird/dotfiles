---
name: bounded-loop
description: Use when the user wants an agent to keep working toward a defined goal across multiple iterations with review checkpoints. 사용자가 review checkpoint를 두고 여러 iteration에 걸쳐 정의된 goal을 향해 agent가 계속 작업하길 원할 때 사용한다.
---

# Bounded Loop

**Intent**: 명시적 goal을 향한 자율 반복이며, 첫 iteration 이전에 예산과 stop condition이 합의됐기
때문에 안전하다. **Boundary**: 루프는 암묵적 예산으로 절대 실행되지 않는다; 루프 승인은
destructive operation, setup/dependency/history 액션, product/architecture 결정을 절대 커버하지
않는다. **Verify**: 모든 iteration은 gate 명령을 실행하고 그 최신 출력을 읽는 것으로 끝난다.

## Preconditions (all explicit before starting)

- **Goal** — 구체적인 결과물. **Scope** — 루프가 건드릴 수 있는 파일/모듈/문서/명령.
- **Iteration budget** — 최대 루프 횟수(필수; time budget은 참고용일 뿐).
- **Verification gate** — 진행을 증명하는 명령 또는 수동 체크.
- **Allowed autonomous actions** — 정확한 파일 영역, 명령, review/fix 범위, worker-agent 사용.
  **Forbidden actions** — setup, dependency, hooks, git history, deletion, deployment.
- **Stop conditions**과 **handoff target**(pause/clear 시 상태를 기록하는 위치).

빠진 것이 있으면 → 물어보거나, 승인용 짧은 제안을 작성한다.

## Iteration Shape

1. iteration 번호, 계획된 액션, 그것이 어떻게 scope 안에 머무는지 명시한다.
2. 가능한 가장 작은 유용한 변경이나 조사를 수행한다.
3. verification gate를 실행하고 최신 출력을 읽는다(실행할 수 없다면 이유를 설명).
4. 변경이 위험하거나, 범위가 넓거나, 반복적이면 focused review를 수행한다.
5. 결정: continue / stop successful / stop blocked / ask. 다음 iteration이 명확한 기대 개선을
   가질 때만 continue한다.
6. plan, review record, 또는 handoff note를 근거와 함께 갱신한다.

## Stop And Ask When

- 다음 단계가 승인된 파일이나 goal 범위를 벗어난다.
- 검증이 **같은 이유로 두 번** 실패한다.
- 결정이 product, domain, architecture, data, security, dependency 방향을 바꾸게 된다.
- 루프가 install, init, hook, history rewrite, delete, deploy를 하거나 allowed action에 없는
  command/file/service/worker 범위를 사용하려 한다.
- goal을 달성하지 못한 채 iteration budget에 도달했다.

Tool permission prompt와 destructive operation은 루프 승인이 절대 커버하지 않는다.

## Fit

적합: bounded file set 안에서 승인된 리뷰의 모든 발견사항을 고치는 것 · 체크 통과까지 승인된
slice를 진행하는 것 · `docs-sync`가 정렬을 확인할 때까지 문서를 반복하는 것 · 실패하는 테스트에
대한 bounded hypothesis testing. 부적합: discovery/brainstorming · 리뷰된 plan 없는 광범위한
refactor · "다 좋아질 때까지 실행" · irreversible action에 대한 사용자 승인을 대체하는 것.

## Output

최종 상태(complete / blocked / stopped for approval) · 사용한 iteration 수 · 변경되거나 검사된
파일 · 검증 및 리뷰 근거 · 남은 위험 · 다음 안전 액션 · 갱신된 handoff target(경로).
