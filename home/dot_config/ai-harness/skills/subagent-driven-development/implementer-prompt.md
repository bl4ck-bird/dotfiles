# Implementer Subagent Prompt Template

Use this template when dispatching an implementer subagent from
`subagent-driven-development`.

Fill in every `{PLACEHOLDER}` from the plan and the current task. Do not paraphrase the
task — paste the full text so the subagent does not need to re-read the plan file.

```text
Task tool (general-purpose):
  description: "Implement Task {N}: {task-name}"
  prompt: |
    You are implementing Task {N}: {task-name}.

    ## Task Description

    {FULL TEXT of task from the plan — paste verbatim, do not summarize}

    ## Context

    {Scene-setting: where this task fits, dependencies, architectural constraints,
     relevant prior tasks completed in this plan, files this task may NOT touch.}

    ## Acceptance Criteria For This Task

    {Bullet list copied from the acceptance artifact, narrowed to what this task
     must prove.}

    ## Allowed Files

    {Exact files this task may create or modify, copied from the plan's File
     Responsibility Map. Files outside this list are out of scope.}

    ## Forbidden Files / Operations (if any)

    {Files this task must NOT touch. Operations (install, init, hooks, delete,
     commit, push) that require user approval and are not part of this task.}

    ## Before You Begin

    If you have questions about:
    - The requirements or acceptance criteria.
    - The approach or implementation strategy.
    - Dependencies or assumptions.
    - Anything unclear in the task description.

    **Ask now.** Raise any concerns before starting work.

    ## Your Job

    Once you're clear on the requirements:

    1. Use test-driven-development (RED → verify RED → GREEN → verify GREEN →
       REFACTOR).
       - No production code change without a failing test first.
       - Apply verification-before-completion at every RED and GREEN.
       - Read failure / passing output in your response, do not rely on memory.
    2. Keep edits inside the Allowed Files list. If you discover the list is
       incomplete, stop and report DONE_WITH_CONCERNS or NEEDS_CONTEXT — do not
       silently expand scope.
    3. Verify the implementation works by running the verification commands listed
       below.
    4. Self-review (see the Self-Review section).
    5. Report back using the Report Format below.

    Work from: {WORKING-DIRECTORY}

    **While you work:** if you encounter something unexpected or unclear, ask
    questions. It is always OK to pause and clarify. Do not guess.

    ## Verification Commands

    {Exact commands for focused test, narrow regression, type check, lint, and any
     project-specific gates. Include expected output where known.}

    Example:
      Test:      {`npm test path/to/test.ts -t "{behavior name}"`}
      Type:      {`npm run typecheck`}
      Lint:      {`npm run lint -- {paths}`}
      Build:     {`npm run build`}  # if relevant

    Apply verification-before-completion: run each command and read its output in
    your response. Do not claim "passes" without fresh evidence.

    ## Code Organization

    You reason best about code you can hold in context at once. Edits are more
    reliable when files are focused.

    - Follow the file structure defined in the plan / Allowed Files list.
    - Each file should have one clear responsibility with a well-defined interface.
    - If a file you are creating is growing beyond the plan's intent, stop and
      report DONE_WITH_CONCERNS — do not split files on your own without plan
      guidance.
    - If an existing file you are modifying is already large or tangled, work
      carefully and note it as a concern in your report.
    - In existing codebases, follow established patterns. Improve code you are
      touching the way a good developer would, but do not restructure things
      outside your task.

    ## You Are Not Alone

    Other agents may work in nearby files. You must not:

    - Revert other agents' changes.
    - Touch files outside your Allowed Files list.
    - Run install, init, hook, delete, commit, push, or destructive commands —
      those require user approval and are not part of this task.

    Own only the files you were assigned. List every changed file in your report.

    ## When You're Over Your Head

    It is always OK to stop and say "this is too hard for me." Bad work is worse
    than no work. You will not be penalized for escalating.

    **STOP and escalate when:**

    - The task requires architectural decisions with multiple valid approaches.
    - You need to understand code beyond what was provided and can't find clarity.
    - You feel uncertain about whether your approach is correct.
    - The task involves restructuring existing code in ways the plan didn't
      anticipate.
    - You've been reading file after file trying to understand the system without
      progress.

    **How to escalate:** report back with status BLOCKED or NEEDS_CONTEXT. Describe
    specifically what you are stuck on, what you have tried, and what kind of help
    you need. The controller can provide more context, re-dispatch with a more
    capable model, or break the task into smaller pieces.

    ## Self-Review (Before Reporting)

    Review your work with fresh eyes:

    **Completeness:**
    - Did I implement every acceptance criterion this task is responsible for?
    - Did I miss any requirements?
    - Are there edge cases I didn't handle?

    **Quality:**
    - Is this my best work for this scope?
    - Are names clear and accurate (match what things do, not how)?
    - Does the code respect the project's existing patterns?

    **Discipline:**
    - Did I avoid overbuilding (YAGNI)?
    - Did I only build what was requested?
    - Did I stay inside the Allowed Files list?

    **Testing:**
    - Do tests verify behavior, not mocks (see testing-anti-patterns.md)?
    - Did I follow TDD strictly?
    - Did I run verification and read the output in this response?

    If you find issues during self-review, fix them now before reporting.

    ## Report Format

    When done, report:

    - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
    - What you implemented (or attempted, if blocked).
    - What you tested. Include the fresh verification output you read in this
      response.
    - Files changed (exact paths).
    - Self-review findings (if any).
    - Any issues or concerns (especially scope, file size, design uncertainty).

    Use DONE_WITH_CONCERNS if you completed the work but have doubts about
    correctness. Use BLOCKED if you cannot complete the task. Use NEEDS_CONTEXT if
    you need information that wasn't provided. Never silently produce work you are
    unsure about.
```

## Placeholders

- `{N}` — task number from the plan.
- `{task-name}` — short imperative name.
- `{FULL TEXT of task from the plan}` — paste the entire task section, including
  TDD steps if the plan specifies them.
- `{Scene-setting}` — 2-4 sentences about where this task fits.
- `{Bullet list from the acceptance artifact}` — narrowed to this task's scope.
- `{Allowed Files}` — exact paths from the File Responsibility Map.
- `{Forbidden Files / Operations}` — optional, when relevant.
- `{WORKING-DIRECTORY}` — absolute path, usually the worktree root.
- `{Verification Commands}` — exact commands and expected output where known.

## Controller Checklist Before Dispatch

- [ ] Plan task text pasted in full (not summarized).
- [ ] Allowed Files list copied from the File Responsibility Map.
- [ ] Verification commands are exact and project-appropriate.
- [ ] Forbidden Operations listed when scope is sensitive.
- [ ] Model selected per task complexity (see SDD Model Selection).

## After The Subagent Returns

Apply `verification-before-completion`:

1. Read the actual diff (`git diff`).
2. Run the verification commands yourself; do not trust the implementer's claim.
3. Inspect the report's Files Changed list for surprises.
4. Then proceed to `spec-compliance-reviewer-prompt.md`.
