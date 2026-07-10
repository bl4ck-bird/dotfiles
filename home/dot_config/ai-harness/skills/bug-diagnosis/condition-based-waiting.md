# Condition-Based Waiting

플레이키 테스트는 흔히 임의의 지연으로 타이밍을 추측한다 — 빠른 머신에서는 통과하지만
부하가 걸리거나 CI에서는 실패한다.

**Core principle**: 걸리는 시간을 추측하지 말고, 실제로 신경 쓰는 조건을 기다린다.

## When To Use

- 테스트가 임의의 지연(`setTimeout`, `sleep`, `time.sleep()`)을 사용한다.
- 테스트가 플레이키하다 — 부하나 병렬 실행에서 가끔 실패한다.
- 테스트가 예측 불가능하게 타임아웃된다.
- 코드가 비동기 연산 완료를 기다린다.

## When *Not* To Use

- 실제 타이밍 동작(디바운스 간격, 스로틀 윈도, 스케줄된 틱)을 테스트할 때. 타임아웃
  자체가 테스트 대상이다 — 지속 시간이 왜 그 값인지 문서화한다.

## Core Pattern

```typescript
// ❌ Before: guessing at timing
await new Promise(r => setTimeout(r, 50));
const result = getResult();
expect(result).toBeDefined();

// ✅ After: waiting for the condition
await waitFor(() => getResult() !== undefined);
const result = getResult();
expect(result).toBeDefined();
```

## Quick Patterns

| Scenario | Pattern |
| --- | --- |
| 이벤트 대기 | `waitFor(() => events.find(e => e.type === 'DONE'))` |
| 상태 대기 | `waitFor(() => machine.state === 'ready')` |
| 개수 대기 | `waitFor(() => items.length >= 5)` |
| 파일 대기 | `waitFor(() => fs.existsSync(path))` |
| 복합 조건 | `waitFor(() => obj.ready && obj.value > 10)` |

## Reference Implementation

```typescript
async function waitFor<T>(
  condition: () => T | undefined | null | false,
  description: string,
  timeoutMs = 5000,
): Promise<T> {
  const startTime = Date.now();
  while (true) {
    const result = condition();
    if (result) return result;
    if (Date.now() - startTime > timeoutMs) {
      throw new Error(`Timeout waiting for ${description} after ${timeoutMs}ms`);
    }
    await new Promise(r => setTimeout(r, 10)); // poll every 10ms
  }
}
```

그 위에 도메인 특화 헬퍼(`waitForEvent`, `waitForEventCount`, `waitForEventMatch`)를
만들어, 테스트가 *얼마나 오래*가 아니라 *무엇을* 기다리는지 표현하게 한다.

Python/Go/Rust에서는 관용적 대응물을 사용한다(Python: `asyncio.wait_for` + 폴링 헬퍼,
Go: `time.After`와 함께 `for { select }`, Rust: 폴링 루프를 감싸는
`tokio::time::timeout`).

## When An Arbitrary Timeout Is Justified

테스트 대상 자체가 타이머일 때.

```typescript
await waitForEvent(manager, 'TOOL_STARTED');  // condition first
await new Promise(r => setTimeout(r, 200));    // documented timed behavior
// 200ms = 2 ticks at 100ms — duration is part of the spec.
```

요건:

1. 트리거 조건을 먼저 기다린다.
2. 지속 시간은 추측이 아니라 문서화된 간격에 근거한다.
3. 지속 시간이 왜 그 값인지 주석으로 설명한다.

## Common Mistakes

- **너무 빠른 폴링**(`setTimeout(check, 1)`). → 10ms 간격으로 폴링한다.
- **타임아웃 없음**. 조건이 절대 발생하지 않으면 루프가 영원히 돈다. → 항상 타임아웃과
  명확한 에러 메시지를 포함한다.
- **루프 밖에서 오래된 상태를 캐싱**. → getter를 루프 안에서 호출한다.
- 기저 이벤트를 관찰할 수 있는데 **파생 상태를 폴링**. → 이벤트를 기다린다.
- **타임아웃이 너무 짧음**. 조건이 5초 후 발생하는데 타임아웃은 1초. → 예상 지연 대비
  여유 있게, 하지만 빠르게 실패할 만큼 짧게.

## Real-World Impact

3개 파일에 걸친 플레이키 테스트 15개를 변환한 대표 세션:

- 통과율: 60% → 100%.
- 실행 시간: 40% 단축(고정된 긴 sleep 없음).
- 경쟁 상태: 0건.

## Hand-Off

조건 기반 대기로 전환한 후:

1. 고쳤다고 주장하기 전에 테스트를 실행하고(프로젝트에 스트레스 모드가 있다면 부하
   상태에서) 최신 출력을 읽는다.
2. Layer 3 환경 가드(`defense-in-depth.md`)가 관련 있다면 — 예를 들어 waiter가
   프로덕션의 실제 경쟁 상태를 가리고 있다면 — 가드를 테스트뿐 아니라 *프로덕션에도*
   추가한다.
3. `bug-diagnosis` SKILL 8-10단계로 복귀한다(수정, 검증, 정리).
