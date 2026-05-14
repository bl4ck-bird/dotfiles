# Review Rules

Harness-wide SSOT for **how reviews iterate, when they stop, and what they may recommend**.
All review skills (`spec-compliance-review`, `code-quality-review`, `security-review`,
`second-review`) and `receiving-review` follow these rules.

Severity classification: see `severity-definitions.md` in this directory.

## Review Iteration Pattern

For each review channel (spec-compliance, code-quality, security, second):

1. **Author or execute** the artifact (slice, diff, plan, spec).
2. **Run the review**.
3. **Act on the result**:
   - **`spec-compliance-review`** — binary:
     - ✅ Spec compliant → next channel.
     - ❌ Issues found → implementer applies fixes via `receiving-review`, re-run.
   - **`code-quality-review` / `security-review` / `second-review`** — three states:
     - **Yes** → next channel or `ship-check`.
     - **With fixes** → implementer applies Critical/Important via `receiving-review`,
       re-run.
     - **No** → plan or acceptance needs revision. Escalate to user; do not loop.
4. **Hard stop after 2 cycles** in the same channel without convergence.
   - Do not run cycle 3 automatically.
   - Summarize unresolved findings.
   - User chooses: reduce scope, accept current state, or revise artifact.
   - Findings introduced in cycle 2 not in cycle 1 must be labeled `introduced-in-cycle-2`
     with reason — signals review scope expanding rather than artifact failing.

Minor findings do not block. List but do not require tracking.

## Review Result Contract

All review skills use this gate. Vocabulary: **`Ready to merge?`** with three answers:

- **Yes** — no Critical or Important remain. Minor may be listed; tracking encouraged not
  required.
- **With fixes** — Critical/Important remain that the implementer can apply directly. Fix via
  `receiving-review`; reviewer re-runs on changed diff.
- **No** — fundamental problem requires plan/acceptance revision, not just code. Escalate to
  user; do not loop.

`spec-compliance-review` is binary: ✅ → `Yes`, ❌ → `With fixes`.

**Hard stop after 2 cycles** — see above. After two cycles without convergence the result is
effectively `No` until the user picks a path.

### Pre-Implementation Verdicts

`write-spec` and `write-plan` reviewer prompts emit parallel three-state verdicts on artifacts (not on merge):

- `Ready to plan: Yes / With fixes / No` (spec reviewer)
- `Ready to execute: Yes / With fixes / No` (plan reviewer)

Same three-state semantics as `Ready to merge?` — Yes/With fixes/No, hard-stop after 2 cycles, Critical/Important/Minor severity. The difference is the artifact under review (spec or plan, not diff) and the next gate (plan or implementation, not merge). Treat all rules in this file as applying to these verdicts as well.

## Review Chain Depth Cap

A focused review may automatically recommend **at most one** follow-on review.

- `code-quality-review` recommends `security-review` (auth touched) → allowed.
- `code-quality-review` recommends `security-review` *and* `second-review` → pick one
  automatic, name the other as a recommendation requiring user confirmation.

A second hop (auto `security-review` then recommends another) **requires user confirmation**.
Stops chains from inflating into "review of review of review" loops.

**Exemption**: `second-review` is exempt from the cap when its Required When Available
criteria are met (High-Risk Surface, explicit double-check, boundary/dependency-direction
change — see `second-review`).

## Review Scope Guard

Findings stay inside the approved acceptance artifact, plan, and touched surface.

- Do not propose new product behavior, broad rewrites, new deps, new storage/API shape, or
  unrelated cleanup as required fixes.
- Real issue outside approved scope → **Minor** unless it is a **Critical** defect in the
  touched path (per `severity-definitions.md` Untouched-Code Rule).
- A required fix may expand scope only with explicit user approval or an accepted-risk record
  updated in the plan.
- "Could be better organized" is not a finding. "This diff adds a reason-to-change that
  conflicts with existing responsibility at `file:line`" is a finding.
- YAGNI applies to reviewers too. Speculative future-proofing is Minor at best.
- Do not recommend large rewrites unless the current design blocks the requested work. Prefer
  small refactor slices that keep tests green.

## When Review Says "Plan Needs Revision"

A `No` result is the system working, not defeat. The authoring skill (`write-spec` /
`write-plan`) is the right place to revise. Do not fight with cycle-2 fixes.

Signs the plan really needs revision:

- Acceptance criterion cannot be satisfied with planned file structure.
- Plan assumes an architecture decision that conflicts with `docs/ARCHITECTURE.md`.
- Implementation requires a domain change not in `CONTEXT.md` / `docs/DOMAIN_MODEL.md`.
- Two slices write the same file and cannot run in either order.

Escalate, revise the plan, restart from the affected slice. Completed earlier slices stay
completed (their reviews already passed).

## Receiving Review Feedback

Once a reviewer returns findings, the next action goes through `receiving-review` before
applying any fix:

- Read all findings first; do not react.
- Restate each finding's technical requirement.
- Verify against codebase / acceptance artifact.
- Push back with technical reasoning when wrong.
- Apply one item at a time, running verification after each (per
  `verification-before-completion`).

`receiving-review` SKILL.md owns the full procedure. This file only states the ordering:
review returns → `receiving-review` → fix → re-run review.

## Cross-Reference

Callers of this file:

- `using-bb-harness` SKILL.md links here.
- Each review skill quotes the iteration rule and scope guard.
- `subagent-driven-development` and `executing-plans-inline` use Hard Stop After 2 Cycles in
  their loop.
- `claude-agents/*-reviewer.md` instructs reviewers to apply the scope guard.

If you change a rule here, audit those callers in the same change.
