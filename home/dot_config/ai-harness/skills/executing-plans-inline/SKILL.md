---
name: executing-plans-inline
description: Use when executing an approved implementation plan in the main agent session — for hosts that cannot dispatch subagents, for 1-3 small tasks where dispatch overhead is not worth it, or when the user explicitly asked to keep execution inline.
---

# Executing Plans Inline

Execute an approved plan task by task in the **main agent session**, with the same
review gates as `subagent-driven-development` but run as skill invocations rather than
fresh subagent dispatches.

This skill is the fallback. Prefer `subagent-driven-development` whenever the host can
dispatch subagents reliably — fresh context per task is worth the overhead.

## When To Use This Skill Instead Of Subagent-Driven

Use `executing-plans-inline` when **any** of the following:

- The host environment does not support subagent dispatch (no Task tool, no
  `general-purpose` agent type, no in-tool subagent dispatcher).
- The plan has 1-3 small tasks and the subagent dispatch overhead clearly exceeds the
  benefit of fresh context per task.
- The user explicitly asked to keep execution in the main session.
- The work needs the main agent to retain visibility into a long-running interactive
  state (a dev server, a watched test runner, a REPL) across multiple tasks.

Otherwise: `subagent-driven-development`.

## Cost Of Inline Mode

- Context accumulates across tasks. After ~3-4 tasks, the controller has to re-read
  earlier files and reviews to stay accurate.
- Self-review across tasks gets weaker — the same agent that wrote task N is now
  reviewing it. `spec-compliance-review` and `code-quality-review` remain mandatory,
  but their effectiveness depends on the main agent treating its own work skeptically.
- Worker / reviewer anti-pattern containment is weaker. Apply `receiving-review`
  strictly.

If any of these costs become a problem mid-plan, switch to
`subagent-driven-development` for the remaining tasks (the plan and acceptance
artifact already exist, so the switch is cheap).

## Preconditions

Same as `subagent-driven-development`:

- Acceptance artifact with acceptance criteria.
- Implementation plan with file responsibility mapping and Plan Self-Review completed.
- Core docs read.
- Conditional docs read when relevant.
- The next task is small enough to complete and verify in one pass.

## Workspace Isolation

Use `using-git-worktrees` to set up an isolated workspace, the same way
`subagent-driven-development` does. The cleanup ownership rules are identical.

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

Same as `subagent-driven-development`: do not pause between tasks. The user approved
the plan; execute it. Stop only on the Required User Checkpoints below.

## Required User Checkpoints

Same as `subagent-driven-development` — four conditions only:

1. **BLOCKED** that cannot be resolved with more context.
2. **Two-cycle review-fix without convergence** in the same task.
3. **Plan does not authorize this action.** Actions inside the plan's approved scope,
   files, dependencies, destructive operations, and review chain run without a
   checkpoint.
4. **High-Risk Surface** in the diff and `second-review` is not scheduled.

Items the plan already authorizes do NOT trigger a checkpoint.

## Inline-Mode Self-Review Discipline

Because the same agent wrote the code and is now reviewing it, apply these extra
guards:

- **Read the diff with fresh eyes**. `git diff` the changes; do not rely on memory of
  what you typed.
- **Re-read the acceptance criterion verbatim** for each criterion. Match each one to
  evidence (test, command output, observation).
- **Apply `verification-before-completion`** at every claim. "Tests pass" requires
  fresh test output read in this response.
- **Apply `receiving-review`** to your own review findings as if they came from a
  reviewer — verify before fixing, push back when wrong, apply one item at a time.
- **Re-check `using-bb-harness` Review Scope Guard** before declaring a finding. Is
  this finding inside the diff and the approved scope? If not, demote to Minor or note
  as out-of-scope.

## Switching To Subagent-Driven Mid-Plan

If inline mode becomes painful (context bloat, weakening review quality), switch:

1. Write a handoff in `docs/reviews/` summarizing completed tasks, decisions, open
   risks, and the next task.
2. Hand control to `subagent-driven-development` for the remaining tasks. The plan and
   acceptance artifact already capture the full work; the switch costs only one
   handoff write.

This is preferable to continuing inline when self-review is no longer trustworthy.

## Worker / Reviewer Anti-Patterns

Most of `subagent-driven-development`'s anti-patterns still apply. The ones unique to
inline mode:

- **Treating self-review as adequate without inline-mode discipline** above. Self
  review is not free in inline mode — it requires explicit re-reading.
- **Carrying assumptions from task N into task N+1**. Each task starts by re-reading
  its acceptance criteria, not by remembering them.
- **Mocking the review** ("I know this is fine"). Run the gate. Read the output.

## Output

After each task, report:

- Task completed.
- Files changed.
- Tests / checks run with fresh evidence.
- Reviews run (spec-compliance, code-quality, optional follow-on) with results.
- Docs updated or intentionally unchanged.
- Next task.

If switching to `subagent-driven-development`, report the switch reason and the
handoff path.
