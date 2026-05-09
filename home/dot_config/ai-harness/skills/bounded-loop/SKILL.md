---
name: bounded-loop
description: Use when the user wants an agent to keep working toward a defined goal across multiple iterations with review checkpoints.
---

# Bounded Loop

Run an agentic loop only after the goal, scope, limits, and stop conditions are explicit.

## Preconditions

Before starting the loop, confirm:

- Goal: the concrete outcome to reach.
- Scope: files, modules, docs, or commands the loop may touch.
- Iteration budget: maximum loop count or time budget.
- Verification gate: commands or manual checks that prove progress.
- Review gate: when to run self-review, subagent review, or independent Codex review.
- Allowed autonomous actions: exact file areas, commands, review/fix scope, and whether worker agents may be used.
- Forbidden actions: setup, dependency, hook, git history, deletion, deployment, or other actions that still require a user checkpoint.
- Stop conditions: success, repeated failure, scope expansion, risky command, unclear product decision, or user checkpoint.
- Handoff target: where to record state if the session is cleared or paused.

If any precondition is missing, ask for it or create a short proposal for approval before continuing.

## Loop Shape

For each iteration:

1. State the current goal, iteration number, allowed scope, allowed autonomous actions, and planned action.
2. Make the smallest useful change or investigation.
3. Run the verification gate or explain why it cannot run.
4. Run the relevant focused review when the change is risky, broad, or repeated.
5. Decide: continue, stop successful, stop blocked, or ask the user.
6. Update the plan, review record, or handoff note with evidence.

Do not continue just because budget remains. Continue only when the next iteration has a clear expected improvement.

The loop may proceed without per-iteration approval only inside the approved goal, scope, allowed actions, iteration budget, and stop conditions. Tool permission prompts, destructive operations, and unapproved product or architecture choices are not covered by loop approval.

## Required User Checkpoints

Ask before continuing when:

- The next step expands scope beyond the approved files or goal.
- Verification fails twice for the same reason.
- A design decision changes product, domain, architecture, data, security, or dependency direction.
- The loop would install packages, initialize git, add hooks, rewrite history, delete files, or run destructive commands.
- The loop would use a command, file area, external service, or worker-agent write scope that was not included in allowed autonomous actions.
- The loop reaches the iteration budget without meeting the goal.

## Good Uses

- Fix all findings from an approved review within a bounded file set.
- Continue implementing an approved plan slice until the slice passes its checks.
- Iterate on docs until `docs-review` finds no material drift.
- Investigate a failing test with a maximum number of hypotheses.

## Bad Uses

- Brainstorming/product discovery or deciding product direction.
- Broad refactors without a reviewed plan.
- Running indefinitely until "everything is better".
- Replacing user approval for irreversible setup, dependency, or history decisions.

## Output

End with:

- final state: complete, blocked, or stopped for approval
- iterations used
- files changed or inspected
- verification evidence
- review evidence
- remaining risk
- next safe action
