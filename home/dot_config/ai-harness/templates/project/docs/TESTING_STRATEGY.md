# Testing Strategy

Document status: stub. TODO claims are not project truth yet. Non-TODO workflow, safety, and quality
rules apply immediately.

## TDD Rule

For behavior changes, write one failing behavior test first, confirm the expected failure, implement
the smallest change, then refactor after green. Production behavior changes may skip TDD only with
explicit user approval and a recorded residual-risk reason.

Reasonable exceptions:

- generated code, pure documentation, or mechanical config without a test harness; record the reason
  in the final report
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

## Hook Policy

Prefer automated project hooks for repeatable checks. When the project uses lefthook, wire only
commands that are already known and stable for the stack, such as focused tests, typecheck, lint,
format check, or secret/file guards.

Do not add or enable lefthook commands that require missing dependencies, slow services,
credentials, or unconfirmed package-manager behavior. Keep manual/browser QA as a documented
exception for behavior that automated tests and hooks cannot cover well.

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
- Are project hooks covering the checks that should run before an approved commit?
- Does the suite protect against the bug or regression being fixed?
- Are there remaining manual checks or untested risks?
