---
name: test-driven-development
description: Use when implementing any feature, bug fix, behavior change, or refactor — write the failing test first, watch it fail for the right reason, then write the minimal code to pass.
---

# Test-Driven Development (TDD)

Write the test first. Watch it fail. Write minimal code to pass.

**Core principle**: if you did not watch the test fail, you do not know if it tests the
right thing.

**Violating the letter of the rules is violating the spirit of the rules.**

## When To Use

**Always**, for:

- New features (any size).
- Bug fixes (with a regression test that fails before the fix).
- Behavior changes (API, UX, domain rule).
- Behavior-preserving refactors (establish green baseline first).

**Exceptions** — require explicit user approval and a recorded residual-risk note:

- Throwaway prototype.
- Generated code, purely textual docs, or mechanical config with no test harness.
- Emergency fix where the residual risk is documented.

Thinking "skip TDD just this once"? Stop. That is rationalization, not pragmatism.

## The Iron Law

```text
NO PRODUCTION CODE CHANGE WITHOUT A FAILING TEST FIRST
```

Wrote code before the test? Delete it. Start over.

**No exceptions:**

- Do not keep it "as reference".
- Do not "adapt it" while writing the test.
- Do not look at it.
- Delete means delete.

Implement fresh from the test. Period. The harness defers to the user's explicit
exception list above — everything else falls under the Iron Law.

## Red-Green-Refactor

```text
RED  → Verify RED  → GREEN  → Verify GREEN  → REFACTOR  → Verify  → next
 ↑         ↓                       ↓                        ↓
 │    wrong failure            still failing             broke green
 │         ↓                       ↓                        ↓
 └── rewrite test ──────── fix implementation ───── revert refactor
```

For each behavior:

### 1. RED — Write One Failing Behavior Test

Write one focused test through a public interface, user-visible flow, or stable domain
boundary.

**Requirements:**

- One behavior. If the test name contains "and", split it.
- Clear name that describes behavior, not implementation.
- Real code paths. No mocks unless unavoidable (see `testing-anti-patterns.md`).

### 2. Verify RED — Watch It Fail

**Mandatory. Apply `verification-before-completion`.**

```bash
# project-appropriate command
npm test path/to/test.ts -t "behavior name"
```

Confirm:

- Test fails (not errors).
- Failure message is the expected reason (feature missing, value mismatch).
- Fails because the behavior is missing — not because of a typo, missing import, or
  unrelated bug.

**Test passes already?** You are testing existing behavior. Fix the test.
**Test errors?** Fix the error, re-run until it fails for the right reason.

### 3. GREEN — Minimal Code

Write the simplest implementation that passes the test. Do not add unrequested options,
flags, configuration knobs, or "while I'm here" cleanups.

### 4. Verify GREEN — Watch It Pass

**Mandatory. Apply `verification-before-completion`.**

```bash
npm test path/to/test.ts -t "behavior name"
# plus narrow regression: nearby tests, related modules
```

Confirm:

- The test passes.
- Other tests still pass.
- Output is clean (no warnings, no unexpected logs).

**Test fails?** Fix the code, not the test.
**Other tests fail?** Fix now before continuing — green baseline is non-negotiable.

### 5. REFACTOR — Clean Up

After green only. Keep tests green. Do not add new behavior.

See the Refactor Gate below for what is in scope at this step.

### 6. Verify After Refactor

Rerun the focused verification with fresh output. Refactor only counts when the test is
still green.

## Vertical, Not Horizontal

Work one behavior at a time, end to end.

```text
WRONG: test1, test2, test3 → impl1, impl2, impl3
RIGHT: test1 → impl1 → test2 → impl2 → test3 → impl3
```

Writing all tests before any implementation is a planning task, not TDD. The point of
TDD is the feedback at each cycle.

## Refactor Gate

After GREEN and before the next RED, check maintainability while the change is still
small:

- The changed module has one primary reason to change.
- Domain or application logic does not depend on UI, framework, storage, network, or
  filesystem details unless the project intentionally uses that simpler shape.
- Interfaces stay small and caller-focused.
- Repeated conditionals, duplicated branching, or long functions are extracted only when
  the extraction clarifies a real concept.
- Apply the file/function size thresholds defined in `code-quality-review` (File And
  Complexity Thresholds) when refactoring touched files.

Refactor only after tests are green, and rerun focused verification after the refactor.

## Good Tests

Prefer tests that:

- Exercise public interfaces or user-visible behavior.
- Use project domain language from `CONTEXT.md`.
- Survive internal refactors.
- Protect invariants and edge cases.
- Cover regression behavior for bugs.

Avoid tests that:

- Assert private helper names or file layout.
- Mock away the behavior being tested.
- Duplicate implementation details.
- Pass without proving the new behavior.
- Require broad fixtures when a smaller public interface is available.

Detailed catalog: see `testing-anti-patterns.md` in this directory.

## Why Order Matters

**"I will write tests after to verify it works"**

Tests written after code pass immediately. Passing immediately proves nothing — the
test may exercise the wrong thing, test implementation rather than behavior, miss edge
cases you forgot. You never saw it catch a bug, so you do not know it can.

Test-first forces you to see the test fail, proving it actually tests something.

**"I already manually tested all the edge cases"**

Manual testing is ad-hoc. No record of what you tested, can't re-run when code changes,
easy to forget cases under pressure. Automated tests are systematic. They run the same
way every time.

**"Deleting X hours of work is wasteful"**

Sunk-cost fallacy. The time is gone. Your choice now: delete and rewrite with TDD
(more hours, high confidence) or keep it and add tests after (lower confidence, likely
hidden bugs). Working code without real tests is technical debt — keeping it costs more
in the long run.

**"TDD is dogmatic; pragmatic means adapting"**

TDD *is* pragmatic. Finds bugs before commit (cheaper than debugging after). Prevents
regressions. Documents behavior. Enables safe refactoring. "Pragmatic" shortcuts =
debugging in production = slower.

**"Tests after achieve the same goals — it's spirit not ritual"**

No. Tests-after answer "what does this do?" Tests-first answer "what should this do?"
Tests-after are biased by your implementation. You test what you built, not what is
required. You verify remembered edge cases, not discovered ones. 30 minutes of tests
after ≠ TDD.

## Common Rationalizations

| Excuse | Reality |
| --- | --- |
| "Too simple to test" | Simple code breaks. The test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Tests after achieve same goals" | Tests-after = "what does this do?" Tests-first = "what should this do?" |
| "Already manually tested" | Ad-hoc ≠ systematic. No record, can't re-run. |
| "Deleting X hours is wasteful" | Sunk-cost fallacy. Keeping unverified code is debt. |
| "Keep as reference, write tests first" | You will adapt it. That is testing after. Delete means delete. |
| "Need to explore first" | Fine. Throw away the exploration. Start with TDD. |
| "Test hard = design unclear" | Listen to the test. Hard to test = hard to use. |
| "TDD will slow me down" | TDD is faster than debugging. Pragmatic = test-first. |
| "Manual test faster" | Manual does not prove edge cases. You will re-test every change. |
| "Existing code has no tests" | You are touching it. Add tests for the part you touch. |

## Red Flags — STOP And Start Over

- Code written before the test.
- Test added after the implementation.
- Test passes immediately on first run.
- Cannot explain why the test failed at RED.
- Tests added "later".
- Rationalizing "just this once".
- Skipping `verification-before-completion` at RED or GREEN.

## Bug Fixes

For bugs, run `bug-diagnosis` first to reproduce, form hypotheses, and clean up
instrumentation. Return here for the red-green-refactor cycle with a regression test
that fails before the fix. Apply Red-Green-Revert per `verification-before-completion`
to prove the regression test actually catches the bug:

```text
1. Write the regression test.
2. Run on the fix → PASS.
3. Revert the fix.
4. Run → MUST FAIL for the right reason.
5. Restore the fix.
6. Run → PASS.
```

If step 3-4 do not happen, the regression coverage is unverified.

## Refactors

For behavior-preserving refactors:

- Establish a green baseline first (`verification-before-completion` reads the output).
- Keep public behavior tests unchanged.
- Refactor in small steps that improve responsibility, dependency direction, naming, or
  testability.
- Run focused checks after each risky extraction.

## Output

For each completed behavior, report:

- Test added or updated.
- RED evidence (failure message read in this response).
- Implementation summary.
- GREEN evidence (passing output read in this response).
- Refactor performed or skipped (with reason).
- Remaining test gaps.

## Companion Reference

- `testing-anti-patterns.md` — anti-patterns catalog: testing mock behavior, test-only
  methods in production, mocking without understanding, incomplete mocks, integration
  tests as afterthought. Load when writing or changing tests, adding mocks, or tempted
  to add test-only methods to production code.
