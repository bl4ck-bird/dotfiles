# Worker / Reviewer Anti-Patterns

Load when:

- Dispatching implementer / reviewer subagents from `subagent-driven-development`
  and verifying the prompt avoids known failure modes.
- Diagnosing why a previous SDD loop produced surprising results — usually one of
  the patterns below was violated.

## Controller-Side (Plan Execution)

Never:

- **Start implementation on `main` / `master` without explicit user consent.**
  Use `using-git-worktrees` first. Acceptance artifact and plan stay on main;
  implementation lives in a worktree.
- **Dispatch multiple implementer subagents in parallel for the same task.**
  Write conflicts are guaranteed. Parallel dispatch is for *read-only / disjoint*
  work (`dispatching-parallel-agents`), not per-task implementation.
- **Make a worker read the plan file when you can paste the full task text.**
  Reading consumes context and risks reinterpretation. Paste the exact task text.
- **Skip a review pass to finish faster.** `spec-compliance-review` and
  `code-quality-review` catch different classes of finding.
- **Treat implementer self-review as `spec-compliance-review`.** Self-review
  catches obvious gaps before return; it does not replace independent review by a
  fresh subagent reading the diff without the implementer's framing.
- **Run `code-quality-review` before `spec-compliance-review` passes.** Order is
  fixed: compliance → quality → optional follow-on.
- **Move to the next task while either review has open Critical / Important
  findings.** Minor findings do not block.
- **Let a reviewer finding propose broad rewrites or new dependencies as
  required fixes.** See `using-bb-harness` Review Scope Guard. Out-of-scope
  improvements are Minor unless they are Critical defects in the touched path.
- **Delegate unresolved product / domain / architecture decisions to a worker.**
  Workers implement; controllers decide. Pause and escalate if uncovered.

## Worker-Side (Implementer Subagent)

The implementer prompt template (`implementer-prompt.md`) restates these in
worker-facing language.

- **Implementing outside the Allowed Files list.** Stop and report
  `DONE_WITH_CONCERNS` or `NEEDS_CONTEXT` — never silently expand scope.
- **Reverting another agent's work.** Own only assigned files; leave others'
  changes in place.
- **Running install / init / hook / delete / commit / push / destructive
  commands** unless the plan explicitly authorized them. These need user approval.
- **Skipping `verification-before-completion`** at RED, GREEN, or before
  reporting. The controller verifies independently, but the worker must not
  return false claims.
- **Reporting DONE when the work is partial.** Use `DONE_WITH_CONCERNS` for
  doubts, `BLOCKED` / `NEEDS_CONTEXT` when incomplete. Honest status is the
  contract.

## Reviewer-Side

The reviewer prompts (`spec-compliance-reviewer-prompt.md`,
`code-quality-reviewer-prompt.md`) inline the relevant rules.

- **Trusting the implementer's report instead of the diff.** Read the code.
  Reports are claims, not evidence.
- **Promoting Minor to Important / Critical to force a fix.** See
  `severity-definitions.md` Do Not Promote. List Minor as Minor.
- **Proposing broad rewrites, new dependencies, or unrelated cleanup as
  required fixes.** Scope Guard violation. Required fixes stay in the diff.
- **Re-running review without giving the implementer the previous findings.**
  Fix loop: review → `receiving-review` → implementer applies → reviewer re-runs.
- **Auto-chaining into a second follow-on review.** Review Chain Depth Cap = 1
  automatic. A second hop requires user confirmation.
- **Inventing facts the diff does not show.** "Might be slow", "could fail",
  "assumes" — without file:line or test output, these are speculative (Minor at
  best).

## Cross-Cutting

- **Skipping workspace isolation.** `using-git-worktrees` is the clean baseline.
- **Treating "host doesn't support subagents" as a reason to drop review gates.**
  Switch to `executing-plans-inline` — same gates, run inline. Reviews are
  non-negotiable; only dispatch mechanism changes.
- **Silently extending the plan mid-execution.** Discovered changes outside the
  File Responsibility Map → stop and escalate. No "fix it while I'm here".
- **Forgetting to apply `receiving-review` to reviewer feedback.** Reviewers can
  be wrong. Verify, push back if needed, apply one item at a time.

## Cross-Reference

- Scope creep in findings → `using-bb-harness/review-rules.md` Scope Guard.
- Severity inflation → `using-bb-harness/severity-definitions.md` Do Not Promote.
- Test-only methods, mocking-away-the-behavior, partial mocks →
  `test-driven-development/testing-anti-patterns.md`.
- Skipping verification → `verification-before-completion`.
- Worker/reviewer prompts inlining these rules → `implementer-prompt.md`,
  `spec-compliance-reviewer-prompt.md`, `code-quality-reviewer-prompt.md`.
