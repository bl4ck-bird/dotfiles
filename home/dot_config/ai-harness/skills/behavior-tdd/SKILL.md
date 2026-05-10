---
name: behavior-tdd
description: Use when implementing features, bug fixes, behavior changes, or refactors that need tests before production code changes.
---

# Behavior TDD Workflow

Implement public behavior one test at a time through red, green, and refactor. Each test must prove
user-visible behavior, public API behavior, or a domain invariant.

## Core Rule

No production behavior change without first seeing a relevant test fail, unless the user explicitly
chooses an exception and the residual risk is recorded.

Reasonable exceptions:

- throwaway prototype
- generated code, purely textual docs, or mechanical config with no test harness; record the reason
  in the final report
- emergency fix where the residual risk is documented

## Red-Green-Refactor

For each behavior:

1. RED: write one focused behavior test through a public interface, user-visible flow, or stable
domain boundary.
2. Verify RED: run it and confirm it fails for the expected reason.
3. GREEN: write the smallest implementation that passes.
4. Verify GREEN: rerun the focused test and related narrow checks.
5. REFACTOR: clean names, duplication, boundaries, or file responsibility after green.
6. Verify again.

Do not write all tests first and all implementation later. Work vertically.

## Refactor Gate

After GREEN and before moving to the next behavior, check maintainability while the change is still
small:

- The changed module has one primary reason to change.
- Domain or application logic does not depend on UI, framework, storage, network, or filesystem
  details unless the project intentionally uses that simpler shape.
- Interfaces stay small and caller-focused.
- Repeated conditionals, duplicated branching, or long functions are extracted only when the
  extraction clarifies a real concept.
- Apply the file/function size thresholds defined in `architecture-review` (File And Complexity
  Thresholds) when refactoring touched files.

Refactor only after tests are green, and rerun the focused verification after the refactor.

## Good Tests

Prefer tests that:

- exercise public interfaces or user-visible behavior
- use project domain language from `CONTEXT.md`
- survive internal refactors
- protect invariants and edge cases
- cover regression behavior for bugs

Avoid tests that:

- assert private helper names
- mock away the behavior being tested
- duplicate implementation details
- pass without proving the new behavior
- require broad fixtures when a smaller public interface is available

## Bug Fixes

For bugs, run `bug-diagnosis` first to reproduce, form hypotheses, and clean up instrumentation.
Return here for the red-green-refactor cycle with a regression test that fails before the fix.

## Refactors

For behavior-preserving refactors:

- Establish a green baseline first.
- Keep public behavior tests unchanged.
- Refactor in small steps that improve responsibility, dependency direction, naming, or testability.
- Run focused checks after each risky extraction.

## Output

For each completed behavior, report:

- Test added or updated
- RED evidence
- Implementation summary
- GREEN evidence
- Refactor performed or skipped
- Remaining test gaps
