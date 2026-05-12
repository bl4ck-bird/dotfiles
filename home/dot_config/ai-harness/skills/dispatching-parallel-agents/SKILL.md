---
name: dispatching-parallel-agents
description: Use when 2+ genuinely independent investigations, bug repros, or read-only research tasks can run concurrently without shared state — for breadth, not for plan execution. Plan-task execution stays in subagent-driven-development.
---

# Dispatching Parallel Agents

Run multiple investigations or read-only tasks **concurrently** when they are
independent. Each agent gets its own context, scope, and return format. The controller
integrates the results.

This is **not** an alternative execution model for plan tasks — `subagent-driven-development`
already dispatches sequentially with two-stage review. Parallel dispatch is for the
*other* case: 2+ unrelated bugs to investigate, 2+ disjoint code areas to map, 2+
independent test failures with different root causes.

## When To Use

Trigger:

- 3+ test files failing with **different** root causes.
- Multiple subsystems broken **independently**.
- Each problem can be understood without context from the others.
- No shared state between investigations.
- Read-only research across distinct concerns ("how does X work?" + "where is Y called?"
  + "what does Z return?").

Do **not** use when:

- Failures are related — fixing one might fix the others.
- The investigation needs full system state held in one place.
- Agents would write to the same files (write conflicts).
- The task is part of a plan execution — that is `subagent-driven-development`.

## Use Case Boundary (vs Subagent-Driven-Development)

| Aspect | `dispatching-parallel-agents` | `subagent-driven-development` |
| --- | --- | --- |
| Purpose | Independent investigations / research | Sequential plan task implementation |
| Concurrency | Parallel (concurrent) | Sequential (one task at a time) |
| Write scope | Read-only or disjoint reads | Each task writes; never parallel writes |
| Review | Controller integrates, no formal review | Two-stage review per task |
| Triggered by | Multiple unrelated symptoms | Approved plan with tasks |

If you are unsure: most plan-execution work goes through `subagent-driven-development`.
Parallel dispatch is the *exception*, used when the controller needs concurrent
breadth, not depth.

## The Pattern

### 1. Identify Independent Domains

Group failures or questions by what they actually need to look at:

- File A tests: tool approval flow
- File B tests: batch completion behavior
- File C tests: abort functionality

Each domain is independent — fixing tool approval does not affect abort tests.

If you cannot articulate why two domains are *unrelated*, treat them as related and use
a single agent.

### 2. Craft Focused Agent Tasks

Each agent gets:

- **Specific scope**: one test file, one subsystem, one question.
- **Clear goal**: "Find the root cause of X" or "Map all call sites of Y".
- **Constraints**: do not change unrelated code; read-only by default unless the task
  permits writes within a disjoint scope.
- **Expected output**: structured summary the controller can integrate.

### 3. Dispatch Concurrently

In Claude Code, send multiple `Task` tool uses **in a single response**. They run in
parallel:

```text
Task("Investigate agent-tool-abort.test.ts failures")
Task("Investigate batch-completion-behavior.test.ts failures")
Task("Investigate tool-approval-race-conditions.test.ts failures")
```

In other harnesses, follow the platform's parallel dispatch idiom. If no parallel
dispatch exists, fall back to sequential dispatch — the *pattern* (one agent per
domain) still applies.

### 4. Integrate Results

When agents return:

1. Read each summary.
2. Verify findings do not conflict ("Agent A says X is broken, Agent B says X works" —
   resolve before acting).
3. Decide which findings need follow-up implementation (route through
   `subagent-driven-development` or `test-driven-development`).
4. Run a full verification after any integration step (apply
   `verification-before-completion`).

## Agent Prompt Structure

Each parallel agent prompt should be:

1. **Focused** — one clear problem domain.
2. **Self-contained** — all context needed to understand the problem (paste the failing
   test, the relevant file, the error message).
3. **Specific about output** — what should the agent return?

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

For each parallel agent, customize the prompt with that domain's specifics. Do not
send all three agents the same generic prompt and hope they figure it out.

## Output To Controller

After integration, report:

- Number of agents dispatched and their domains.
- Per-domain findings (one block per agent).
- Cross-cutting observations (if any domain affects another).
- Recommended next step:
  - Sequential fix via `subagent-driven-development` (multi-domain fixes).
  - Single-domain fix via `test-driven-development`.
  - Need additional investigation (some agent returned BLOCKED or NEEDS_CONTEXT).

## Anti-Patterns

- **Dispatching for plan execution**: parallel implementer subagents cause write
  conflicts. Plan tasks run sequentially via `subagent-driven-development`.
- **Vague agent prompts** ("look into the test failures"): each agent needs a specific
  domain and return format.
- **Letting agents share state**: each agent has its own context. Do not assume one
  agent saw what the other agent did.
- **Skipping integration step**: dispatching 3 agents and then trusting all three
  reports without cross-checking. Read each summary, verify no conflicts, then act.
- **Parallel writes**: if two agents touch the same files, the second overwrites the
  first. Either give each agent a disjoint write scope or make them all read-only.
- **Forgetting `verification-before-completion`**: agent reports are claims. If an
  agent says "I confirmed the bug", the controller still runs the repro itself before
  acting on the report.

## When Parallel Dispatch Is Not Worth It

The dispatch overhead is real (one Task tool call per agent, plus integration cost).
Stay single-agent when:

- 2 domains are small and one agent can hold both in context.
- The investigations share enough state that "saving context" is a wash.
- The controller already has the answer for 2 of 3 domains and only needs 1 agent.

## Failure Modes

- One agent returns BLOCKED: re-dispatch that one agent with more context. The other
  agents' results are still valid.
- Two agents disagree: read both summaries. Usually one is wrong about a fact that the
  other has correct. Resolve by re-checking the disputed fact yourself, not by
  re-dispatching.
- Agent returns nothing useful: prompt was too vague. Re-craft with a sharper scope
  and dispatch a single replacement (not all of them).

## Bottom Line

Parallel dispatch is a **breadth tool**, not an execution model. Use it when you have
3+ unrelated investigations and you want them done concurrently. Use
`subagent-driven-development` for everything that flows through an approved plan.
