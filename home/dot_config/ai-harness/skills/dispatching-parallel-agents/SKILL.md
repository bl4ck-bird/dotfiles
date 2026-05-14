---
name: dispatching-parallel-agents
description: Use when 2+ genuinely independent investigations, bug repros, or read-only research tasks can run concurrently without shared state — for breadth, not for plan execution. Plan-task execution stays in subagent-driven-development.
---

# Dispatching Parallel Agents

Run multiple investigations / read-only tasks **concurrently** when independent. Each agent gets own context, scope, return format. Controller integrates.

**Not** an alternative execution model for plan tasks — `subagent-driven-development` dispatches sequentially with two-stage review. Parallel dispatch handles the *other* case: 2+ unrelated bugs, 2+ disjoint code areas, 2+ independent test failures with different root causes.

## When To Use

Trigger:

- 3+ test files failing with **different** root causes.
- Multiple subsystems broken **independently**.
- Each problem understandable without context from others.
- No shared state between investigations.
- Read-only research across distinct concerns.

Do **not** use when:

- Failures related — fixing one might fix others.
- Investigation needs full system state in one place.
- Agents would write to same files (conflicts).
- Task is plan execution — that's `subagent-driven-development`.

## Use Case Boundary (vs Subagent-Driven-Development)

| Aspect | `dispatching-parallel-agents` | `subagent-driven-development` |
| --- | --- | --- |
| Purpose | Independent investigations / research | Sequential plan task implementation |
| Concurrency | Parallel (concurrent) | Sequential (one task at a time) |
| Write scope | Read-only or disjoint reads | Each task writes; never parallel writes |
| Review | Controller integrates, no formal review | Two-stage review per task |
| Triggered by | Multiple unrelated symptoms | Approved plan with tasks |

Unsure? Most plan-execution work → `subagent-driven-development`. Parallel dispatch is the *exception* when controller needs concurrent breadth, not depth.

## The Pattern

### 1. Identify Independent Domains

Group failures/questions by what they need to look at. Example:

- File A tests: tool approval flow
- File B tests: batch completion behavior
- File C tests: abort functionality

Each independent — fixing tool approval does not affect abort tests.

Cannot articulate why two domains are *unrelated*? Treat as related, use one agent.

### 2. Craft Focused Agent Tasks

Each agent gets:

- **Specific scope**: one test file, one subsystem, one question.
- **Clear goal**: "Find root cause of X" or "Map all call sites of Y".
- **Constraints**: do not change unrelated code; read-only by default unless task permits writes within disjoint scope.
- **Expected output**: structured summary the controller can integrate.

### 3. Dispatch Concurrently

Claude Code: send multiple `Task` tool uses **in a single response**:

```text
Task("Investigate agent-tool-abort.test.ts failures")
Task("Investigate batch-completion-behavior.test.ts failures")
Task("Investigate tool-approval-race-conditions.test.ts failures")
```

Other harnesses (Codex, Gemini, generic CLI): follow the platform's parallel dispatch idiom if one exists; otherwise dispatch sequentially (one investigator at a time, same prompt structure) and merge results in the same order. The investigation-per-domain pattern still applies — only the concurrency mechanism changes.

### 4. Integrate Results

When agents return:

1. Read each summary.
2. Verify findings do not conflict — resolve before acting.
3. Decide which findings need follow-up (route through `subagent-driven-development` or `test-driven-development`).
4. Run full verification after integration (`verification-before-completion`).

## Agent Prompt Structure

Each prompt: **focused** (one domain), **self-contained** (paste failing test, relevant file, error), **specific about output**.

Template:

```text
Task tool (general-purpose):
  description: "Investigate <domain>"
  prompt: |
    Investigate <specific problem> in <specific files>.

    ## Context

    {Background, related code, what is already known}

    ## What To Find

    1. Root cause (file:line, mechanism).
    2. Reproduction (smallest failing input or test).
    3. Affected scope (which other tests / call sites depend on this).
    4. Hypothesis for the fix (do NOT apply it — return the analysis).

    ## Constraints

    - Do NOT modify code. This is investigation only.
    - Stay inside: <file list>. Do not read outside this scope unless you can justify
      a single specific reason.
    - Apply verification-before-completion when running any repro command — read the
      output in your response.

    ## Return Format

    - Root cause: <one paragraph>
    - Repro: <command or test snippet>
    - Affected scope: <list>
    - Suggested fix: <one paragraph>
    - Files inspected: <list>
```

Customize per domain. Do not send all agents the same generic prompt.

## Output To Controller

After integration:

- Number of agents dispatched and domains.
- Per-domain findings (one block per agent).
- Cross-cutting observations.
- Recommended next step: sequential fix via `subagent-driven-development` / single-domain fix via `test-driven-development` / additional investigation (BLOCKED or NEEDS_CONTEXT).

## Anti-Patterns

- **Dispatching for plan execution**: parallel implementers cause write conflicts. Plan tasks run sequentially via `subagent-driven-development`.
- **Vague prompts** ("look into the test failures"): each agent needs specific domain and return format.
- **Letting agents share state**: each has own context. Don't assume one saw what another did.
- **Skipping integration**: dispatching 3 agents, trusting all reports without cross-checking. Read each, verify no conflicts, act.
- **Parallel writes**: two agents on same files → second overwrites first. Disjoint write scope or all read-only.
- **Forgetting `verification-before-completion`**: reports are claims. Controller runs repro itself before acting.

## When Parallel Dispatch Is Not Worth It

Dispatch overhead is real. Stay single-agent when:

- 2 domains small, one agent holds both.
- Investigations share enough state that "saving context" is a wash.
- Controller already has answer for 2 of 3 domains.

## Failure Modes

- One agent BLOCKED: re-dispatch with more context. Others still valid.
- Two agents disagree: read both. Usually one wrong about a fact other has right. Re-check disputed fact yourself, not re-dispatch.
- Agent returns nothing useful: prompt too vague. Re-craft with sharper scope, dispatch single replacement (not all).

## Bottom Line

Breadth tool, not execution model. Use for 3+ unrelated investigations concurrently. Use `subagent-driven-development` for everything flowing through an approved plan.
