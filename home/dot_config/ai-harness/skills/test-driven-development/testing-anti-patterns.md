# Testing Anti-Patterns

Load when writing/changing tests, adding mocks, or tempted to add test-only methods to
production code.

**Core principle**: test what the code does, not what the mocks do.

Following strict TDD prevents these — each anti-pattern signals a skipped Red-Green-Refactor
step.

## The Iron Laws

```text
1. NEVER test mock behavior.
2. NEVER add test-only methods to production classes.
3. NEVER mock without understanding the dependency chain.
4. NEVER use partial mocks of structures you do not fully understand.
5. NEVER claim "done" without tests written first (per TDD Iron Law).
```

## Anti-Pattern 1: Testing Mock Behavior

```typescript
// ❌ BAD — asserting the mock exists
expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();

// ✅ GOOD — test real behavior, or do not mock it
render(<Page />);
expect(screen.getByRole('navigation')).toBeInTheDocument();
```

If the component must be mocked for isolation, test the parent's behavior with the mock
present — never assert on the mock.

### Gate

```text
BEFORE asserting on any mock element:
  Am I testing real behavior or mock existence?
  IF mock existence: STOP — delete assertion or unmock.
```

## Anti-Pattern 2: Test-Only Methods In Production

```typescript
// ❌ BAD — destroy() only used by tests, pollutes production class
class Session {
  async destroy() { await this._workspaceManager?.destroyWorkspace(this.id); }
}

// ✅ GOOD — test utilities own test cleanup
export async function cleanupSession(session: Session) {
  const workspace = session.getWorkspaceInfo();
  if (workspace) await workspaceManager.destroyWorkspace(workspace.id);
}
```

Pollutes production, dangerous if called from production, violates YAGNI, confuses object
lifecycle with entity lifecycle.

### Gate

```text
BEFORE adding any method to a production class:
  Only used by tests? → put in test utilities.
  Does this class own this resource's lifecycle? → if no, wrong class.
```

## Anti-Pattern 3: Mocking Without Understanding

```typescript
// ❌ BAD — mock removes the side effect the test depends on
vi.mock('ToolCatalog', () => ({ discoverAndCacheTools: vi.fn().mockResolvedValue(undefined) }));
await addServer(config);
await addServer(config);  // should throw — but mock removed config-write side effect

// ✅ GOOD — mock at the correct level (only the slow op)
vi.mock('MCPServerManager');
```

Over-mocking "to be safe" breaks actual behavior; test passes for the wrong reason or fails
mysteriously.

### Gate

```text
BEFORE mocking any method:
  1. What side effects does the real method have?
  2. Does this test depend on any of those?
  3. Do I fully understand what the test needs?

  IF the test depends on side effects:
    Mock at a lower level (slow/external op), OR use a test double that preserves
    necessary behavior — NOT the high-level method the test depends on.

  IF unsure: run with real implementation FIRST, observe, then minimal mocking.

  Red flags: "mock to be safe", "might be slow, better mock", mocking without
  understanding the dependency chain.
```

## Anti-Pattern 4: Incomplete Mocks

```typescript
// ❌ BAD — partial mock missing fields downstream code uses
const mockResponse = { status: 'success', data: { userId: '123' } };
// breaks when code accesses response.metadata.requestId

// ✅ GOOD — mirror real API completely
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' },
  metadata: { requestId: 'req-789', timestamp: 1234567890 },
};
```

Partial mocks hide structural assumptions, fail silently when code consumes omitted fields,
produce false confidence.

**Iron rule:** mock the *complete* data structure as it exists in reality.

### Gate

```text
BEFORE creating a mock response:
  1. Examine actual response (docs / examples / captured real call).
  2. Include ALL fields downstream might consume.
  3. Verify mock matches real schema completely.
  IF uncertain: include all documented fields.
```

## Anti-Pattern 5: Tests As Afterthought

```text
✅ Implementation complete
❌ No tests written
"Ready for testing"
```

Testing is part of implementation. Apply the TDD cycle from parent `SKILL.md`:
test → fail → implement → pass → refactor → THEN claim complete.

## When Mocks Become Too Complex

Warning signs: mock setup longer than test logic; mocking everything to pass; mocks missing
methods real components have; test breaks when mock changes.

Ask: "Do we need a mock here?" Integration with real components is often simpler.

## TDD Prevents These

1. Write test first → forces thought about what is being tested.
2. Watch it fail → confirms real behavior is exercised.
3. Minimal impl → no test-only methods creep in.
4. Real deps first → see what the test needs before mocking.

Testing mock behavior = TDD violated (mocks added without watching test fail against real
code first).

## Quick Reference

| Anti-pattern | Fix |
| --- | --- |
| Assert on mock elements | Test the real component or unmock it |
| Test-only methods in production | Move to test utilities |
| Mock without understanding | Understand deps first, mock minimally |
| Incomplete mocks | Mirror real API completely |
| Tests as afterthought | TDD — tests first |
| Over-complex mocks | Consider integration tests with real components |

## Red Flags

- Assertion checks for `*-mock` test IDs.
- Methods only called in test files.
- Mock setup is more than half the test.
- Test fails when the mock is removed.
- Cannot explain why the mock is needed.
- Mocking "just to be safe".

## Bottom Line

**Mocks isolate, they are not the thing tested.** If TDD reveals you are testing mock
behavior, test real behavior or question why you are mocking at all.
