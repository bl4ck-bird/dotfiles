---
name: ship-check
description: Use when preparing to hand off, commit, merge, open a PR, or release after implementation and focused reviews.
---

# Ship Check

Final readiness pass before handing work back, committing, stacking, opening a PR, or shipping.

## Preconditions

Substantial work should have:

- Acceptance artifact with criteria (spec, PRD, issue, review finding, approved task). Artifact's Self-Review (see `write-spec` / `write-plan`) completed.
- Implementation plan or clear small-task rationale.
- TDD or regression coverage where behavior changed.
- `spec-compliance-review` returned ✅ Spec compliant for each implemented slice.
- `code-quality-review` returned Ready to merge: Yes (or With fixes followed by applied fixes + re-run returning Yes).
- `security-review` run when security-sensitive surface touched, or explicitly noted as not triggered.
- `second-review` run when High-Risk Surface touched or user requested independent double-check, or fallback recorded per `second-review` Fallback Record.
- `receiving-review` applied when fixes taken from any reviewer (one item at a time, YAGNI checked).
- `docs-sync` considered.
- Commit, PR, release, or stacked-branch actions approved when they are part of next step.

## Tiny/Local Pass

Tiny/local (one bounded module, no product/domain/API/data/security decision changing, no High-Risk Surface): run only steps **1, 3, 9, 11** below. Mark rest as "N/A — tiny/local scope". Do not run full 11-step checklist for changes the Workflow Weight table classifies as Tiny/local.

If change set grows past Tiny/local definition, escalate to full checklist before continuing.

## Checklist

1. Inspect `git status` and confirm change set is scoped to request.
2. Read relevant diff and ensure no unrelated user changes were reverted.
3. Run narrowest meaningful tests, type checks, linters, or build checks. Apply `verification-before-completion` — "green" claims require fresh output read in this response, not remembered prior run.
4. Confirm docs sync was considered for changed behavior, architecture, tests, security.
5. Confirm `docs/CURRENT.md` reflects final current phase, blocker status, last verification, next action when substantial work changed state.
6. Confirm `spec-compliance-review` and `code-quality-review` were run with passing results, and `security-review` was run or explicitly noted as not triggered.
7. Run or request `second-review` for required High-Risk Surface changes, or note why optional independent double-check is not needed.
8. Confirm no source file crossed file-size thresholds from `code-quality-review` (File And Complexity Thresholds) without review.
9. Confirm validation was not gamed by weakening assertions, narrowing coverage, skipping relevant checks, or changing tests to match broken behavior.
10. Decide commit status: not requested, ready to commit, committed, or blocked.
11. Summarize result with verification evidence and residual risk.

If independent review required but unavailable, do not silently pass. Record unavailable reason, compensating review, accepted risk, whether user explicitly accepted shipping without it.

Relevant checks already failed before this work → state clearly, do not attribute to your change. Check fails after your change → make one targeted fix when cause is clear; otherwise stop and report with evidence.

## Finishing Options

When tests pass and slice is reviewed, present a structured choice rather than open-ended "what next?". Standard options: merge locally / push and create PR / keep as-is / discard. Detached-HEAD environments drop merge option.

Judgment rules (host runs commands):

- **Merge**: delete feature branch and clean up worktree *after* merge succeeds, not before.
- **PR**: keep worktree alive for review iteration.
- **Discard**: require user to confirm explicitly (typed token recommended) before deletion.

## Commit / Stack Gate

Do not commit, push, create PRs, or rewrite history unless user requested, project-local instructions require, or approved bounded goal includes that action.

When commit or stack work approved:

1. Inspect `git status` and diff before staging.
2. Stage only files owned by completed task or slice.
3. Prefer one commit per completed vertical slice when history matters.
4. Stacked branches: each branch focused on one review concern, record stack order (parent → child) in PR description.
5. Run available pre-commit and commit-msg hooks.
6. Report commit hash, PR URL, or reason action was blocked.

Prefer host agent's commit/PR helper (Claude Code `commit-commands` plugin, Codex commit recipe, project script) when available. Otherwise `git`/`gh`.

## Worktree Cleanup Provenance

Cleanup ownership and procedure live in `using-git-worktrees` Cleanup. Summary: only remove worktrees this harness created (under `.worktrees/` or `worktrees/`). Worktrees owned by host native tools or other agents must be left in place. Always `cd` to main repo root before `git worktree remove`. Order: merge → cleanup worktree → delete branch.

Commit not approved → report change is ready to commit and suggest a commit message.

## Retro (optional)

After substantial work, capture one to three short lines:

- What worked
- What surprised us
- One rule worth keeping for future work

Promote a rule into host agent's memory system only when non-obvious from code and would help future sessions; host agent (e.g. Claude global `auto memory`) owns format and classification. Otherwise leave the line in the review record.

User has `retro-capture` skill installed → that skill picks up memory candidates and routes through host agent's persistent memory. `retro-capture` is external to BB Harness, so this skill names but does not require it — Retro lines stand on their own either way.

## Output

Keep final report short:

- What changed
- What was verified
- Focused reviews completed
- Independent review status
- Docs updated or intentionally unchanged
- Commit status and suggested message or commit hash
- What remains risky or unverified
- Memory candidates: persist non-obvious rules through host agent's memory system per Retro guidance above.

## Do Not Ship If

- Required checks fail.
- Implementation does not match accepted behavior.
- Critical or Important review finding unresolved.
- Validation weakened or skipped to make result look green.
- Final answer would need to hide uncertainty.

## Rollback And Incident Response

When a shipped change breaks production, downstream tests, or accepted behavior:

1. **Stop forward work.** Do not stack a fix on top — revert first, debug after.
2. **Pick the revert path** by blast radius:
   - Single commit on main, no dependent work → `git revert <sha>` (creates a revert commit; history-safe).
   - Multiple commits, intertwined → revert the merge with `git revert -m 1 <merge-sha>`.
   - Pre-merge (PR not yet merged) → close PR or push a fix; do not force-push shared branches.
   - Deployed artifact (container/binary/release) → redeploy previous artifact first, then revert source.
3. **Verify rollback closed the symptom.** Re-run the failing check that triggered the incident. Apply `verification-before-completion` — read the output, not the deployer's word.
4. **Open a regression test that reproduces the failure** before re-attempting the change. Per `bug-diagnosis` workflow, no second attempt without a failing test.
5. **Record the incident** in `docs/reviews/YYYY-MM-DD-<topic>-incident.md`:
   - What shipped, what broke, blast radius, who was affected
   - Detection signal and lead time
   - Revert commands run + verification evidence
   - Root cause (or hypothesis if unconfirmed)
   - Follow-up: test added, durable doc updated, decision recorded
6. **Update `docs/CURRENT.md`** with the incident and the recovery state.

Do not delete the broken commit (history-rewrite). Do not silently re-roll the same change without addressing the root cause and adding regression coverage. Project-specific deploy commands and revert procedures belong in `docs/AGENT_WORKFLOW.md`.
