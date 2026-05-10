---
name: bug-diagnosis
description: Use when fixing bugs, flaky tests, production-like failures, unexpected behavior, or regressions before changing implementation code.
---

# Bug Diagnosis

Fix bugs from evidence, not guesses. Reproduction comes before implementation changes.

The reproduction loop is the core of this skill. Iterate on the loop itself: make it faster,
sharpen the assertion, remove flakiness. For non-deterministic bugs, raise the reproduction rate
until it is debuggable rather than chasing a single clean repro.

## Workflow

1. Restate the observed behavior and expected behavior.
2. Build or identify the shortest reproduction loop. Try in roughly this order:
   - failing test at the seam that reaches the bug (unit, integration, e2e)
   - curl/HTTP script against a running dev server
   - CLI invocation diffing stdout against a known-good snapshot
   - headless browser script (Playwright/Puppeteer)
   - replay a captured trace (request payload, event log, network capture)
   - throwaway harness exercising the bug code path with one function call
   - property/fuzz loop for "sometimes wrong output"
   - bisection harness when the bug appeared between two known states
   - differential loop diffing old vs new version on the same input
3. Confirm the reproduction fails for the right reason.
4. Form 3-5 falsifiable hypotheses.
5. Check hypotheses with the cheapest evidence first.
6. Add focused instrumentation only when needed, with a unique prefix and a cleanup plan.
7. Write or preserve a regression test before the fix when practical.
8. Fix the root cause with the smallest change.
9. Rerun the reproduction and relevant checks.
10. Remove temporary instrumentation. Update durable docs if the bug exposed a rule.

## Rules

- Do not patch from intuition when a reproduction loop is available.
- Do not broaden scope into refactoring until the bug is reproduced and understood.
- Do not change tests to match broken behavior unless the expected behavior was wrong and the user
  agrees.
- If reproduction is impossible, explain why and list the evidence used instead.
- Security, money, data-loss, auth, crypto, and concurrency bugs require a stronger regression test
  or explicit residual risk note.

## Hypothesis Format

Use this format for non-trivial bugs:

```text
Hypothesis: <specific mechanism>
Prediction: <what should be observed if true>
Check: <command/file/log/test>
Result: <confirmed/refuted/unknown>
```

## Hand Off To `behavior-tdd`

After reproduction is confirmed and the root cause is identified, return to `behavior-tdd` for the
red-green-refactor cycle: regression test that fails before the fix, then the smallest change that
makes it pass. Do not implement the fix inside this skill; this skill owns reproduction,
hypothesis, and root cause.

## Output

Report:

- Reproduction path
- Root cause
- Fix summary (handed off to `behavior-tdd`)
- Regression coverage
- Verification commands and results
- Residual risk
