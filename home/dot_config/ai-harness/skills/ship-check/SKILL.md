---
name: ship-check
description: Use when preparing to hand off, commit, merge, open a PR, or release after implementation and focused reviews.
---

# Ship Check

Run a final readiness pass before handing work back, committing, stacking, opening a PR,
or shipping it.

## Preconditions

Before ship-check, substantial work should have:

- Acceptance artifact with acceptance criteria: spec, PRD, issue, review finding, or approved
  task. The artifact's own Self-Review (see `write-spec` / `write-plan`) completed.
- Implementation plan or clear small-task rationale.
- TDD or regression coverage where behavior changed.
- `spec-compliance-review` returned ✅ Spec compliant for each implemented slice.
- `code-quality-review` returned Ready to merge: Yes (or With fixes followed by applied
  fixes and a re-run that returned Yes).
- `security-review` run when a security-sensitive surface was touched, or explicitly noted
  as not triggered.
- `second-review` run when a High-Risk Surface was touched or the user requested an
  independent double-check, or fallback recorded per `second-review` Fallback Record.
- `receiving-review` applied when fixes were taken from any reviewer (one item at a time,
  YAGNI checked).
- `docs-sync` considered.
- Commit, PR, release, or stacked-branch actions approved when they are part of the next
  step.

## Tiny/Local Pass

For Tiny/local changes (one bounded module, no product/domain/API/data/security decision changing,
no High-Risk Surface touched), run only steps **1, 3, 9, 11** below. Mark the rest as
"N/A — tiny/local scope" in the report. Do not run the full 11-step checklist for changes that the
Workflow Weight table classifies as Tiny/local.

If the change set later grows past the Tiny/local definition, escalate to the full checklist
before continuing.

## Checklist

1. Inspect `git status` and confirm the change set is scoped to the request.
2. Read the relevant diff and ensure no unrelated user changes were reverted.
3. Run the narrowest meaningful tests, type checks, linters, or build checks available.
   Apply `verification-before-completion` — claims of "green" require fresh output read in
   this response, not a remembered prior run.
4. Confirm docs sync was considered for changed behavior, architecture, tests, and security.
5. Confirm `docs/CURRENT.md` reflects the final current phase, blocker status, last verification,
and next action when substantial work changed state.
6. Confirm `spec-compliance-review` and `code-quality-review` were run with passing results,
   and `security-review` was run or explicitly noted as not triggered.
7. Run or request `second-review` for required High-Risk Surface changes, or note why
   optional independent double-check is not needed.
8. Confirm no source file crossed the file-size thresholds defined in
   `code-quality-review` (File And Complexity Thresholds) without review.
9. Confirm validation was not gamed by weakening assertions, narrowing coverage, skipping relevant
checks, or changing tests to match broken behavior.
10. Decide commit status: not requested, ready to commit, committed, or blocked.
11. Summarize the result with verification evidence and residual risk.

If independent review is required but unavailable, do not silently pass. Record the unavailable
reason, compensating review, accepted risk, and whether the user explicitly accepted shipping
without it.

If relevant checks already failed before this work, state that clearly and do not attribute
them to your change. If a check fails after your change, make one targeted fix when the
cause is clear; otherwise stop and report the failure with evidence.

## Finishing Options

When tests pass and the slice is reviewed, present a structured choice rather than an open-ended
"what next?". Standard options: merge locally / push and create PR / keep as-is / discard.
Detached-HEAD environments drop the merge option.

Judgment rules (host runs the commands):

- **Merge**: only delete the feature branch and clean up the worktree *after* the merge
  succeeds, not before.
- **PR**: keep the worktree alive for review iteration.
- **Discard**: require the user to confirm explicitly (typed token recommended) before deletion.

## Commit / Stack Gate

Do not commit, push, create PRs, or rewrite history unless the user requested it, project-local
instructions require it, or an approved bounded goal includes that action.

When commit or stack work is approved:

1. Inspect `git status` and the diff before staging.
2. Stage only files owned by the completed task or slice.
3. Prefer one commit per completed vertical slice when history matters.
4. For stacked branches, keep each branch focused on one review concern and record stack order
   (parent → child) in the PR description.
5. Run available pre-commit and commit-msg hooks.
6. Report the commit hash, PR URL, or the reason the action was blocked.

Prefer the host agent's commit/PR helper (Claude Code `commit-commands` plugin, Codex commit
recipe, or project script) when available. Otherwise run standard `git`/`gh` commands.

## Worktree Cleanup Provenance

Cleanup ownership and procedure live in `using-git-worktrees` Cleanup. Summary: only
remove worktrees this harness created (under `.worktrees/` or `worktrees/`). Worktrees
owned by host native tools or other agents must be left in place. Always `cd` to the main
repo root before `git worktree remove`. Order: merge → cleanup worktree → delete branch.

If commit is not approved, report that the change is ready to commit and suggest a commit
message.

## Retro (optional)

After substantial work, capture one to three short lines:

- What worked
- What surprised us
- One rule worth keeping for future work

Promote a rule into the host agent's memory system only when it is non-obvious from the code and
would help future sessions; the host agent (e.g. Claude global `auto memory`) owns format and
classification. Otherwise leave the line in the review record.

## Output

Keep the final report short:

- What changed
- What was verified
- Focused reviews completed
- Independent review status
- Docs updated or intentionally unchanged
- Commit status and suggested message or commit hash
- What remains risky or unverified
- Memory candidates: persist non-obvious rules through the host agent's memory system per Retro
  guidance above.

## Do Not Ship If

- Required checks fail.
- The implementation does not match the accepted behavior.
- A Critical or Important review finding is unresolved.
- Validation was weakened or skipped to make the result look green.
- The final answer would need to hide uncertainty.
