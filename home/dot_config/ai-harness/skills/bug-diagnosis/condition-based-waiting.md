# Condition-Based Waiting

Flaky tests often guess at timing with arbitrary delays — passes on fast machines, fails
under load or in CI.

**Core principle**: wait for the actual condition you care about, not a guess about how long
it takes.

## When To Use

- Tests use arbitrary delays (`setTimeout`, `sleep`, `time.sleep()`).
- Tests are flaky — pass sometimes, fail under load or parallel runs.
- Tests time out unpredictably.
- Code waits for async operations to complete.

## When *Not* To Use

- Testing actual timing behavior (debounce intervals, throttle windows, scheduled ticks). The
  timeout is the unit under test — document *why* the duration is what it is.

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
| Wait for an event | `waitFor(() => events.find(e => e.type === 'DONE'))` |
| Wait for a state | `waitFor(() => machine.state === 'ready')` |
| Wait for a count | `waitFor(() => items.length >= 5)` |
| Wait for a file | `waitFor(() => fs.existsSync(path))` |
| Complex condition | `waitFor(() => obj.ready && obj.value > 10)` |

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

Build domain-specific helpers on top (`waitForEvent`, `waitForEventCount`,
`waitForEventMatch`) so tests express *what* they wait for, not *how long*.

For Python/Go/Rust use idiomatic equivalents (Python: `asyncio.wait_for` + polling helper,
Go: `for { select }` with `time.After`, Rust: `tokio::time::timeout` around polling loop).

## When An Arbitrary Timeout Is Justified

The unit under test *is* a timer.

```typescript
await waitForEvent(manager, 'TOOL_STARTED');  // condition first
await new Promise(r => setTimeout(r, 200));    // documented timed behavior
// 200ms = 2 ticks at 100ms — duration is part of the spec.
```

Requirements:

1. Wait for the triggering condition first.
2. Duration based on a documented interval, not a guess.
3. Comment explains *why* the duration is what it is.

## Common Mistakes

- **Polling too fast** (`setTimeout(check, 1)`). → Poll every 10 ms.
- **No timeout**. Loop runs forever when condition never fires. → Always include timeout +
  clear error message.
- **Caching stale state outside the loop**. → Call the getter inside the loop.
- **Polling for derived state** when underlying event is observable. → Wait for the event.
- **Timeout too short**. Condition fires after 5 s, timeout is 1 s. → Generous vs expected
  latency, short enough to fail fast.

## Real-World Impact

Representative session converting 15 flaky tests across 3 files:

- Pass rate: 60% → 100%.
- Execution time: 40% faster (no fixed long sleeps).
- Race conditions: 0.

## Hand-Off

After converting to condition-based waiting:

1. Apply `verification-before-completion` — run the test (under load if project has stress
   mode) before claiming fixed.
2. If a Layer 3 environment guard (`defense-in-depth.md`) is relevant — e.g., waiter masks a
   real race in production — add the guard *in production*, not only in tests.
3. Return to `bug-diagnosis` SKILL step 8-10 (fix, verify, clean up).
