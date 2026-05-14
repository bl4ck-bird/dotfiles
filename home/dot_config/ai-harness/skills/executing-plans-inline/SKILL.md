---
name: executing-plans-inline
description: Use when executing an approved implementation plan in the main agent session — for hosts that cannot dispatch subagents, for 1-3 small tasks where dispatch overhead is not worth it, or when the user explicitly asked to keep execution inline.
---

# Executing Plans Inline

Execute approved plan task by task in **main agent session**, same review gates as `subagent-driven-development` but as skill invocations rather than fresh subagent dispatches.

Fallback skill. Prefer `subagent-driven-development` when host can dispatch subagents reliably — fresh context per task is worth the overhead.

## When To Use This Skill Instead Of Subagent-Driven

Use when **any**:

- Host does not support subagent dispatch (no Task tool, no `general-purpose` agent type, no in-tool dispatcher).
- Plan has 1-3 small tasks; subagent dispatch overhead clearly exceeds fresh-context benefit.
- User explicitly asked to keep execution in main session.
- Work needs main agent visibility into long-running interactive state (dev server, watched test runner, REPL) across tasks.

Otherwise: `subagent-driven-development`.

## Cost Of Inline Mode

- Context accumulates. After ~3-4 tasks, controller must re-read earlier files/reviews.
- Self-review weakens — same agent that wrote task N reviews it. `spec-compliance-review` and `code-quality-review` remain mandatory; effectiveness depends on treating own work skeptically.
- Worker/reviewer anti-pattern containment weaker. Apply `receiving-review` strictly.

If costs become a problem mid-plan, switch to `subagent-driven-development` for remaining tasks (plan + acceptance artifact already exist; switch is cheap).

## Preconditions

Same as `subagent-driven-development`:

- Acceptance artifact with criteria.
- Implementation plan with file responsibility mapping + Plan Self-Review completed.
- Core docs read.
- Conditional docs read when relevant.
- Next task small enough to complete and verify in one pass.

## Workspace Isolation

**Required.** Invoke `using-git-worktrees` before the first task — same way as `subagent-driven-development`. Cleanup ownership rules identical.

**Never start implementation on a protected base branch** (`main`, `master`, `develop`, `trunk`, or any branch named as base in the repo's `AGENTS.md` / `CLAUDE.md`) without explicit user consent in this session. See `using-bb-harness` Branch Policy for the full rule.

## Execution Loop (Inline)

```text
Read plan once → identify next task → execute → review → review → next.

For each task in order:

  1. Implement the task in the main agent session.
     - Use test-driven-development for behavior changes.
     - Keep edits scoped to the file responsibility map.
     - Run focused verification with verification-before-completion at each TDD step.

  2. Self-inspect the resulting diff before review.
     - git status / git diff
     - Re-read the acceptance criteria.
     - Re-read the plan task.

  3. Run spec-compliance-review against your own diff.
     Treat your own report with the same skepticism as a worker report —
     "do not trust the report, read the code."
     - ✅ Spec compliant → step 4.
     - ❌ Issues found → apply receiving-review, fix the items, re-run step 3.
     - Stop after two cycles. Escalate to user.

  4. Run code-quality-review against your own diff.
     Apply the SSOT checks (DDD / SOLID / file size / Coverage Matrix / docs drift).
     - Ready to merge: Yes → step 5.
     - Ready to merge: With fixes → apply receiving-review, fix, re-run step 4.
     - Ready to merge: No → plan or acceptance needs revision. Escalate to user.
     - Stop after two cycles. Escalate to user.

  5. Run security-review or second-review if triggered (Review Chain Depth Cap = 1
     automatic follow-on).

  6. Mark task complete. Update plan checklist and any changed docs.

  7. Record residual risk and verification evidence.

  8. If the plan uses per-slice commits, run ship-check before the commit gate.

  9. Continue to the next task. Do not stop to ask for confirmation unless a Required
     User Checkpoint applies.
```

## Continuous Execution

Same as `subagent-driven-development`: do not pause between tasks. User approved plan; execute it. Stop only on Required User Checkpoints below.

## Required User Checkpoints

Four conditions only:

1. **BLOCKED** that cannot be resolved with more context.
2. **Two-cycle review-fix without convergence** in same task.
3. **Plan does not authorize this action.** Actions inside plan's approved scope, files, dependencies, destructive operations, review chain run without checkpoint.
4. **High-Risk Surface** (`security` / `data-loss` / `money` / `auth` / `crypto` / `deletion` / `core architecture` — canonical list in `second-review`) in diff and `second-review` not scheduled.

Items plan authorizes do NOT trigger checkpoint.

## Inline-Mode Self-Review Discipline

Same agent wrote code, now reviews it — extra guards:

- **Read diff with fresh eyes**. `git diff`; don't rely on memory.
- **Re-read acceptance criterion verbatim** per criterion. Match to evidence (test, command output, observation).
- **Apply `verification-before-completion`** at every claim. "Tests pass" → fresh test output read in this response.
- **Apply `receiving-review`** to own findings as if from reviewer — verify before fixing, push back when wrong, one item at a time.
- **Re-check `using-bb-harness` Review Scope Guard** before declaring a finding. Inside diff and approved scope? If not, demote to Minor or note out-of-scope.

## Switching To Subagent-Driven Mid-Plan

Inline mode painful (context bloat, weakening review quality):

1. Write handoff in `docs/reviews/` — completed tasks, decisions, open risks, next task.
2. Hand control to `subagent-driven-development` for remaining tasks. Plan + acceptance artifact already capture full work; switch costs one handoff write.

Preferable to continuing inline when self-review is no longer trustworthy.

## Worker / Reviewer Anti-Patterns

Most of `subagent-driven-development`'s anti-patterns apply. Unique to inline:

- **Treating self-review as adequate without inline-mode discipline** above. Self-review not free in inline mode — requires explicit re-reading.
- **Carrying assumptions from task N into N+1**. Each task starts by re-reading its acceptance criteria, not remembering.
- **Mocking the review** ("I know this is fine"). Run the gate. Read the output.

## Output

After each task:

- Task completed.
- Files changed.
- Tests / checks run with fresh evidence.
- Reviews run (spec-compliance, code-quality, optional follow-on) with results.
- Docs updated or intentionally unchanged.
- Next task.

Switching to `subagent-driven-development` → report switch reason and handoff path.
