---
name: receiving-review
description: Use when receiving any review feedback (implementation, security, second, or external) — before applying fixes verify against codebase, push back if wrong, apply one item at a time, YAGNI check. 어떤 리뷰 피드백을 받든 수정 전에 코드베이스로 검증하고, 틀렸으면 반박하며, 한 번에 하나씩 적용할 때 사용한다.
---

# Receiving Review

**Intent**: 발견 사항은 실행할 명령이 아니라 평가할 제안이다 — 우호적 태도보다
기술적 정확성이 우선한다. **Boundary**: 코드베이스로 finding을 검증하기 전에는 어떤
수정도 적용하지 않는다; 일괄 수정 없음; 형식적인 동의 없음. **Verify**: 적용한 각
수정 뒤에는 반드시 focused 검증을 실행하고 그 출력을 읽는다.

리뷰어(스킬, subagent, `second-review`, 또는 사람)가 finding을 반환할 때마다, 어떤
수정이든 적용하기 전에 사용한다.

## Response Pattern

```text
1. READ:       All findings before reacting.
2. UNDERSTAND: Restate each finding's technical requirement.
3. VERIFY:     Against actual codebase, tests, acceptance artifact.
4. EVALUATE:   Correct for THIS project? Breaks anything?
5. RESPOND:    Acknowledge correct, push back on wrong with reasoning.
6. IMPLEMENT:  One at a time — Critical, then Important, then Minor —
               running relevant verification after each.
```

불명확한 finding이 하나라도 있으면 → 어떤 수정이든 적용하기 전에 멈추고 질문한다;
finding들은 서로 연관될 수 있고, 부분적인 이해는 잘못된 구현을 낳는다.

## Forbidden Responses

절대 하지 말 것: "You're absolutely right!", "Great point!", 감사 표현, 검증 전에
"implementing all of that now"라고 말하기. 대신: 변경 내용을 다시 서술하거나,
불명확하면 질문하거나, 틀렸으면 반박하거나, 그냥 적용하고 diff를 보여준다 — diff가
들었다는 증거다.

## YAGNI Check

Finding이 "제대로 구현하라" / "빠진 X를 추가하라"고 말하면 → 먼저 실제 호출부를
grep한다. 사용되지 않는다면 → 만들어 넣는 대신 제거할지 사용자에게 물어본다. YAGNI
여부는 리뷰어가 아니라 사용자가 결정한다.

## When To Push Back

기술적 근거와 함께, finding과 모순되는 파일/테스트/결정을 인용하며: 수락된 동작이나
통과 중인 테스트를 깨뜨린다 · 리뷰어가 diff에 드러나지 않는 컨텍스트를 놓치고
있다 · YAGNI · 승인된 plan이나 durable decision과 충돌한다 · 범위 밖이다
(`using-bb-harness` Review Scope Guard). 아키텍처 관련 이견 → 사용자를 참여시킨다.
반박이 틀린 것으로 밝혀지면: "Checked <X>. You were correct — implementing now." —
사과문은 필요 없다.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Performative agreement | Restate or just apply |
| Blind implementation | Verify against codebase first |
| Batch fixes without testing | One at a time, verify each |
| Assuming the reviewer is right | Check whether the fix breaks existing behavior |
| Avoiding push-back | Technical correctness over comfort |
| Applying the understood subset | Clarify all unclear items first |
| Cannot verify, proceed anyway | State the limit, ask for direction |
