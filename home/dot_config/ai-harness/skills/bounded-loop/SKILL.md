---
name: bounded-loop
description: Use when the user wants an agent to keep working toward a defined goal across multiple iterations with review checkpoints.
---

# Bounded Loop

Run an agentic loop only after goal, scope, limits, and stop conditions are explicit.

## Preconditions

Confirm before starting:

- Goal: concrete outcome.
- Scope: files, modules, docs, commands the loop may touch.
- Iteration budget: max loop count or time budget.
- Verification gate: commands/manual checks that prove progress.
- Review gate: when to run self-review, subagent review, or independent Codex review.
- Allowed autonomous actions: exact file areas, commands, review/fix scope, whether worker
  agents may be used.
- Forbidden actions: setup, dependency, hook, git history, deletion, deployment — anything
  still requiring a user checkpoint.
- Stop conditions: success, repeated failure, scope expansion, risky command, unclear product
  decision, user checkpoint.
- Handoff target: where to record state if session is cleared/paused.

Missing precondition → ask or create a short proposal for approval before continuing.

## Loop Shape

Each iteration:

1. State goal, iteration number, allowed scope, allowed actions, planned action.
2. Make smallest useful change or investigation.
3. Run verification gate or explain why it cannot. Apply `verification-before-completion` —
   fresh output read in this response, not a remembered prior run.
4. Run focused review when change is risky, broad, or repeated.
5. Decide: continue, stop successful, stop blocked, or ask the user.
6. Update plan, review record, or handoff note with evidence.

Continue only when next iteration has a clear expected improvement.

Loop proceeds without per-iteration approval **only inside** approved goal, scope, actions,
budget, stop conditions. Tool permission prompts, destructive operations, unapproved
product/architecture choices are **not** covered by loop approval.

## Required User Checkpoints

Ask before continuing when:

- Next step expands scope beyond approved files or goal.
- Verification fails twice for same reason.
- Design decision changes product, domain, architecture, data, security, or dependency
  direction.
- Loop would install packages, init git, add hooks, rewrite history, delete files, or run
  destructive commands.
- Loop would use a command, file area, external service, or worker-agent write scope not in
  allowed actions.
- Loop reaches iteration budget without meeting goal.

## Good Uses

- Fix all findings from an approved review within a bounded file set.
- Continue implementing an approved plan slice until it passes checks.
- Iterate on docs until `code-quality-review` (durable docs drift) finds no material drift, or
  until `docs-sync` confirms alignment.
- Investigate a failing test with max number of hypotheses.

## Bad Uses

- Brainstorming/product discovery or deciding product direction.
- Broad refactors without a reviewed plan.
- Running indefinitely until "everything is better".
- Replacing user approval for irreversible setup, dependency, or history decisions.

## Output

- final state: complete, blocked, or stopped for approval
- iterations used
- files changed or inspected
- verification evidence
- review evidence
- remaining risk
- next safe action
