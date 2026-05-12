---
name: subagent-driven-development
description: Use when executing an approved implementation plan task-by-task — dispatches a fresh implementer subagent per task, followed by two-stage review (spec-compliance then code-quality). Preferred default for multi-task work when the host supports subagents.
---

# Subagent-Driven Development

Execute an approved plan one task / vertical slice at a time using fresh subagents for
each step. The main agent stays as **controller**: it never inherits worker context,
never pauses for unnecessary check-ins, and never delegates unresolved product / domain /
architecture decisions.

This is the harness's preferred execution model. Use `executing-plans-inline` only when
the host environment cannot reliably dispatch subagents.

## Why Subagent-Driven

Each subagent dispatch gives:

- **Fresh context per task** — no contamination from earlier work, no token bloat from
  unrelated prior tasks.
- **Two-stage review separated from implementation** — the reviewer sees the diff, not
  the implementer's reasoning. This catches over-fitting and spec drift.
- **Continuous progress** — the controller does not stop between tasks unless a
  required user checkpoint applies.
- **Model selection per role** — implementer can run on a cheap fast model when the
  task is mechanical; reviewer can run on a capable model when judgment matters.

## Preconditions

Before editing, confirm:

- There is a current acceptance artifact with acceptance criteria: spec, PRD, issue,
  review finding, or approved task.
- There is an implementation plan with file responsibility mapping and Plan Self-Review
  completed (see `write-plan` Self-Review).
- Core docs read: `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`,
  `docs/AGENT_WORKFLOW.md`, the current acceptance artifact / plan, and relevant code.
- Conditional docs read only when relevant: `CONTEXT-MAP.md`, `docs/ARCHITECTURE.md`,
  `docs/DOMAIN_MODEL.md`, `docs/DATA_MODEL.md`, `docs/SECURITY_MODEL.md`,
  `docs/TESTING_STRATEGY.md`, durable decisions.
- The host environment can dispatch subagents. If not, use `executing-plans-inline`
  instead.
- The next task is small enough to complete and verify in one pass.

If any precondition is missing, pause and create or update the missing artifact first.

Use `bounded-loop` instead of this skill when the user asks the agent to continue
autonomously toward a goal across repeated iterations beyond the approved plan.

## Workspace Isolation

Use `using-git-worktrees` to set up an isolated workspace before starting the loop.
That skill owns detection, creation priority (host-native first), `.gitignore` safety,
baseline verification, and cleanup ownership rules.

Stop conditions specific to plan execution:

- If baseline tests fail in the fresh workspace, distinguish pre-existing failures from
  regressions caused by worktree creation and ask before proceeding.
- Do not run dependency installation without explicit user approval, even inside a
  fresh worktree (user-managed dependency rule).

## Execution Loop

```text
Read plan once → extract all tasks with full text and context → create task list.

For each task in order:

  1. Dispatch implementer subagent (fresh context, no chat history).
     Pass: full task text, scene-setting context, allowed files, verification commands,
     return format. Worker uses test-driven-development for behavior changes.
     Use the implementer-prompt.md template in this directory.

  2. Implementer reports: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED.
     Apply verification-before-completion — inspect the actual diff and run the
     implementer's claimed verification yourself. Worker reports are claims, not
     evidence.

  3. Dispatch spec-compliance-review subagent on the resulting diff.
     Use the spec-compliance-reviewer-prompt.md template in this directory.
     - ✅ Spec compliant → step 4.
     - ❌ Issues found → implementer fixes the listed items (via receiving-review),
       re-run step 3.
     - Stop after two cycles in the same task. Escalate to user.

  4. Dispatch code-quality-review subagent on the resulting diff.
     Use the code-quality-reviewer-prompt.md template in this directory.
     - Ready to merge: Yes → step 5.
     - Ready to merge: With fixes → implementer applies Critical/Important findings
       (via receiving-review), re-run step 4.
     - Ready to merge: No → plan or acceptance needs revision. Escalate to user.
     - Stop after two cycles in the same task. Escalate to user.

  5. If code-quality-review recommended a follow-on (security-review or
     second-review), run it now. At most one automatic follow-on per task — additional
     follow-ons require user confirmation (Review Chain Depth Cap in using-bb-harness).

  6. Mark task complete. Update plan checklist and any changed docs.

  7. Record residual risk and verification evidence.

  8. If the plan uses per-slice commits, run ship-check before the commit gate.

  9. Continue to the next task without pausing for confirmation — the user approved the
     plan, so execute it. Stop only on BLOCKED, two-cycle review escalation, or a
     boundary listed in "Required User Checkpoints" below.
```

## Continuous Execution

**Do not pause to check in with the user between tasks.** The user approved the plan;
execute it. Progress summaries, "Should I continue?" prompts, and per-task confirmation
requests waste time. Run task → spec-compliance-review → code-quality-review → next task,
without interruption.

Stop only on the Required User Checkpoints below.

## Required User Checkpoints

Stop and ask the user **only** when:

1. **BLOCKED** that the controller cannot resolve with more context or a more capable
   model. (Worker reports BLOCKED, retry with more context fails, retry with a stronger
   model fails, splitting the task fails — escalate.)
2. **Two-cycle review-fix without convergence** in the same task. Apply
   `using-bb-harness` Review Iteration Pattern Hard Stop.
3. **Plan does not authorize this action.** The plan and acceptance artifact already
   authorize their listed scope, files, dependencies, destructive operations
   (install / init / hooks / delete / commit / push / PR / history rewrite), and review
   chain. Stop only when the next required action is **outside** what the plan already
   covered.
4. **High-Risk Surface** (see `second-review`) appears in the diff and `second-review`
   is not scheduled in the plan.

Items the plan already authorizes do NOT trigger a checkpoint. If the plan says
"install lodash for Task 3", running `npm install lodash` during Task 3 is approved
work, not a destructive surprise. If the plan says "delete the legacy auth middleware
in Task 5", that delete is approved work.

Tool permission prompts from the host (e.g., Claude Code asking the user to allow a
specific shell command) are not "user checkpoints" — those are the host's own UI and
do not require an extra agent pause.

## Prompt Templates

Three subagent prompt templates live in this directory:

- `implementer-prompt.md` — for the implementer subagent. Full task text + scene
  context + verification + return format + self-review prompt.
- `spec-compliance-reviewer-prompt.md` — for the spec-compliance reviewer. "Do not
  trust the implementer's report. Read the code."
- `code-quality-reviewer-prompt.md` — for the code-quality reviewer. Five-area
  checklist (alignment / quality / architecture / testing / production readiness)
  with severity grading.

Use the templates verbatim, substituting `{PLACEHOLDERS}`. Do not synthesize prompts
freehand — consistency across tasks depends on the templates.

## Dispatching An Implementer Subagent

Brief overview (full template in `implementer-prompt.md`):

- Full task text from the plan (paste it; do not make the subagent re-read the plan
  file).
- Scene-setting context: where this task fits, dependencies, architectural
  constraints.
- Allowed files or modules. Forbidden files when relevant.
- Verification commands (test command, type check, lint, build) and expected signals.
- Return format: status, files changed, verification evidence, self-review notes,
  unresolved questions.
- A reminder that they are not alone in the codebase, must not revert other agents'
  work, and own only the assigned files.
- TDD inside the worker for behavior changes — failing test first, verify RED, then
  implement, then verify GREEN.

## Dispatching A Reviewer Subagent

Reviewers always run in fresh subagents so they do not inherit the implementer's
framing.

- **`spec-compliance-review`**: pass the acceptance artifact path, the diff, and the
  implementer's claim. Reviewer reads the code, not the report.
- **`code-quality-review`**: pass the diff, plan task, acceptance artifact, and
  relevant durable docs. Reviewer runs the SSOT checks defined in
  `code-quality-review`.
- **`security-review`**: triggered automatically when the diff touches a
  security-sensitive surface (auth, secrets, crypto, deletion, untrusted input,
  sensitive data).
- **`second-review`**: triggered automatically for High-Risk Surfaces or when the user
  requested an independent double-check. Codex is the default reviewer.

After a reviewer returns findings, the implementer subagent (not the controller)
applies fixes one item at a time per `receiving-review`. The controller dispatches the
reviewer again on the fixed diff.

## Model Selection

Use the least powerful model that can handle each role to conserve cost and time.

- **Mechanical implementation** (isolated function, clear spec, 1-2 files): fast / cheap
  model.
- **Integration / judgment** (multi-file coordination, debugging): standard model.
- **Architecture, design, review**: most capable available model.

Task complexity signals:

- 1-2 files, complete spec → cheap.
- Multi-file integration concerns → standard.
- Design judgment or broad codebase understanding → most capable.

## Handling Implementer Status

- **DONE** → proceed to spec-compliance-review.
- **DONE_WITH_CONCERNS** → read the concerns. Correctness / scope concerns: address
  before review. Observations only: note and proceed.
- **NEEDS_CONTEXT** → provide the missing context and re-dispatch with the same model.
- **BLOCKED** → assess the blocker:
  1. Context problem → provide more context, re-dispatch (same model).
  2. Requires more reasoning → re-dispatch with a more capable model.
  3. Task too large → split into smaller pieces.
  4. Plan itself is wrong → escalate to the user.

Never ignore an escalation or force the same model to retry without changes. If the
implementer said it's stuck, something needs to change.

## Worker / Reviewer Anti-Patterns

Never:

- Start implementation on `main` / `master` without explicit user consent.
- Dispatch multiple implementer subagents in parallel for the same task (write
  conflicts).
- Make a worker read the plan file when you can paste the full task text.
- Skip a review pass to finish faster.
- Treat implementer self-review as the same thing as `spec-compliance-review`.
- Run `code-quality-review` before `spec-compliance-review` passes.
- Move to the next task while either review has open Critical / Important findings.
- Let a reviewer finding propose broad rewrites or new dependencies as required fixes
  (see `using-bb-harness` Review Scope Guard).
- Delegate unresolved product / domain / architecture decisions to a worker.

## Subagents For Independent Tracks

Outside the per-task loop, subagents are also used for:

- Investigating a bounded codebase question while the main agent works elsewhere.
- Running an architecture, test, security, or docs deep-dive that
  `code-quality-review` did not need to cover.
- A requested independent `second-review`.

Bad subagent tasks:

- A vague "build the feature" assignment.
- Shared writes across the same files without clear ownership.
- Work that depends on unresolved product or domain decisions.
- Formatting or summarizing data already available in the controller's context.

## Handoff

Before clearing the session or pausing long work, write a handoff in `docs/reviews/`
with:

- Current goal.
- Acceptance artifact and plan paths.
- Completed tasks.
- Changed files.
- Decisions made.
- Verification evidence.
- Open risks.
- Next task.

## Output

After each task, report:

- Task completed.
- Files changed.
- Tests / checks run with evidence.
- Reviews run (spec-compliance, code-quality, optional follow-on) with results.
- Docs updated or intentionally unchanged.
- Next task.

## When To Use `executing-plans-inline` Instead

Switch to `executing-plans-inline` when:

- The host environment cannot dispatch subagents (no Task tool, no general-purpose
  agent type).
- The plan has 1-3 small tasks where the subagent dispatch overhead exceeds the
  context-isolation benefit.
- The user explicitly asked to keep execution in the main session.

In those cases the same review gates apply, but they run as skill invocations against
the main agent's diff rather than as separate subagents.
