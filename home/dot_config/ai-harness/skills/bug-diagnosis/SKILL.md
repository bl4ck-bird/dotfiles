---
name: bug-diagnosis
description: Use when fixing bugs, flaky tests, production-like failures, unexpected behavior, or regressions before changing implementation code.
---

# Bug Diagnosis

Fix bugs from evidence, not guesses. Reproduction comes before implementation changes.

Reproduction loop is the core. Iterate on the loop: faster, sharper, less flaky. For
non-deterministic bugs, raise reproduction rate until debuggable rather than chasing one clean
repro.

## Workflow

1. Restate observed vs expected behavior.
2. Build or identify shortest reproduction loop. Try roughly in order:
   - failing test at the seam (unit, integration, e2e)
   - curl/HTTP script against running dev server
   - CLI invocation diffing stdout against known-good snapshot
   - headless browser script (Playwright/Puppeteer)
   - replay captured trace (request payload, event log, network capture)
   - throwaway harness exercising bug code path with one function call
   - property/fuzz loop for "sometimes wrong output"
   - bisection harness when bug appeared between two known states
   - differential loop diffing old vs new version on same input
3. Confirm reproduction fails for the right reason.
4. Form 3-5 falsifiable hypotheses.
5. Check hypotheses with cheapest evidence first.
6. Add focused instrumentation only when needed, with unique prefix and cleanup plan.
7. Write or preserve a regression test before the fix when practical.
8. Fix root cause with smallest change.
9. Rerun reproduction and relevant checks.
10. Remove temporary instrumentation. Update durable docs if bug exposed a rule.

## Rules

- No patching from intuition when a reproduction loop is available.
- No broadening scope into refactoring until bug is reproduced and understood.
- No changing tests to match broken behavior unless expected behavior was wrong and user agrees.
- Reproduction impossible → explain why and list evidence used instead.
- Security, money, data-loss, auth, crypto, concurrency bugs → stronger regression test or
  explicit residual risk note.
- Apply `verification-before-completion` after fix — re-run reproduction in this response, read
  passing output before claiming fixed.
- Bug spans 2+ independent test files/subsystems with different root causes (multi-domain) →
  use `dispatching-parallel-agents` to investigate concurrently. Apply this workflow per agent
  and integrate findings.

## Companion Techniques

Load on demand:

- **`root-cause-tracing.md`** — bug deep in call stack. Trace backward to original trigger.
  Stack-trace instrumentation, "find the polluter".
- **`defense-in-depth.md`** — invalid data flowed through multiple layers. Add validation at
  entry/business/environment/debug layers so the bug becomes structurally impossible. Run
  after root cause identified.
- **`condition-based-waiting.md`** — flaky test or async race. Convert `sleep`/`setTimeout`
  waits into condition-based polls.
- **`test-pollution.md`** — test leaves files/state behind, or passes alone but fails in suite.
  Investigation process, common polluter mechanisms, `find-polluter.sh` bisection script.
- **`debugging-pressure-scenarios.md`** — urge to skip workflow under time, exhaustion,
  sunk-cost, or social pressure. Three training scenarios with right answer and failure mode.

Do not load all by default. `bug-diagnosis` SKILL.md is the entry point.

## Hypothesis Format

For non-trivial bugs:

```text
Hypothesis: <specific mechanism>
Prediction: <what should be observed if true>
Check: <command/file/log/test>
Result: <confirmed/refuted/unknown>
```

## Hand Off To `test-driven-development`

After reproduction confirmed and root cause identified → `test-driven-development` for
red-green-refactor: regression test fails before fix, then smallest change passes. Do not
implement the fix here — this skill owns reproduction, hypothesis, root cause.

## Output

- Reproduction path
- Root cause
- Fix summary (handed off to `test-driven-development`)
- Regression coverage
- Verification commands and results
- Residual risk
