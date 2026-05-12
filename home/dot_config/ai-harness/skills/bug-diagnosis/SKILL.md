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
- Do not change tests to match broken behavior unless the expected behavior was wrong and
  the user agrees.
- If reproduction is impossible, explain why and list the evidence used instead.
- Security, money, data-loss, auth, crypto, and concurrency bugs require a stronger
  regression test or explicit residual risk note.
- Apply `verification-before-completion` after the fix — re-run the reproduction in this
  response and read the passing output before claiming the bug is fixed.

## Companion Techniques

When the bug is non-trivial, draw on these BB Harness companion files:

- **`root-cause-tracing.md`** — bug appears deep in the call stack. Trace backward from
  the immediate failure to the original trigger before changing code. Includes stack-trace
  instrumentation pattern and "find the polluter" guidance.
- **`defense-in-depth.md`** — when invalid data flowed through multiple layers. Add
  validation at entry / business / environment / debug layers so the bug becomes
  structurally impossible, not just fixed. Run after the root cause is identified.
- **`condition-based-waiting.md`** — when the bug is a flaky test or async race. Convert
  arbitrary `sleep` / `setTimeout` waits into condition-based polls so the test waits
  for the actual state, not a guess about timing.
- **`test-pollution.md`** — when a test leaves files / state behind, or tests pass alone
  but fail in suite. Includes investigation process, common polluter mechanisms, and
  `find-polluter.sh` bisection script.
- **`debugging-pressure-scenarios.md`** — load when you sense the urge to skip the
  workflow under time, exhaustion, sunk-cost, or social pressure. Three training
  scenarios (production outage, flaky test at 8 pm, senior engineer pushing a fix)
  with the right answer and the failure mode of each shortcut.

Read the companion file when its trigger fits. Do not load all three by default —
`bug-diagnosis` SKILL.md is the entry point; the companions are loaded on demand.

## Hypothesis Format

Use this format for non-trivial bugs:

```text
Hypothesis: <specific mechanism>
Prediction: <what should be observed if true>
Check: <command/file/log/test>
Result: <confirmed/refuted/unknown>
```

## Hand Off To `test-driven-development`

After reproduction is confirmed and the root cause is identified, return to `test-driven-development` for the
red-green-refactor cycle: regression test that fails before the fix, then the smallest change that
makes it pass. Do not implement the fix inside this skill; this skill owns reproduction,
hypothesis, and root cause.

## Output

Report:

- Reproduction path
- Root cause
- Fix summary (handed off to `test-driven-development`)
- Regression coverage
- Verification commands and results
- Residual risk
