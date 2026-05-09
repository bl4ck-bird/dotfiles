---
name: agentic-execution
description: Use when executing an approved implementation plan with multiple tasks, vertical slices, subagents, or review checkpoints.
---

# Agentic Execution

Execute an approved plan one vertical slice at a time with review checkpoints and durable handoff notes.

## Preconditions

Before editing, confirm:

- There is a current spec or issue with acceptance criteria.
- There is an implementation plan with file responsibility mapping.
- Core docs were read: `AGENTS.md`, `CONTEXT.md`, `docs/AGENT_WORKFLOW.md`, the current spec/plan, and relevant code.
- Conditional docs were read only when relevant: `CONTEXT-MAP.md`, `docs/ARCHITECTURE.md`, `docs/DOMAIN_MODEL.md`, `docs/DATA_MODEL.md`, `docs/SECURITY_MODEL.md`, `docs/TESTING_STRATEGY.md`, and ADRs.
- The next task is small enough to complete and verify in one pass.

If any precondition is missing, pause execution and create or update the missing artifact first.

Use `bounded-goal-loop` instead of this skill when the user asks the agent to continue autonomously toward a goal across repeated iterations. Do not run open-ended loops from `agentic-execution`.

## Execution Loop

For each task or slice:

1. State the slice goal and files likely to change.
2. Use `tdd-workflow` for behavior changes.
3. Keep edits scoped to the slice. Do not opportunistically refactor unrelated code.
4. Run the narrowest meaningful verification for the slice.
5. Update the plan checklist and any changed docs.
6. Run `review-gate` when the slice changes architecture, domain behavior, tests, security-sensitive code, or more than a few files.
7. Record residual risk before moving to the next slice.

Stop and ask before expanding scope beyond the approved plan, changing product/domain/architecture decisions, installing dependencies, adding hooks, initializing git, deleting files, or rewriting history.

## Worker Execution

Use the main agent as the controller. Use a worker agent only when the task can be executed from durable artifacts rather than hidden chat context.

When using Codex, Claude, or another agent as a coding worker:

- Give the worker the exact spec, plan task, allowed files or modules, relevant docs to read, constraints, verification commands, and return format.
- Assign one vertical slice or one disjoint write scope. Do not ask a worker to "build the feature" broadly.
- Ask for behavior tests through public interfaces or user-visible flows when behavior changes.
- Require the worker to list changed files, verification evidence, unresolved questions, and residual risk.
- Keep the worker context fresh: pass artifact paths and essential decisions, not the full primary chat.

After a worker returns, the controller must inspect the diff and run two review passes before moving to the next worker task:

1. Spec compliance: does the result match the accepted spec, plan task, and acceptance criteria?
2. Code quality: are tests, maintainability, DDD/SOLID fit, file responsibility, and safety acceptable?

Use `review-gate`, reviewer subagents, or an independent Codex review for these passes when risk justifies it. Fix or explicitly accept findings before marking the task complete.

## Subagents

Use subagents when tasks are independent and have disjoint write scopes.

Scope in the main agent first. Do not delegate before the plan, files, ownership, and return format are clear.

Good subagent tasks:

- Implement a single vertical slice with explicit files or module ownership.
- Review a plan, diff, test suite, security surface, or docs.
- Investigate a bounded codebase question while the main agent works elsewhere.

Bad subagent tasks:

- A vague "build the feature" assignment.
- Shared writes across the same files without clear ownership.
- Work that depends on unresolved product or domain decisions.
- Formatting or summarizing data already available in the main-agent context.

For exploratory repo analysis, prefer a batch of two or more independent concerns when practical. A single focused reviewer subagent is acceptable for architecture, test, docs, security, or requested second-review gates.

When dispatching workers, tell them:

- They are not alone in the codebase.
- They must not revert others' changes.
- They own only the assigned files or responsibility.
- They must list changed files and verification in the final report.

## Review Checkpoints

Use two review levels for substantial work:

- First review: self-review or reviewer subagent against the spec and plan.
- Second review: independent Codex review when available for risky specs, plans, large diffs, architecture changes, or security-sensitive work.

A slice is not complete until review findings are either fixed or explicitly accepted with a reason.

## Handoff

Before clearing the session or pausing long work, write a handoff in `docs/reviews/` with:

- Current goal
- Spec and plan paths
- Completed slices
- Changed files
- Decisions made
- Verification evidence
- Open risks
- Next action

## Output

After each slice, report:

- Slice completed
- Files changed
- Tests/checks run
- Reviews run
- Docs updated or intentionally unchanged
- Next slice
