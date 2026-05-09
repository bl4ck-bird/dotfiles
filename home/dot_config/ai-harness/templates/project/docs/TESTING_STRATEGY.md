# Testing Strategy

Document status: stub. TODO claims are not project truth yet. Non-TODO workflow, safety, and quality rules apply immediately.

## TDD Rule

For behavior changes, write one failing behavior test first, confirm the expected failure, implement the smallest change, then refactor after green.

Reasonable exceptions:

- generated code
- pure documentation
- mechanical config without a test harness
- throwaway prototype
- emergency fix with documented residual risk

## Test Pyramid

- Unit: TODO
- Integration: TODO
- End-to-end: TODO
- Manual or exploratory: TODO

## Required Checks

- Install: TODO
- Focused test: TODO
- Full test: TODO
- Typecheck: TODO
- Lint: TODO
- Build: TODO
- E2E/manual: TODO

## Principles

- Prefer behavior-focused tests.
- Avoid tests that only duplicate implementation details.
- Cover risky edge cases, data boundaries, and error handling.
- Test names should use project domain language from `CONTEXT.md` when relevant.
- Regression tests should fail before the fix and pass after the fix.
- Avoid mocking away the behavior under test.

## What To Test

- Domain invariants
- User-visible workflows
- Application use cases
- Adapter contracts
- Error and edge cases
- Security-sensitive input handling
- Migration or compatibility behavior

## What Not To Overfit

- Private helper names
- Incidental file layout
- Framework internals
- Mock call counts that do not prove behavior

## Review Checklist

Before shipping:

- Did at least one test fail before implementation?
- Do tests prove acceptance criteria?
- Are critical edge cases covered?
- Are tests stable and reasonably fast?
- Does the suite protect against the bug or regression being fixed?
- Are there remaining manual checks or untested risks?
