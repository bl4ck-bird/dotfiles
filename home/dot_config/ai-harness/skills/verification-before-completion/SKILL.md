---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing — requires running the verification command and reading its output in the same response. Evidence before assertions, always.
---

# Verification Before Completion

Claiming work is complete without fresh verification evidence is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always. Violating the letter of this rule violates
the spirit of this rule.

## The Iron Law

```text
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE IN THIS RESPONSE
```

If you have not run the verification command in this message, you cannot claim it passes.
"Should pass", "looks right", "I'm confident" are not verification.

## The Gate

Before any statement that implies success — "done", "fixed", "passes", "ready", "complete",
"works", or any synonym — run this gate:

```text
1. IDENTIFY: which command proves this claim?
2. RUN:      execute the full command (fresh, complete, in this response).
3. READ:     full output, exit code, failure count.
4. VERIFY:   does the output confirm the claim?
   - If NO: state actual status with evidence. Do not claim success.
   - If YES: state the claim *with* the evidence.
5. ONLY THEN: make the claim.

Skipping any step = lying, not verifying.
```

## When To Apply

Always, before:

- Any variation of success / completion / done statements.
- Any expression of satisfaction ("perfect", "great", "all good").
- Committing, pushing, opening a PR, releasing.
- Marking a task complete in TodoWrite or a plan checklist.
- Handing work back to the user or to the next phase skill.
- Approving worker / subagent output ("agent says it's done" needs independent verification).

The rule applies to:

- Exact phrases.
- Paraphrases and synonyms.
- Implications of success ("everything is green", "no more errors").
- Any communication that suggests completion or correctness.

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

A regression test only proves a fix if you can show it would catch a regression. Verify:

```text
1. Write the test.
2. Run it on the fix → PASS.
3. Revert the fix.
4. Run the test → MUST FAIL for the right reason.
5. Restore the fix.
6. Run the test → PASS.
```

Skipping step 3-4 means the test may pass for unrelated reasons; the regression coverage is
unverified.

## Worker / Subagent Output

When a worker subagent (implementer in `subagent-driven-development`, Codex helper, etc.) reports success:

```text
1. Read the actual diff (git diff or files changed).
2. Run the verification commands yourself.
3. Read the output yourself.
4. Only then accept the worker's report.
```

Worker reports are claims, not evidence. The controller verifies independently. This is the
same principle as `spec-compliance-review` — read the code, not the report.

## Acceptance Criteria Verification

Before claiming a slice or task complete:

```text
1. Re-read the acceptance criteria from the artifact.
2. For each criterion, name the test, command, or observation that proves it.
3. Mark any criterion you cannot prove as MISSING and report it.
4. Pass / fail per criterion, not "tests are green" as a blanket.
```

This is the same vocabulary as the Coverage Matrix in `code-quality-review`.

## Red Flags — STOP And Verify

If you catch yourself about to write any of these without fresh verification output in this
response, stop and run the command first:

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

- User says "I don't believe you" — trust broken; subsequent work doubted.
- Broken code shipped — eventually caught by a slower channel, costing more.
- Acceptance criteria silently missed — work declared done but rolled back later.
- Worker / subagent error masked — same bug investigated twice.
- `ship-check` passes on stale evidence — release built on lies.

## Where This Skill Is Required

- Inside `test-driven-development` GREEN and REFACTOR steps.
- Inside `subagent-driven-development` after each implementer subagent reports DONE.
- Inside `spec-compliance-review` and `code-quality-review` before declaring a result.
- Inside `ship-check` for the verification evidence section.
- Inside `bug-diagnosis` after applying a fix and before declaring it resolved.
- Inside `bounded-loop` at each iteration's verification gate.

Each of those skills assumes this skill's iron law. They name it in their checklists but
the rule itself lives here.

## The Bottom Line

Run the command. Read the output. Then claim the result.

No shortcuts. No exceptions. This is non-negotiable.
