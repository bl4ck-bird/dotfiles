# Worker / Reviewer Anti-Patterns

Load this reference when:

- Dispatching implementer or reviewer subagents from `subagent-driven-development`
  and verifying the prompt does not slip into a known failure mode.
- Reviewing why a previous SDD loop produced surprising results — usually one of
  the patterns below was violated.

## Controller-Side Anti-Patterns (Plan Execution)

Never:

- **Start implementation on `main` / `master` without explicit user consent.** Use
  `using-git-worktrees` to set up an isolated workspace first. The acceptance
  artifact and plan stay in the main branch; implementation lives in a worktree.
- **Dispatch multiple implementer subagents in parallel for the same task.** Write
  conflicts are guaranteed: each subagent runs in its own context but writes to the
  shared file tree. Parallel dispatch is for *read-only / disjoint* work
  (`dispatching-parallel-agents`), not for the per-task implementation loop.
- **Make a worker read the plan file when you can paste the full task text.**
  Reading the file consumes the worker's context window and risks misalignment if
  the worker re-interprets the plan differently. Paste the exact task text from the
  plan into the implementer prompt.
- **Skip a review pass to finish faster.** Both `spec-compliance-review` and
  `code-quality-review` exist because they catch different classes of finding. The
  cost saved by skipping is paid back with interest in the next slice when the bug
  propagates.
- **Treat implementer self-review as the same thing as `spec-compliance-review`.**
  Self-review lives in the implementer prompt for catching obvious gaps before
  return. It does not replace the independent review by a fresh subagent that
  reads the diff without inheriting the implementer's framing.
- **Run `code-quality-review` before `spec-compliance-review` passes.** Quality
  review on non-compliant code wastes the reviewer's findings on code that will
  change anyway. The order is fixed: compliance → quality → optional follow-on.
- **Move to the next task while either review has open Critical / Important
  findings.** Critical / Important findings block the task. Minor findings do not
  block.
- **Let a reviewer finding propose broad rewrites or new dependencies as
  required fixes.** See `using-bb-harness` Review Scope Guard. Out-of-scope
  improvements are Minor unless they are Critical defects in the touched path.
- **Delegate unresolved product / domain / architecture decisions to a worker.**
  Workers implement; controllers decide. If the plan does not cover the decision,
  pause and escalate to the user.

## Worker-Side Anti-Patterns (Implementer Subagent)

The implementer subagent must avoid these. The implementer prompt template
(`implementer-prompt.md`) restates them in worker-facing language.

- **Implementing outside the Allowed Files list.** If the task needs a file not
  listed, stop and report `DONE_WITH_CONCERNS` or `NEEDS_CONTEXT` — do not
  silently expand scope.
- **Reverting another agent's work.** The worker owns only its assigned files. Any
  encountered changes to other files are someone else's work; leave them in place.
- **Running install / init / hook / delete / commit / push / destructive commands**
  unless the plan explicitly authorized them. These require user approval.
- **Skipping `verification-before-completion`** at RED, GREEN, or before reporting
  status. Worker reports are claims; the controller verifies independently
  regardless, but the worker should not return a false claim in the first place.
- **Reporting DONE when the work is partial.** Use `DONE_WITH_CONCERNS` if the
  work completed but has known doubts. Use `BLOCKED` or `NEEDS_CONTEXT` when the
  work could not complete. Honesty about status is part of the contract.

## Reviewer-Side Anti-Patterns

Each reviewer subagent must avoid these. The reviewer prompts
(`spec-compliance-reviewer-prompt.md`, `code-quality-reviewer-prompt.md`) inline
the relevant ones.

- **Trusting the implementer's report instead of the diff.** The first rule of
  every reviewer: read the code. Reports are claims, not evidence.
- **Promoting Minor findings to Important / Critical to force a fix.** See
  `severity-definitions.md` Do Not Promote rule. If you want it fixed but it is
  genuinely Minor, list it as Minor — the implementer may apply it at their
  discretion.
- **Proposing broad rewrites, new dependencies, or unrelated cleanup as required
  fixes.** Scope Guard violation. Required fixes stay within the diff.
- **Re-running review without giving the implementer the previous findings to
  apply.** The fix loop is: review returns findings → `receiving-review` →
  implementer applies → reviewer re-runs. Skipping `receiving-review` causes the
  same findings to be re-flagged.
- **Auto-chaining into a second follow-on review.** Review Chain Depth Cap = 1
  automatic follow-on. A second hop requires user confirmation.
- **Inventing facts the diff does not show.** "This might be slow", "this could
  fail", "this assumes" — without a file:line in the diff or test output, these
  are speculative and belong in Minor at best.

## Cross-Cutting Anti-Patterns

- **Skipping the workspace isolation step.** `using-git-worktrees` is the entry
  to a clean baseline. Skipping it means polluting the user's main tree.
- **Treating "host doesn't support subagents" as a reason to drop the review
  gates.** Switch to `executing-plans-inline` — same review gates, run inline. The
  reviews are non-negotiable; only the dispatch mechanism is.
- **Silently extending the plan mid-execution.** If the implementer discovers a
  needed change outside the plan's File Responsibility Map, stop and escalate to
  the user. Do not "fix it while I'm here".
- **Forgetting to apply `receiving-review` to reviewer feedback.** Reviewers can
  be wrong. Verify, push back if needed, apply one item at a time.

## Cross-Reference

Anti-patterns that touch a specific concern have their full treatment elsewhere:

- Scope creep in findings → `using-bb-harness/review-rules.md` Scope Guard.
- Severity inflation → `using-bb-harness/severity-definitions.md` Do Not Promote.
- Test-only methods, mocking-away-the-behavior, partial mocks →
  `test-driven-development/testing-anti-patterns.md`.
- Skipping verification → `verification-before-completion`.
- Worker/reviewer prompts that already inline the relevant rules →
  `implementer-prompt.md`, `spec-compliance-reviewer-prompt.md`,
  `code-quality-reviewer-prompt.md`.
