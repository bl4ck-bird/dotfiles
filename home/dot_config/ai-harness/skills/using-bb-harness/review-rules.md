# Review Rules

Harness-wide SSOT for **how reviews iterate, when they stop, and what they may
recommend**. All review skills (`spec-compliance-review`, `code-quality-review`,
`security-review`, `second-review`) and `receiving-review` follow these rules.

For severity classification of individual findings, see `severity-definitions.md` in
this directory.

## Review Iteration Pattern

For each review channel (spec-compliance, code-quality, security, second):

1. **Author or execute** the artifact (slice, diff, plan, spec).
2. **Run the review**.
3. **Act on the result**:
   - **`spec-compliance-review`** — binary:
     - ✅ Spec compliant → proceed to the next channel.
     - ❌ Issues found → implementer applies fixes via `receiving-review`, re-run
       this review.
   - **`code-quality-review` / `security-review` / `second-review`** — three states:
     - **Ready to merge: Yes** → proceed to the next channel or to `ship-check`.
     - **Ready to merge: With fixes** → implementer applies Critical / Important
       findings via `receiving-review`, re-run this review.
     - **Ready to merge: No** → plan or acceptance needs revision. Escalate to the
       user; do not loop on review-fix.
4. **Hard stop after 2 cycles** in the same review channel without convergence.
   - Do not run a third cycle automatically.
   - Summarize unresolved findings.
   - Ask the user to choose: reduce scope, accept the current state, or revise the
     artifact.
   - Findings introduced in cycle 2 that were not in cycle 1 must be labeled
     `introduced-in-cycle-2` with a reason. This is the signal that the *review
     scope* is expanding rather than the *artifact* failing.

Minor findings do not block. List them but do not require tracking.

## Review Result Contract

All review skills use this gate. Authoring skills must apply it when reading review
results.

- **Blocked** — any unresolved Critical / Important finding, missing required
  evidence, or acceptance mismatch.
- **Pass with follow-ups** — only Minor findings remain. Every follow-up is tracked
  in an issue, plan task, or accepted-risk record. No accepted behavior is changed.
- **Pass** — no material findings remain.
- **Hard stop after 2 cycles** — see Review Iteration Pattern above.

The contract maps to the user-facing `Ready to merge?` answer:

| Review Result | Ready to merge? |
| --- | --- |
| Pass | Yes |
| Pass with follow-ups | With fixes (if any follow-up requires action) or Yes |
| Blocked | No |

## Review Chain Depth Cap

A focused review may automatically recommend **at most one** follow-on review.
Examples:

- `code-quality-review` recommends `security-review` because the diff touches auth →
  allowed, one follow-on.
- `code-quality-review` recommends `security-review` *and* `second-review` →
  pick one automatic, name the other as a recommendation requiring user
  confirmation.

A second hop (e.g., the auto-recommended `security-review` then recommends another
review) **requires user confirmation**. This stops chains from inflating into
"review of review of review" loops on small to medium work.

**Exemption**: `second-review` is exempt from the cap when its Required When
Available criteria are met (High-Risk Surface, explicit double-check request, or
boundary / dependency-direction change — see `second-review`).

## Review Scope Guard

Review findings must stay inside the approved acceptance artifact, plan, and touched
surface.

- Do not propose new product behavior, broad rewrites, new dependencies, new
  storage / API shape, or unrelated cleanup as required fixes.
- If a real issue is outside approved scope, classify it as **Minor** unless it is a
  **Critical** defect in the touched path (per `severity-definitions.md`
  Untouched-Code Rule).
- A required fix may expand scope only with explicit user approval or an
  accepted-risk record updated in the plan.
- "Could be better organized" is not a finding. "This diff adds a reason-to-change
  that conflicts with existing responsibility at `file:line`" is a finding.
- YAGNI applies to reviewers too. Speculative future-proofing is Minor at best.
- Do not recommend large rewrites unless the current design blocks the requested
  work. Prefer small refactor slices that keep tests green.

## When Review Says "Plan Needs Revision"

A `Ready to merge: No` result is not a defeat — it is the system working. The
authoring skill (`write-spec` / `write-plan`) is the right place to revise. Do not
fight the result with cycle 2 fixes.

Signs the plan really does need revision:

- The acceptance criterion cannot be satisfied with the planned file structure.
- The plan assumes an architecture decision that conflicts with `docs/ARCHITECTURE.md`.
- Implementing the plan requires a domain change not captured in `CONTEXT.md` /
  `docs/DOMAIN_MODEL.md`.
- Two slices in the plan write the same file and they cannot run in either order.

Escalate, revise the plan, restart from the affected slice. The completed earlier
slices stay completed (their reviews already passed).

## Receiving Review Feedback

Once a reviewer returns findings, the next agent action goes through `receiving-review`
before applying any fix:

- Read all findings first; do not react.
- Restate each finding's technical requirement.
- Verify against the codebase / acceptance artifact.
- Push back with technical reasoning when wrong.
- Apply one item at a time, running verification after each (per
  `verification-before-completion`).

`receiving-review` SKILL.md owns the full procedure. This file only states the
ordering: review returns → `receiving-review` → fix → re-run review.

## Cross-Reference

Callers of this file:

- `using-bb-harness` SKILL.md links here for the full rules.
- Each review skill quotes the iteration rule and the scope guard.
- `subagent-driven-development` and `executing-plans-inline` use the Hard Stop After
  2 Cycles in their loop.
- `claude-agents/*-reviewer.md` instructs reviewers to apply the scope guard.

If you change a rule here, audit those callers in the same change.
