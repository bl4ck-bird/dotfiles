---
name: subagent-driven-development
description: Use when executing an approved implementation plan task-by-task — dispatches a fresh implementer subagent per task, followed by two-stage review (spec-compliance then code-quality). Preferred default for multi-task work when the host supports subagents.
---

# Subagent-Driven Development

Execute an approved plan one task / vertical slice at a time using fresh subagents. Main agent is **controller**: never inherits worker context, never pauses unnecessarily, never delegates unresolved product / domain / architecture decisions.

Harness's preferred execution model. Use `executing-plans-inline` only when the host cannot dispatch subagents.

## Why Subagent-Driven

- **Fresh context per task** — no contamination, no token bloat.
- **Two-stage review separated from implementation** — reviewer sees diff, not implementer reasoning. Catches over-fitting and spec drift.
- **Continuous progress** — controller does not stop between tasks unless a required checkpoint applies.
- **Model selection per role** — cheap model for mechanical work, capable model for judgment.

## Preconditions

Confirm before editing:

- Current acceptance artifact with acceptance criteria (spec, PRD, issue, review finding, or approved task).
- Implementation plan with file responsibility mapping and Plan Self-Review done (see `write-plan` Self-Review).
- Core docs read: `AGENTS.md`, `CONTEXT.md`, `docs/CURRENT.md`, `docs/AGENT_WORKFLOW.md`, current artifact / plan, relevant code.
- Conditional docs read when relevant: `CONTEXT-MAP.md`, `docs/ARCHITECTURE.md`, `docs/DOMAIN_MODEL.md`, `docs/DATA_MODEL.md`, `docs/SECURITY_MODEL.md`, `docs/TESTING_STRATEGY.md`, durable decisions.
- Host can dispatch subagents. If not → `executing-plans-inline`.
- Next task small enough to complete and verify in one pass.

If any precondition missing, pause and fix the artifact first.

Use `bounded-loop` instead when the user wants autonomous iteration beyond the approved plan.

## Workspace Isolation

Use `using-git-worktrees` to set up isolation before the loop. That skill owns detection, creation priority (host-native first), `.gitignore` safety, baseline verification, cleanup ownership.

Plan-execution stop conditions:

- Baseline tests fail in fresh workspace → distinguish pre-existing from regression, ask before proceeding.
- No dependency installation without explicit user approval, even inside a fresh worktree (user-managed dependency rule).

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

**Do not pause between tasks.** User approved the plan; execute it. Progress summaries, "Should I continue?" prompts, and per-task confirmation waste time. Task → spec-compliance-review → code-quality-review → next task, uninterrupted.

Stop only on Required User Checkpoints.

## Required User Checkpoints

Stop and ask **only** when:

1. **BLOCKED** the controller cannot resolve (more context fails, stronger model fails, splitting fails → escalate).
2. **Two-cycle review-fix without convergence** in the same task. Apply `using-bb-harness` Review Iteration Pattern Hard Stop.
3. **Plan does not authorize this action.** The plan and acceptance artifact already authorize listed scope, files, dependencies, destructive operations (install / init / hooks / delete / commit / push / PR / history rewrite), and review chain. Stop only when the next action is **outside** plan coverage.
4. **High-Risk Surface** (see `second-review`) appears in the diff and `second-review` is not scheduled in the plan.

Plan-authorized items do NOT trigger checkpoints. Plan says "install lodash for Task 3" → `npm install lodash` during Task 3 is approved work. Plan says "delete legacy auth middleware in Task 5" → that delete is approved work.

Host tool permission prompts (e.g., Claude Code asking to allow a shell command) are not "user checkpoints" — host UI, no extra agent pause.

## Prompt Templates

Three subagent prompts in this directory:

- `implementer-prompt.md` — implementer subagent. Full task + scene + verification + return format + self-review.
- `spec-compliance-reviewer-prompt.md` — spec-compliance reviewer. "Do not trust the implementer's report. Read the code."
- `code-quality-reviewer-prompt.md` — code-quality reviewer. Five-area checklist (alignment / quality / architecture / testing / production readiness) with severity grading.

Use templates verbatim, substituting `{PLACEHOLDERS}`. No freehand prompts — consistency depends on templates.

## Dispatching An Implementer Subagent

Overview (full template in `implementer-prompt.md`):

- Full task text from plan (paste; do not make subagent re-read plan file).
- Scene-setting: where this task fits, dependencies, architectural constraints.
- Allowed files or modules. Forbidden files when relevant.
- Verification commands (test, type check, lint, build) and expected signals.
- Return format: status, files changed, verification evidence, self-review notes, open questions.
- Reminder: they are not alone in the codebase, must not revert other agents' work, own only the assigned files.
- TDD inside worker for behavior changes — failing test first, verify RED, implement, verify GREEN.

## Dispatching A Reviewer Subagent

Reviewers always run in fresh subagents — no inheritance of implementer framing.

- **`spec-compliance-review`**: pass acceptance artifact path, diff, implementer claim. Reviewer reads code, not report.
- **`code-quality-review`**: pass diff, plan task, acceptance artifact, relevant durable docs. Reviewer runs SSOT checks from `code-quality-review`.
- **`security-review`**: auto-triggered when diff touches security-sensitive surface (auth, secrets, crypto, deletion, untrusted input, sensitive data).
- **`second-review`**: auto-triggered for High-Risk Surfaces or when user requested independent double-check. Codex is default reviewer.

After reviewer returns findings, implementer subagent (not controller) applies fixes one item at a time per `receiving-review`. Controller re-dispatches reviewer on fixed diff.

## Model Selection

Least powerful model that handles the role.

| Task | Model |
| --- | --- |
| Mechanical (isolated function, clear spec, 1-2 files) | cheap / fast |
| Integration / judgment (multi-file, debugging) | standard |
| Architecture, design, review | most capable |

## Handling Implementer Status

- **DONE** → proceed to spec-compliance-review.
- **DONE_WITH_CONCERNS** → read concerns. Correctness / scope: address before review. Observations: note and proceed.
- **NEEDS_CONTEXT** → provide context, re-dispatch (same model).
- **BLOCKED** → assess:
  1. Context problem → more context, re-dispatch (same model).
  2. More reasoning needed → re-dispatch (stronger model).
  3. Task too large → split.
  4. Plan itself wrong → escalate.

Never ignore an escalation. Never retry same model unchanged. Stuck means something must change.

## Worker / Reviewer Anti-Patterns

Full catalog: `worker-anti-patterns.md` — controller-side, worker-side, reviewer-side, cross-cutting. Top hits: no parallel implementer for the same task, no skipping a review, no severity inflation, no auto-chained second follow-on, no silent scope expansion, no trust of worker reports without verification.

## Subagents For Independent Tracks

Outside the per-task loop, subagents are also used for:

- Bounded codebase investigation while main agent works elsewhere.
- Architecture, test, security, or docs deep-dive that `code-quality-review` did not cover.
- Requested independent `second-review`.

For **2+ genuinely independent investigations** that can run concurrently, use `dispatching-parallel-agents` — *parallel* and *read-only or disjoint*, distinct from this skill's *sequential* loop.

Bad subagent tasks:

- Vague "build the feature".
- Shared writes across same files without clear ownership.
- Work depending on unresolved product or domain decisions.
- Formatting or summarizing data already in controller's context.

## Handoff

Before clearing the session or pausing long work, write a handoff in `docs/reviews/` with:

- Current goal.
- Acceptance artifact and plan paths.
- Completed tasks.
- Changed files.
- Decisions made.
- Verification evidence.
- Open risks.
- Next task.

## Output

Per task, report:

- Task completed.
- Files changed.
- Tests / checks run with evidence.
- Reviews run (spec-compliance, code-quality, optional follow-on) with results.
- Docs updated or intentionally unchanged.
- Next task.

## When To Use `executing-plans-inline` Instead

Switch when:

- Host cannot dispatch subagents (no Task tool, no general-purpose agent type).
- Plan has 1-3 small tasks where dispatch overhead exceeds context-isolation benefit.
- User explicitly asked to keep execution in main session.

Same review gates apply; they run as skill invocations against the main agent's diff rather than as separate subagents.
