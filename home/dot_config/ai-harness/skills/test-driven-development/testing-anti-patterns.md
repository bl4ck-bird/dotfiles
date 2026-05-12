# Testing Anti-Patterns

Load this reference when writing or changing tests, adding mocks, or tempted to add
test-only methods to production code.

## Overview

Tests must verify real behavior, not mock behavior. Mocks are a means to isolate, not
the thing being tested.

**Core principle**: test what the code does, not what the mocks do.

**Following strict TDD prevents these anti-patterns.** Each one is a signal that a step
of the Red-Green-Refactor cycle was skipped or rationalized.

## The Iron Laws

```text
1. NEVER test mock behavior.
2. NEVER add test-only methods to production classes.
3. NEVER mock without understanding the dependency chain.
4. NEVER use partial mocks of structures you do not fully understand.
5. NEVER claim "done" without tests written first (per TDD Iron Law).
```

## Anti-Pattern 1: Testing Mock Behavior

**Violation:**

```typescript
// ❌ BAD — Asserting that the mock exists
test('renders sidebar', () => {
  render(<Page />);
  expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();
});
```

**Why wrong:** you are verifying the mock works, not that the component works. The
test passes when the mock is present and fails when it is not — it tells you nothing
about real behavior.

**Fix:**

```typescript
// ✅ GOOD — Test the real component, or do not mock it
test('renders sidebar', () => {
  render(<Page />);  // Do not mock sidebar
  expect(screen.getByRole('navigation')).toBeInTheDocument();
});
```

If sidebar must be mocked for isolation, do not assert on the mock — test the parent's
behavior with the sidebar present.

### Gate

```text
BEFORE asserting on any mock element:
  Ask: "Am I testing real component behavior or just mock existence?"

  IF testing mock existence:
    STOP — delete the assertion or unmock the component.
    Test real behavior instead.
```

## Anti-Pattern 2: Test-Only Methods In Production

**Violation:**

```typescript
// ❌ BAD — destroy() is only used by tests
class Session {
  async destroy() {                // looks like a production API
    await this._workspaceManager?.destroyWorkspace(this.id);
  }
}

// In tests
afterEach(() => session.destroy());
```

**Why wrong:**

- Production class is polluted with test-only code.
- Dangerous if accidentally called from production.
- Violates YAGNI and separation of concerns.
- Confuses object lifecycle with entity lifecycle.

**Fix:**

```typescript
// ✅ GOOD — Test utilities handle test cleanup
// Session has no destroy() — it is stateless in production.

// test-utils/
export async function cleanupSession(session: Session) {
  const workspace = session.getWorkspaceInfo();
  if (workspace) {
    await workspaceManager.destroyWorkspace(workspace.id);
  }
}

// In tests
afterEach(() => cleanupSession(session));
```

### Gate

```text
BEFORE adding any method to a production class:
  Ask: "Is this only used by tests?"
  IF yes: STOP — put it in test utilities instead.

  Ask: "Does this class own this resource's lifecycle?"
  IF no:  STOP — wrong class for this method.
```

## Anti-Pattern 3: Mocking Without Understanding

**Violation:**

```typescript
// ❌ BAD — Mock breaks the test logic
test('detects duplicate server', () => {
  vi.mock('ToolCatalog', () => ({
    discoverAndCacheTools: vi.fn().mockResolvedValue(undefined),
  }));

  await addServer(config);
  await addServer(config);  // Should throw — but the mock removed the side effect
});
```

**Why wrong:** the mocked method had a side effect (writing config) that the test
depends on. Over-mocking "to be safe" breaks actual behavior. The test passes for the
wrong reason or fails mysteriously.

**Fix:**

```typescript
// ✅ GOOD — Mock at the correct level
test('detects duplicate server', () => {
  vi.mock('MCPServerManager'); // Mock only the slow server startup
  await addServer(config);     // Config is still written
  await addServer(config);     // Duplicate detected ✓
});
```

### Gate

```text
BEFORE mocking any method:
  STOP. Do not mock yet.

  1. Ask: "What side effects does the real method have?"
  2. Ask: "Does this test depend on any of those side effects?"
  3. Ask: "Do I fully understand what this test needs?"

  IF the test depends on side effects:
    Mock at a lower level (the slow / external operation),
    OR use a test double that preserves the necessary behavior,
    NOT the high-level method the test depends on.

  IF unsure what the test depends on:
    Run the test with the real implementation FIRST.
    Observe what actually needs to happen.
    THEN add minimal mocking at the right level.

  Red flags:
    - "I'll mock this to be safe."
    - "This might be slow, better mock it."
    - Mocking without understanding the dependency chain.
```

## Anti-Pattern 4: Incomplete Mocks

**Violation:**

```typescript
// ❌ BAD — Partial mock with only the fields you think you need
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' },
  // Missing: metadata that downstream code uses
};

// Later: breaks when code accesses response.metadata.requestId
```

**Why wrong:**

- Partial mocks hide structural assumptions.
- Downstream code may depend on fields you did not include — silent failures.
- Tests pass but integration fails.
- False confidence.

**Iron rule:** mock the *complete* data structure as it exists in reality, not just the
fields your immediate test uses.

**Fix:**

```typescript
// ✅ GOOD — Mirror real API completeness
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' },
  metadata: { requestId: 'req-789', timestamp: 1234567890 },
};
```

### Gate

```text
BEFORE creating a mock response:
  Check: "What fields does the real API response contain?"

  Actions:
    1. Examine actual response from docs / examples / a captured real call.
    2. Include ALL fields the system might consume downstream.
    3. Verify mock matches the real response schema completely.

  If you are creating a mock, you must understand the ENTIRE structure.
  Partial mocks fail silently when code depends on omitted fields.

  If uncertain: include all documented fields.
```

## Anti-Pattern 5: Tests As Afterthought

**Violation:**

```text
✅ Implementation complete
❌ No tests written
"Ready for testing"
```

**Why wrong:** testing is part of implementation, not an optional follow-up. TDD would
have caught this. You cannot claim "done" without tests.

**Fix:** apply the TDD cycle as defined in the parent `SKILL.md`:

```text
1. Write the failing test.
2. Watch it fail (verification-before-completion).
3. Implement to pass.
4. Watch it pass (verification-before-completion).
5. Refactor.
6. THEN claim complete.
```

## When Mocks Become Too Complex

Warning signs:

- Mock setup is longer than the test logic.
- Mocking everything to make the test pass.
- Mocks are missing methods that real components have.
- The test breaks when the mock changes.

Ask: "Do we need to be using a mock here?" Often an integration test with real
components is simpler than a complex mock.

## TDD Prevents These Anti-Patterns

1. **Write the test first** → forces you to think about what you are actually testing.
2. **Watch it fail** → confirms the test exercises real behavior, not the mock.
3. **Minimal implementation** → no test-only methods creep in.
4. **Real dependencies first** → you see what the test actually needs before mocking.

If you are testing mock behavior, you violated TDD — you added mocks without watching
the test fail against real code first.

## Quick Reference

| Anti-pattern | Fix |
| --- | --- |
| Assert on mock elements | Test the real component or unmock it |
| Test-only methods in production | Move to test utilities |
| Mock without understanding | Understand dependencies first, mock minimally |
| Incomplete mocks | Mirror real API completely |
| Tests as afterthought | TDD — tests first |
| Over-complex mocks | Consider integration tests with real components |

## Red Flags

- Assertion checks for `*-mock` test IDs.
- Methods only called in test files.
- Mock setup is more than half the test.
- The test fails when you remove the mock.
- Cannot explain why the mock is needed.
- Mocking "just to be safe".

## Bottom Line

**Mocks are tools to isolate, not things to test.**

If TDD reveals you are testing mock behavior, you have gone wrong. Test real behavior
or question why you are mocking at all.
