# Severity Definitions

Harness-wide SSOT for review finding severity. All review skills (`spec-compliance-review`,
`code-quality-review`, `security-review`, `second-review`) and reviewer subagents in
`claude-agents/` use this vocabulary. Do not invent local equivalents.

## The Three Levels

- **Critical (Must Fix)** — blocks shipping.
  - Correctness defect (wrong behavior, wrong output, wrong state).
  - Data loss risk (deletion without confirmation, irreversible operation without approval,
    lost writes, corrupted persistence).
  - Security / auth / crypto vulnerability (injection, traversal, auth bypass, leaked secret,
    broken crypto, missing authorization at the right boundary).
  - Destructive operation without approval.
  - Accepted behavior from the acceptance artifact not met.
  - Silent failure (swallowed exception, fallback that masks the bug).
  - Missing test for a behavior the diff claims to implement.

- **Important (Should Fix)** — blocks the next phase.
  - Architecture flaw in the touched path: wrong boundary, framework leakage into domain,
    dependency direction reversed, file/function past 300/600 threshold without documented
    exception.
  - Test design flaw: mocks remove the behavior under test, regression test passes without
    Red-Green-Revert, missing edge case coverage for a claimed criterion.
  - Durable doc claim already false (`CONTEXT.md` glossary out of sync,
    `docs/ARCHITECTURE.md` describes the old shape).
  - Missing error handling on a path that can actually fail.
  - DDD violation in the touched path: ubiquitous-language drift, missing aggregate
    invariant test, cross-context import without translation.

- **Minor (Nice To Have)** — does not block.
  - Style, naming polish, comment hygiene.
  - Optimization opportunity (no measured impact).
  - Out-of-scope improvement.
  - Speculative future-proofing concern.
  - DRY without measured duplication cost.
  - Comments that could be clearer (no information loss).

## Untouched-Code Rule

Findings on code **not touched by the current diff or artifact** are Minor by default.

Exception: a finding may be Critical or Important on untouched code when the change makes
that code unsafe — e.g., a new caller passes an invalid value to a previously safe function.
The finding must cite **explicit evidence of the new unsafety**, not speculation.

This rule prevents review scope creep. A reviewer who wants to fix "all the problems they
saw" promotes them to Critical and the cycle never ends.

## Do Not Promote A Finding

Reviewers must not promote a finding above its real impact to get it fixed. A genuinely Minor
finding the reviewer "really wants fixed" stays Minor — the implementer applies at
discretion, not a fake Important to force their hand.

Symptoms of severity inflation:

- Many Critical findings with no shipping risk explained.
- Important findings where the impact is "could be cleaner".
- Re-promotion across cycles ("you didn't fix this, so it's Critical now").

When you catch yourself escalating, demote. The hard-stop-after-two-cycles rule exists in
part to catch this.

## Cross-Reference

- `using-bb-harness` Review Result Contract (in `review-rules.md`) uses these definitions to
  gate the `Ready to merge?` answer.
- `code-quality-review` Severity section quotes this file.
- `security-review` Severity section uses Critical / Important / Minor directly.
- Each `claude-agents/*-reviewer.md` instructs reviewers to apply these definitions.

If you change a definition here, audit those callers in the same change.
