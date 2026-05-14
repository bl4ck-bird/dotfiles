---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing — requires running the verification command and reading its output in the same response. Evidence before assertions, always.
---

# Verification Before Completion

Claiming work complete without fresh verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims. Violating the letter violates the spirit.

## The Iron Law

```text
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE IN THIS RESPONSE
```

Not run in this message? Cannot claim it passes. "Should pass", "looks right", "I'm confident" are not verification.

## The Gate

Before any statement implying success ("done", "fixed", "passes", "ready", "complete", "works", or synonym): **identify the proving command → run it fresh in this response → read full output and exit code → verify it confirms the claim → only then state the claim with that evidence**. Skipping any step = lying, not verifying.

## When To Apply

Always, before:

- Success / completion / done statements.
- Satisfaction ("perfect", "great", "all good").
- Committing, pushing, opening PR, releasing.
- Marking task complete in TodoWrite or plan checklist.
- Handing work back to user or next phase skill.
- Approving worker/subagent output ("agent says it's done" needs independent verification).

Applies to exact phrases, paraphrases, synonyms, implications ("everything is green", "no more errors"), any communication suggesting completion or correctness.

## Required Verification Per Claim

| Claim | Required evidence | Not sufficient |
| --- | --- | --- |
| Tests pass | Test command output: `0 failures` | Previous run, "should pass" |
| Linter clean | Linter output: `0 errors` | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look fine |
| Type check clean | Type checker output | "Compiles in my head" |
| Bug fixed | Re-run the original reproduction → passes | Code changed, assumed fixed |
| Regression test works | Red-green-revert cycle verified | Test passes once on the fix |
| Worker / subagent done | VCS diff inspected | Agent reports "success" |
| Acceptance criteria met | Per-criterion checklist with evidence | "Tests pass, must be done" |

## Regression Test Verification (Red-Green-Revert)

Regression test only proves a fix if you can show it would catch a regression:

```text
1. Write the test.
2. Run it on the fix → PASS.
3. Revert the fix.
4. Run the test → MUST FAIL for the right reason.
5. Restore the fix.
6. Run the test → PASS.
```

Skipping 3-4: test may pass for unrelated reasons; regression coverage unverified.

## Worker / Subagent Output

Worker subagent (implementer in `subagent-driven-development`, Codex helper, etc.) reports success:

```text
1. Read the actual diff (git diff or files changed).
2. Run the verification commands yourself.
3. Read the output yourself.
4. Only then accept the worker's report.
```

Worker reports are claims, not evidence. Controller verifies independently. Same as `spec-compliance-review` — read the code, not the report.

## Acceptance Criteria Verification

Before claiming slice/task complete:

```text
1. Re-read the acceptance criteria from the artifact.
2. For each criterion, name the test, command, or observation that proves it.
3. Mark any criterion you cannot prove as MISSING and report it.
4. Pass / fail per criterion, not "tests are green" as a blanket.
```

Same vocabulary as Coverage Matrix in `code-quality-review`.

## Red Flags — STOP And Verify

About to write any of these without fresh verification in this response? Stop and run first:

- "should work now"
- "probably", "seems to", "I think"
- "all tests pass" / "build is green" / "lint is clean"
- "done", "fixed", "ready"
- "great", "perfect", "all good"
- "the worker completed", "the agent finished"
- "I've added a regression test" (without red-green-revert evidence)

## Rationalization Prevention

| Excuse | Reality |
| --- | --- |
| "Should work now" | Run the verification. |
| "I'm confident" | Confidence ≠ evidence. |
| "Just this once" | No exceptions. |
| "Linter passed" | Linter ≠ compiler ≠ runtime. |
| "Agent said success" | Verify independently. |
| "I'm tired" | Exhaustion ≠ excuse. |
| "Partial check is enough" | Partial proves only the partial scope. |
| "Different words so the rule doesn't apply" | Spirit over letter. |
| "Re-running is wasteful" | One re-run is cheaper than one false-complete claim. |

## Failure Modes If You Skip This

- "I don't believe you" — trust broken; subsequent work doubted.
- Broken code shipped — caught by slower channel, costing more.
- Acceptance criteria silently missed — work declared done, rolled back later.
- Worker/subagent error masked — same bug investigated twice.
- `ship-check` passes on stale evidence — release built on lies.

## Where This Skill Is Required

- `test-driven-development` GREEN and REFACTOR steps.
- `subagent-driven-development` after each implementer subagent reports DONE.
- `spec-compliance-review` and `code-quality-review` before declaring a result.
- `ship-check` verification evidence section.
- `bug-diagnosis` after applying a fix and before declaring resolved.
- `bounded-loop` at each iteration's verification gate.

Those skills assume this iron law; rule itself lives here.

## The Bottom Line

Run the command. Read the output. Then claim the result.

No shortcuts. No exceptions. Non-negotiable.
