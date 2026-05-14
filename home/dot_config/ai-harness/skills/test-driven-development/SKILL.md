---
name: test-driven-development
description: Use when implementing any feature, bug fix, behavior change, or refactor — write the failing test first, watch it fail for the right reason, then write the minimal code to pass.
---

# Test-Driven Development (TDD)

Write the test first. Watch it fail. Write minimal code to pass.

**Core principle**: if you did not watch the test fail, you do not know if it tests the right thing.

**Violating the letter of the rules is violating the spirit of the rules.**

## When To Use

**Always** — new features, bug fixes (regression test fails before fix), behavior changes (API/UX/domain), behavior-preserving refactors (green baseline first).

**Exceptions** — explicit user approval + recorded residual-risk note:

- Throwaway prototype.
- Generated code, pure docs, or mechanical config with no test harness.
- Emergency fix with documented residual risk.

Thinking "skip TDD just this once"? That is rationalization, not pragmatism.

## The Iron Law

```text
NO PRODUCTION CODE CHANGE WITHOUT A FAILING TEST FIRST
```

Wrote code before the test? **Delete it.** Do not keep it as reference, do not adapt it, do not look at it. Implement fresh from the test.

## Red-Green-Refactor

```text
RED  → Verify RED  → GREEN  → Verify GREEN  → REFACTOR  → Verify  → next
 ↑         ↓                       ↓                        ↓
 │    wrong failure            still failing             broke green
 │         ↓                       ↓                        ↓
 └── rewrite test ──────── fix implementation ───── revert refactor
```

### 1. RED — Write One Failing Behavior Test

One focused test through a public interface, user-visible flow, or stable domain boundary.

- One behavior per test. Test name contains "and"? Split.
- Name describes behavior, not implementation.
- Real code paths. No mocks unless unavoidable (`testing-anti-patterns.md`).

### 2. Verify RED — Watch It Fail

**Mandatory. Apply `verification-before-completion`.**

```bash
npm test path/to/test.ts -t "behavior name"
```

Confirm:

- Test fails (not errors).
- Failure message matches the expected reason — feature missing, value mismatch.
- Fails for the right reason, not a typo / missing import / unrelated bug.

**Passes already?** Testing existing behavior. Fix the test.
**Errors?** Fix the error, re-run until it fails for the right reason.

### 3. GREEN — Minimal Code

Simplest implementation that passes the test. No unrequested options, flags, knobs, or "while I'm here" cleanups.

### 4. Verify GREEN — Watch It Pass

**Mandatory. Apply `verification-before-completion`.**

```bash
npm test path/to/test.ts -t "behavior name"
# plus narrow regression: nearby tests, related modules
```

Confirm: target test passes, other tests still pass, output is clean.

**Target fails?** Fix the code, not the test.
**Others fail?** Fix now — green baseline is non-negotiable.

### 5. REFACTOR — Clean Up

After green only. Keep tests green. No new behavior. See **Refactor Gate** below.

### 6. Verify After Refactor

Rerun focused verification with fresh output. Refactor only counts when the test is still green.

## Vertical, Not Horizontal

```text
WRONG: test1, test2, test3 → impl1, impl2, impl3
RIGHT: test1 → impl1 → test2 → impl2 → test3 → impl3
```

Writing all tests before any implementation is planning, not TDD.

## Refactor Gate

After GREEN, before next RED:

- Changed module has one primary reason to change.
- Domain/application logic does not depend on UI/framework/storage/network/filesystem unless the project intentionally uses that shape.
- Interfaces stay small and caller-focused.
- Extract duplication only when the extraction clarifies a real concept.
- Apply file/function size thresholds from `code-quality-review` (File And Complexity Thresholds).

Refactor only after green. Rerun focused verification after.

## Good Tests

Prefer:

- Public interfaces or user-visible behavior.
- Project domain language from `CONTEXT.md`.
- Survive internal refactors.
- Protect invariants and edge cases.
- Cover regression behavior for bugs.

Avoid:

- Assert private helper names or file layout.
- Mock away the behavior being tested.
- Duplicate implementation details.
- Pass without proving new behavior.
- Require broad fixtures when a smaller public interface exists.

Catalog: `testing-anti-patterns.md`.

## Rationalizations And Reality

| Excuse | Reality |
| --- | --- |
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. Bias toward what you built, not what is required. |
| "Already manually tested" | Ad-hoc ≠ systematic. No record, can't re-run, forgotten under pressure. |
| "Deleting X hours is wasteful" | Sunk-cost fallacy. Unverified code is debt. |
| "Keep as reference" | You will adapt it. That is testing after. Delete means delete. |
| "Need to explore first" | Fine. Throw the exploration away. Start with TDD. |
| "Test hard = design unclear" | Listen to the test. Hard to test = hard to use. |
| "TDD will slow me down" | TDD is faster than debugging in production. |
| "Manual test faster" | Manual does not prove edge cases. You will re-test every change. |
| "Existing code has no tests" | You are touching it. Add tests for the part you touch. |
| "Spirit not ritual" | Tests-after answer "what does this do?" Tests-first answer "what should this do?" Different artifact. |

## Red Flags — STOP And Start Over

- Code written before the test.
- Test added after the implementation.
- Test passes immediately on first run.
- Cannot explain why the test failed at RED.
- Tests added "later".
- Rationalizing "just this once".
- Skipping `verification-before-completion` at RED or GREEN.

## Bug Fixes

Run `bug-diagnosis` first to reproduce, form hypotheses, clean up instrumentation. Return here for red-green-refactor with a regression test that fails before the fix. Apply Red-Green-Revert per `verification-before-completion`:

```text
1. Write the regression test.
2. Run on the fix → PASS.
3. Revert the fix.
4. Run → MUST FAIL for the right reason.
5. Restore the fix.
6. Run → PASS.
```

Skip 3-4 and regression coverage is unverified.

## Refactors

Behavior-preserving:

- Establish a green baseline first (`verification-before-completion` reads the output).
- Keep public behavior tests unchanged.
- Small steps that improve responsibility, dependency direction, naming, or testability.
- Focused checks after each risky extraction.

## Output

Per completed behavior:

- Test added or updated.
- RED evidence (failure message read in this response).
- Implementation summary.
- GREEN evidence (passing output read in this response).
- Refactor performed or skipped (with reason).
- Remaining test gaps.

## Companion Reference

- `testing-anti-patterns.md` — anti-patterns: testing mock behavior, test-only methods in production, mocking without understanding, incomplete mocks, integration tests as afterthought. Load when writing/changing tests, adding mocks, or tempted to add test-only methods to production code.
