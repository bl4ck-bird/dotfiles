---
name: pressure-test
description: Use when a product idea, feature, architecture, spec, or plan needs pressure-testing before documentation or implementation. Assumes goal/direction is set — run product-discovery first if MVP or non-goals are unclear. 문서화나 구현 전에 product idea/feature/architecture/spec/plan을 pressure-test해야 할 때 사용한다(goal/방향이 정해져 있다고 가정 — MVP나 non-goal이 불명확하면 product-discovery를 먼저 실행).
---

# Pressure Test

**Intent**: spec이나 코드 이전에 아이디어의 약점이 드러난다 — 한 번에 질문 하나씩, 각각 권장 답변
이나 tradeoff를 함께 제시해 사용자가 빈 페이지에서 설계하지 않도록 한다. **Boundary**: repo가
답할 수 있는 것(glossary, package 구조, tests, UI 패턴, 이전 결정 — 대신 조사할 것)은 묻지 않는다;
여기서 spec을 작성하지 않는다. **Verify**: 아래의 summary가 존재하고 다음 아티팩트를 명시한다.

Soft cap: 약 7개 질문 후, 해결된/미해결 사항을 요약하고 계속할지 물어본다.

## What To Challenge

Product goal(진짜 어떤 문제인지) · user(누가 충분히 신경 쓰는지) · MVP(가장 작은 유용한 동작) ·
non-goals · success signal · overloaded된 도메인 용어 · 가정을 깨는 edge case · data(저장, 파생,
migration, 삭제, 보호) · UX(첫 happy path가 아니라 반복되는 workflow) · architecture(어떤
boundary/dependency 결정이 되돌리기 어려운지) · tests(어떤 동작이 done을 증명하는지) ·
review(무엇이 `second-review`를 받을 가치가 있는지).

## Stop When

goal, MVP, non-goals, success criteria가 spec-ready 상태; 도메인 용어가 해결됐거나 open으로
표시됨; 위험한 tradeoff가 식별됨; 다음 아티팩트가 명확함(`.ai-harness/CONTEXT.md`, acceptance
artifact, ADR, 또는 plan).

## Output

요약: 해결된 결정 · 권장 방향 · 미해결 질문 · 위험 · 제안하는 다음 스킬 · 업데이트할 문서. 3개
이상의 결정을 해결한(또는 clear 직전의) 세션 → `.ai-harness/reviews/YYYY-MM-DD-<topic>-pressure-test.md`에
저장; phase 변경 시 `.ai-harness/CURRENT.md` 갱신. Spec 작성은 `write-spec`으로 이동.
